from utils.log_helper import setup_logger
from .worker_template import AioredisWorker
from .message_proto_handler import MessageProtoHandler
from .settings import ROUNDTRIP_CHANNEL
from aioredis import Redis


class DbAccessWorker(MessageProtoHandler):

    redis_pub: Redis

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = setup_logger(__name__)

    async def process_msg_inbound(self, chann_name, msg_raw):
        await super().process_msg_inbound(chann_name, msg_raw)  # AioredisWorker
        msg_result = await self.process_message(msg_raw)  # MessageProtoHandler
        for msg in msg_result:
            await self.redis_pub.publish_json(ROUNDTRIP_CHANNEL, msg)
