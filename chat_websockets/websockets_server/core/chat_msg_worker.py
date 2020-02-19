from utils.log_helper import setup_logger
from .worker_template import AioredisWorker
from .settings import ROUNDTRIP_CHANNEL
import json
from aioredis import Redis


class DbAccessWorker(AioredisWorker):

    redis_pub: Redis
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = setup_logger(__name__)

    async def process_msg_inbound(self, chann_name, msg_raw):
        await super().process_msg_inbound(chann_name, msg_raw)
        await self.redis_pub.publish(ROUNDTRIP_CHANNEL, msg_raw)
