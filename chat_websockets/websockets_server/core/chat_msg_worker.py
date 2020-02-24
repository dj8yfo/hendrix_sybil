from utils.log_helper import setup_logger
from .message_proto_handler import MessageProtoHandler
from aioredis import Redis
import os

# it's permissible here, as the message processing pipeline is sequential
# no context switch occurs until a message's processing and its django orm operations are finished
# and the pipeline continues to next message queued in redis channel
# this depends on subscring to only one channel:
# channels_handlers = [(self.sub_topic, self.process_msg_inbound)] in AioredisWorker
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"


class DbAccessWorker(MessageProtoHandler):

    redis_pub: Redis

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = setup_logger(__name__)

    async def process_msg_inbound(self, chann_name, msg_raw):
        await super().process_msg_inbound(chann_name, msg_raw)  # AioredisWorker
        msg_result = await self.process_message(msg_raw)  # MessageProtoHandler
        for msg, channel in msg_result:
            self.logger.debug('[%s] publiishing message: [%s]', channel, msg)
            await self.redis_pub.publish_json(channel, msg)
