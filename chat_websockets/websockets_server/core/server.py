import json
from aiohttp import web, WSCloseCode
from typing import Dict
from websockets_server.core import views, settings
from websockets_server.core.template_routine import TmpltRedisRoutines
from utils.log_helper import setup_logger
from aioredis import Redis


class HXApplication(web.Application, TmpltRedisRoutines):

    REQ_MSG_KEYS = ['action']
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
        self.rooms = {}
        self.logger = setup_logger(__name__)

        self.on_startup.append(self._setup)
        self.on_shutdown.append(self._on_shutdown_handler)

    @staticmethod
    def extract_websockets_id(request):
        return request.headers.get('X-Forwarded-For', None) or\
            request.remote

    async def _setup(self, app):
        self.logger.info('HXApplication: attaching websocket view')
        self.router.add_get('/ws', views.WebSocketView)
        redis_addr = (settings.REDIS_HOST, settings.REDIS_PORT)
        channels_handlers = [(settings.ROUNDTRIP_CHANNEL, self.process_msg_inbound)]
        await self.init_redis_tasks(redis_addr, channels_handlers)

    async def _on_shutdown_handler(self, app):
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
            'message_tuples': [],   # list of tuples of format (type_char, msg_id)
            'identity_name': 'unauthenticated',
            'room': None
        }
        self.logger.info('[%s] websocket was added to websocket list', ws_id)

    def handle_ws_disconnect(self, ws_id):
        self.websockets.pop(ws_id, None)
        self.logger.debug('[%s] websocket was removed from websocket list', ws_id)

    async def process_msg_inbound(self, chann_name, raw_msg):
        self.logger.debug('receieved message on [%s]: [%s]', chann_name, raw_msg)
        msg = json.loads(raw_msg)
        ws_id = msg['ws_id']
        ws = self.websockets[ws_id]['ws']
        await ws.send_str(json.dumps(msg['msg']))

    async def process_msg_outbound(self, msg_raw, ws_id):
        # preliminary validation
        try:
            msg = json.loads(msg_raw)
        except json.JSONDecodeError as jse:
            raise ValueError('invalid json encoding of incoming message') from jse
        if not all(msg.get(key) for key in self.REQ_MSG_KEYS):
            raise ValueError(f'not all keys present in incoming message: {msg} |' +
                             f'{self.REQ_MSG_KEYS}')
        pub_topic = settings.WORKER_TOPIC
        types = list(map(lambda x: x[0], self.websockets[ws_id]['message_tuples']))
        data_out = {}
        data_out['message_types'] = types
        data_out['ws_id'] = ws_id
        data_out['msg'] = msg
        self.logger.debug('[%s] publish message [%s] to topic [%s]', ws_id,
                          data_out, pub_topic)
        await self.redis_pub.publish_json(pub_topic, data_out)
