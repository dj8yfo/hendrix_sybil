import random
import json
import asyncio
from aiohttp import web, WSCloseCode
from typing import Dict
from websockets_server.core import views, settings
from websockets_server.core.template_routine import TmpltRedisRoutines
from websockets_server.core.message_proto_handler import MessageProtoHandler
from utils.log_helper import setup_logger
from aioredis import Redis


nyms = []
with open("nyms", "r") as nyms_file:
    for line in nyms_file:
        nyms.append(line.rstrip())


class HXApplicationState(object):

    accept = True

    def __init__(self, logger):
        self.logger = logger
        self.websockets = {}
        self.rooms = {}  # dict: room -> set(ws_id~s)

    def store_new_connection(self, ws_id, ws):
        if self.accept:
            self.websockets[ws_id] = {
                "ws": ws,
                "message_types": [],  # list of (type_char)
                "identity_nym": None,
                "room": None,
                # mutex: one message at a time from a connection until
                # successfull response
                "processing_blocked": False,
                "closed": False,
            }
            self.logger.info("[%s] websocket was added to websocket store", ws_id)

    def __iter__(self):
        return iter(self.websockets)

    def __getitem__(self, key):
        return self.websockets[key]

    class WebsocketsInfo(object):
        class ProxyToDict(object):
            def __init__(self, dikt, field):
                self.dikt = dikt
                self.field = field

            def __getitem__(self, key):
                return self.dikt[key][self.field]

            def __setitem__(self, key, value):
                self.dikt[key][self.field] = value

        def __init__(self, field):
            self.field = field

        def __get__(self, obj, objtype):
            if obj is None:
                raise ValueError("not expecting to use descriptor on class")
            return self.ProxyToDict(obj.websockets, self.field)

    conn = WebsocketsInfo("ws")  # websocket connections accessor
    msg_types = WebsocketsInfo("message_types")
    identities = WebsocketsInfo("identity_nym")
    closed = WebsocketsInfo("closed")

    @staticmethod
    def extract_websockets_id(request, ws):
        prefix = request.headers.get("X-Forwarded-For", None) or request.remote
        return str(prefix) + ":" + str(id(ws))
        # return str(prefix)

    async def close_connection(
        self, ws_id, code=WSCloseCode.POLICY_VIOLATION, message="replacing_conn"
    ):
        if ws_id in self.websockets:
            info = self.websockets.pop(ws_id)
            stored_ws = info["ws"]
            nym_freed = info["identity_nym"]
            room_left = info["room"]

            if room_left is not None:
                self.rooms[room_left].remove(ws_id)
                if len(self.rooms[room_left]) == 0:
                    self.rooms.pop(room_left)
                else:
                    content = f"[{nym_freed}] has left {room_left}"
                    announce, _ = MessageProtoHandler.send_message_layout(
                        content, room_left, from_nym="hendrix"
                    )
                    await self.redis_pub.publish_json(
                        settings.ROUNDTRIP_CHANNEL, announce
                    )

            if nym_freed is not None:
                self.logger.info("[%s] freeing a nym", nym_freed)
                await self.redis_pub.sadd(
                    settings.NYMS_KEY, nym_freed.encode(encoding="utf-8")
                )
            await stored_ws.close(code=code, message=message)

            self.logger.info(
                "[%s] websocket was removed from websocket store and closed", ws_id
            )
        else:
            self.logger.warn("an attempt to close an already closed conn: [%s]", ws_id)

    def join_room(self, ws_id, prev_room, room):
        if prev_room is not None:
            self.rooms[prev_room].remove(ws_id)
            if len(self.rooms[prev_room]) == 0:
                self.rooms.pop(prev_room)

        if room in self.rooms:
            pass
        else:
            self.rooms[room] = set()
        self.rooms[room].add(ws_id)
        self.websockets[ws_id]["room"] = room

    async def drop_all_connections(self):
        self.accept = False
        all_keys = list(iter(self))
        for ws_id in all_keys:
            await self.close_connection(
                ws_id, code=WSCloseCode.GOING_AWAY, message="servo_shutdown"
            )

    def aquire_lock(self, ws_id):
        if self.websockets[ws_id]["processing_blocked"]:
            raise RuntimeError(
                "silentily dropping a new message"
                f" on a user channel, blocked by another message: {ws_id}"
            )
        else:
            self.websockets[ws_id]["processing_blocked"] = True

    def release_lock(self, ws_id):
        self.websockets[ws_id]["processing_blocked"] = False

    async def send_message(self, ws_id, msg, convert=True):
        if convert:
            json_msg = json.dumps(msg)
        else:
            json_msg = msg
        ws = self.conn[ws_id]
        self.logger.debug("sending ws message on [%s]: [%s]", ws_id, msg)
        await ws.send_str(json_msg)

    async def broadcast_message(self, msg, *recepients):
        json_msg = json.dumps(msg)
        self.logger.debug("broadcast list: [%s]", recepients)
        coros = map(
            lambda recepient: self.send_message(recepient, json_msg, convert=False),
            recepients,
        )
        await asyncio.gather(*coros, return_exceptions=True)


class HXApplication(web.Application, TmpltRedisRoutines):

    message_actions = {
        "authenticate": {"handler": "handle_authenticate"},  # 'handle_%s'
        "close": {"handler": "handle_close"},
        "select_room": {"handler": "handle_select_room"},
        "send_message": {"handler": "handle_send_message"},
        "history_retrieve": {"handler": "handle_history_retrieve"},
    }
    redis_pub: Redis
    redis_sub: Dict[str, Redis]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tasks = []

        self.logger = setup_logger(__name__)

        # the fact, that the connection state resides in the process memory
        # implies usage of [--workers 1] parameter of gunicorn or running
        # without gunicorn altogether )
        # if one intends to use many workers,
        # the global game (room, connection, id) state has to  be shared between workers
        # via redis e.g., that's more complex structure for this simple application
        #
        # at current state the total set of available nyms is shared via redis
        # by this web.Application and its worker processes
        self.state = HXApplicationState(self.logger)

        self.on_startup.append(self._setup)
        self.on_shutdown.append(self._on_shutdown_handler)

    @staticmethod
    def extract_websockets_id(request, ws):
        return HXApplicationState.extract_websockets_id(request, ws)

    async def _setup(self, app):
        self.logger.info("HXApplication: attaching websocket view")
        self.logger.info("available nyms: %s", nyms)
        self.router.add_get("/ws", views.WebSocketView)
        self.router.add_static("/static", "./ui/")
        redis_addr = (settings.REDIS_HOST, settings.REDIS_PORT)
        channels_handlers = [(settings.ROUNDTRIP_CHANNEL, self.process_msg_inbound)]
        channels_handlers += [(settings.HENDRIX_CHANNEL, self.process_msg_admin)]
        await self.init_redis_tasks(redis_addr, channels_handlers)
        self.state.redis_pub = self.redis_pub
        for nym in nyms:
            await self.redis_pub.sadd(settings.NYMS_KEY, nym.encode(encoding="utf-8"))

    async def _on_shutdown_handler(self, app):
        await self.state.drop_all_connections()
        rem_nyms = await self.redis_pub.spop(settings.NYMS_KEY, len(nyms))
        self.logger.info("removed nyms: %s", rem_nyms)
        await self.shutdown_templ()

    # async def channel_subscribe(self, chann_name, msg_handler) - inherited

    async def handle_ws_connect(self, ws_id, ws):
        await self.state.close_connection(ws_id)

        self.state.store_new_connection(ws_id, ws)

    async def handle_ws_disconnect(self, ws_id, code, message):
        await self.state.close_connection(ws_id, code=code, message=message)

    async def process_msg_inbound(self, chann_name, raw_msg):
        self.logger.debug("receieved message on [%s]: [%s]", chann_name, raw_msg)
        msg = json.loads(raw_msg)
        ws_id = msg.pop("ws_id")

        if ws_id in self.state:
            self.state.release_lock(ws_id)
            if msg["status"] == MessageProtoHandler.SUCCESS:
                action = msg["msg"]["action"]
                self.state.msg_types[ws_id].append(action)

                handler = self.message_actions[action]["handler"]
                meth = getattr(self, handler)
                await meth(msg, ws_id)

            await self.state.send_message(ws_id, msg)
            if self.state.closed[ws_id]:
                await self.state.close_connection(
                    ws_id, code=views.good_exit_code, message=views.good_exit_message
                )
        elif ws_id == "broadcast":
            if msg["status"] == MessageProtoHandler.SUCCESS:
                action = msg["msg"]["action"]
                handler = self.message_actions[action]["handler"]
                meth = getattr(self, handler)
                await meth(msg, ws_id)
        else:
            self.logger.warn("connection [%s] already not present", ws_id)

    async def handle_authenticate(self, msg, ws_id):
        self.state.identities[ws_id] = msg["msg"]["from_nym"]

    async def handle_close(self, msg, ws_id):
        self.state.closed[ws_id] = True

    async def handle_select_room(self, msg, ws_id):
        self.state.join_room(
            ws_id, prev_room=msg["msg"]["prev_room"], room=msg["msg"]["room"]
        )

    async def handle_send_message(self, msg, ws_id):
        room = msg["msg"]["room"]
        recipients = set(self.state.rooms[room])
        if ws_id in recipients:
            recipients.remove(ws_id)
        await self.state.broadcast_message(msg, *recipients)

    async def handle_history_retrieve(self, msg, ws_id):
        pass

    async def process_msg_admin(self, chann_name, raw_msg):
        self.logger.debug("receieved message on [%s]: [%s]", chann_name, raw_msg)
        msg = json.loads(raw_msg)
        ws_id = msg.pop("ws_id")
        message_content = msg["msg"]["content"]
        if ws_id in self.state:
            found_room = self.state.websockets[ws_id]["room"]
            payload, _ = MessageProtoHandler.send_message_layout(
                message_content, found_room, "hendrix", ws_id=None
            )
            await self.state.send_message(ws_id, payload)
        else:
            self.logger.warn("connection [%s] already not present", ws_id)

    async def process_msg_outbound(self, msg_raw, ws_id):
        # preliminary validation
        msg = MessageProtoHandler.validate_raw_input(msg_raw)

        self.state.aquire_lock(ws_id)

        pub_topic = random.choice(settings.WORKER_TOPIC)
        dikt = self.state[ws_id]
        data_out = MessageProtoHandler.pack_input(msg, ws_id, **dikt)

        self.logger.debug(
            "[%s] publish message [%s] to topic [%s]", ws_id, data_out, pub_topic
        )
        await self.redis_pub.publish_json(pub_topic, data_out)
