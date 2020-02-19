import asyncio


async def shutdown(application):
    for task in application.tasks:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            application.logger.info("an expected cancellation of task: %s",
                                    task.get_name())

    for redis_conn in [application.redis_sub, application.redis_pub]:
        if redis_conn and not application.redis_sub.closed:
            redis_conn.close()
            await redis_conn.wait_closed()
