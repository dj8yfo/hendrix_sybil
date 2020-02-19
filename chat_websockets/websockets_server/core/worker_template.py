from utils.log_helper import setup_logger
from .template_routine import TmpltRedisRoutines
from . import template_routine
import asyncio
import signal
# import os

class AioredisWorker(TmpltRedisRoutines):

    def __init__(self, host, port, sub_topic, loop=None, **kwargs):
        self.logger = setup_logger(__name__)
        self.loop = loop or asyncio.get_event_loop()
        self.host = host
        self.port = port
        self.sub_topic = sub_topic
        self.tasks = []
        for signum in [signal.SIGTERM, signal.SIGINT]:
            self.loop.add_signal_handler(signum, self.shutdown)

    def shutdown(self):
        self.logger.info('shutdown initiated. unsubscribing from all channels')
        task = self.loop.create_task(self.shutdown_templ())

        def artificial(*args, **kwargs):
            self.loop.stop()
        task.add_done_callback(artificial)

    # async def channel_subscribe(self, chann_name, msg_handler) - inherited

    async def process_msg_inbound(self, chann_name, msg_raw):
        self.logger.debug('[%s]: [%s]', chann_name, msg_raw)

    async def _run(self):
        redis_addr = (self.host, self.port)
        channels_handlers = [(self.sub_topic, self.process_msg_inbound)]
        await self.init_redis_tasks(redis_addr, channels_handlers)

    def run(self):
        # print(f"I'm {os.getpid()}, hello!")
        self.loop.create_task(self._run())
        try:
            self.loop.run_forever()
        finally:
            self.loop.close()
        self.logger.info('AioredisWorker succesfully run')
