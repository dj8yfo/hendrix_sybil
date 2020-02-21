import random
import json
from aiohttp import web, WSCloseCode
from typing import Dict
from websockets_server.core import views, settings
from websockets_server.core.template_routine import TmpltRedisRoutines
from websockets_server.core.message_proto_handler import MessageProtoHandler
from utils.log_helper import setup_logger
from aioredis import Redis


nyms = []
with open('nyms', 'r') as nyms_file:
    for line in nyms_file:
        nyms.append(line.rstrip())


class HXApplication(web.Application, TmpltRedisRoutines):

    message_actions = {
        'authenticate': {
            'handler': 'handle_authenticate'
        },
        'close': {
            'handler': 'handle_close',
        },
        'select_room': {
            'handler': 'handle_select_room',
        },
        'send_message': {
            'handler': 'handle_send_message',
        },
        'history_retrieve': {
            'handler': 'handle_history_retrieve',
        }

    }
    redis_pub: Redis
    redis_sub: Dict[str, Redis]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tasks = []

        # the fact, that the connection state in the process memory implies usage
        # of [--workers 1] parameter of gunicorn; if one intends to use many workers,
        # the global game (room, connection, id) state has to  be shared between workers
        # via redis e.g., that's a more complex structure
        self.websockets = {}
        self.rooms = {}  # dict: room -> set(nyms)
        self.logger = setup_logger(__name__)

        self.on_startup.append(self._setup)
        self.on_shutdown.append(self._on_shutdown_handler)

    @staticmethod
    def extract_websockets_id(request, ws):
        prefix = request.headers.get('X-Forwarded-For', None) or\
            request.remote
        return str(prefix) + ':' + str(id(ws))
        # return str(prefix)

    async def _setup(self, app):
        self.logger.info('HXApplication: attaching websocket view')
        self.logger.info('available nyms: %s', nyms)
        self.router.add_get('/ws', views.WebSocketView)
        redis_addr = (settings.REDIS_HOST, settings.REDIS_PORT)
        channels_handlers = [(settings.ROUNDTRIP_CHANNEL, self.process_msg_inbound)]
        channels_handlers += [(settings.HENDRIX_CHANNEL, self.process_msg_admin)]
        await self.init_redis_tasks(redis_addr, channels_handlers)
        for nym in nyms:
            await self.redis_pub.sadd(settings.NYMS_KEY, nym.encode(encoding='utf-8'))

    async def _on_shutdown_handler(self, app):
        rem_nyms = await self.redis_pub.spop(settings.NYMS_KEY, len(nyms))
        self.logger.info('removed nyms: %s', rem_nyms)
        await self.shutdown_templ()

        for ws_id in self.websockets.keys():
            ws = self.websockets[ws_id]['ws']
            await ws.close(code=WSCloseCode.GOING_AWAY, message='servo_shutdown')

    # async def channel_subscribe(self, chann_name, msg_handler) - inherited

    async def handle_ws_connect(self, ws_id, ws):
        if ws_id in self.websockets:
            stored_ws = self.websockets[ws_id]['ws']
            await stored_ws.close(code=WSCloseCode.GOING_AWAY,
                                  message='replacing_conn')
            self.logger.info('[%s] websocket was removed from websocket list and closed',
                             ws_id)

        self.websockets[ws_id] = {
            'ws': ws,
            'message_types': [],   # list of (type_char)
            'identity_nym': None,
            'room': None,
            # mutex: one message at a time from a connection until successfull response
            'processing_blocked': False
        }
        self.logger.info('[%s] websocket was added to websocket list', ws_id)

    async def handle_ws_disconnect(self, ws_id):
        # await self.redis_pub.sadd(settings.NYMS_KEY, ws_id_associated_nym)
        self.websockets.pop(ws_id, None)
        self.logger.debug('[%s] websocket was removed from websocket list', ws_id)

    async def process_msg_inbound(self, chann_name, raw_msg):
        self.logger.debug('receieved message on [%s]: [%s]', chann_name, raw_msg)
        msg = json.loads(raw_msg)
        ws_id = msg.pop('ws_id')

        if ws_id in self.websockets.keys():
            self.websockets[ws_id]['processing_blocked'] = False
            if msg['status'] == MessageProtoHandler.SUCCESS:
                self.websockets[ws_id]['message_types'].append(msg['msg']['action'])
                payload = msg['msg']
                action = payload['action']
                handler = self.message_actions[action]['handler']
                meth = getattr(self, handler)
                await meth(payload, ws_id)

            ws = self.websockets[ws_id]['ws']
            self.logger.debug('sending ws message on [%s]: [%s]', ws_id, msg)
            await ws.send_str(json.dumps(msg))
        else:
            self.logger.warn('connection [%s] already not present', ws_id)

    async def handle_authenticate(self, msg, ws_id):
        self.websockets[ws_id]['identity_nym'] = msg['from_nym']

    async def handle_select_room(self, msg, ws_id):
        pass

    async def handle_send_message(self, msg, ws_id):
        pass

    async def process_msg_admin(self, chann_name, raw_msg):
        self.logger.debug('receieved message on [%s]: [%s]', chann_name, raw_msg)
        msg = json.loads(raw_msg)

        ws_id = msg['ws_id']
        message_content = msg['message']
        if ws_id in self.websockets.keys():
            ws = self.websockets[ws_id]['ws']
            payload = {
                'action': 'message',
                'room': 'get_the_room_of_ws_id',
                'text': message_content
            }
            await ws.send_str(json.dumps(payload))
        else:
            self.logger.warn('connection [%s] already not present', ws_id)

    async def process_msg_outbound(self, msg_raw, ws_id):
        # preliminary validation
        msg = MessageProtoHandler.validate_raw_input(msg_raw)

        if self.websockets[ws_id]['processing_blocked']:
            raise RuntimeError('silentily dropping a new message'
                               f' on a user channel, blocked by another message: {ws_id}')
        else:
            self.websockets[ws_id]['processing_blocked'] = True

        pub_topic = random.choice(settings.WORKER_TOPIC)
        types = self.websockets[ws_id]['message_types']
        from_nym = self.websockets[ws_id]['identity_nym']
        room = self.websockets[ws_id]['room']
        data_out = MessageProtoHandler.pack_input(msg, types, ws_id, from_nym, room)

        self.logger.debug('[%s] publish message [%s] to topic [%s]', ws_id,
                          data_out, pub_topic)
        await self.redis_pub.publish_json(pub_topic, data_out)
