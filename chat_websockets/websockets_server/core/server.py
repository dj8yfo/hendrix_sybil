import asyncio
import json
import aioredis
from aiohttp import web, WSCloseCode
from websockets_server.core import views, settings
from websockets_server.core import shutdown, subscribe
from utils.log_helper import setup_logger
from aioredis import Redis


class HXApplication(web.Application):

    REQ_MSG_KEYS = ['action']
    redis_pub: Redis
    redis_sub: Redis

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tasks = []
        self.websockets = {}
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
        for attr in ('redis_sub', 'redis_pub'):
            setattr(self, attr, await aioredis.create_redis(redis_addr,
                                                            loop=self.loop))

        listen_channel = self.channel_subscribe(settings.ROUNDTRIP_CHANNEL)
        self.tasks.append(self.loop.create_task(listen_channel,
                                                name='redis_roundrip_chan'))

    async def _on_shutdown_handler(self, app):
        await shutdown.shutdown(self)

        for ws_id in self.websockets.keys():
            ws = self.websockets[ws_id]['ws']
            await ws.close(code=WSCloseCode.GOING_AWAY, message='servo_shutdown')

    async def channel_subscribe(self, chann_name):
        await subscribe.subscribe(self, chann_name, self.process_msg_inbound)

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

    def process_msg_inbound(self, chann_name, raw_msg):
        self.logger.debug('receieved message on %s: %s', chann_name, raw_msg)

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
