import asyncio
import aioredis
import traceback


class TmpltRedisRoutines(object):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def channel_subscribe(self, chann_name, msg_handler):
        self.logger.info('HXApplication: subscribing to channel %s', chann_name)
        try:
            self.logger.debug("redis_sub.subscribe: %s",
                              self.redis_sub[chann_name].subscribe)
            channel, *_ = await self.redis_sub[chann_name].subscribe(chann_name)

            while await channel.wait_message():
                try:
                    msg_raw = await channel.get()
                    await msg_handler(chann_name, msg_raw)
                except (ValueError, Exception) as e:
                    self.logger.error('[%s] exception while processing inbound redis msg',
                                      e)

                    self.logger.error('\n%s', traceback.format_exc())

        except asyncio.CancelledError:
            self.logger.error('CancelledError exception received.'
                              'unsibscribing from %s', chann_name)
            await self.redis_sub[chann_name].unsubscribe(chann_name)

    async def shutdown_templ(self):
        for task in self.tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                self.logger.info("an expected cancellation of task: %s",
                                 task.get_name())

        conns = [self.redis_pub] + [v for _, v in self.redis_sub.items()]
        self.logger.info('redis connection: [%s]', conns)
        for redis_conn in conns:
            if redis_conn and not redis_conn.closed:
                redis_conn.close()
                self.logger.info('closing redis connection: [%s]', redis_conn)
                await redis_conn.wait_closed()

    async def init_redis_tasks(self, redis_addr, sub_channels):
        self.logger.info('redis connection at %s. subscribed to: %s.', redis_addr,
                         sub_channels)
        self.redis_pub = await aioredis.create_redis(redis_addr,
                                                     loop=self.loop)
        self.redis_sub = {}
        for channel, handler in sub_channels:
            self.redis_sub[channel] = await aioredis.create_redis(redis_addr,
                                                                  loop=self.loop)

            listen_channel = self.channel_subscribe(channel, handler)
            routine_name = f'redis_{channel}_chan'
            self.tasks.append(self.loop.create_task(listen_channel,
                                                    name=routine_name))
