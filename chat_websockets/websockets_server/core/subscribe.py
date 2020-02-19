import asyncio


async def subscribe(application, chann_name, msg_handler=print):
    application.logger.info('HXApplication: subscribing to channel %s', chann_name)
    try:
        application.logger.debug("redis_sub.subscribe: %s", application.redis_sub.subscribe)
        channel, *_ = await application.redis_sub.subscribe(chann_name)

        while await channel.wait_message():
            try:
                msg_raw = await channel.get()
                msg_handler(chann_name, msg_raw)
            except (ValueError, Exception) as e:
                application.logger.error('[%s] exception while processing inbound redis msg',
                                         e)

    except asyncio.CancelledError:
        application.logger.error('CancelledError exception received.'
                                 'unsibscribing from %s', chann_name)
        await application.redis_sub.unsubscribe(chann_name)
