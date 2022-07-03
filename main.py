import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger

from components.redis import register_redis
from components.requests import close_requests, register_requests
from script.checkin_daily import checkin_daily
from script.refresh_clash_config import refresh_clash_config
from script.refresh_clash_subscription import refresh_clash_subscription


class InterceptHandler(logging.Handler):
    """Intercepts builtin logging messages and routes them to Loguru"""

    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1
        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


# Enable interceptor
logging.basicConfig(handlers=[InterceptHandler()], level=0)

if __name__ == "__main__":
    logger.add("default.log", rotation="200KB", compression="zip", level="INFO")
    logger.add("error.log", rotation="200KB", compression="zip", level="ERROR")

    loop = asyncio.get_event_loop()
    loop.run_until_complete(register_redis())
    loop.run_until_complete(register_requests())

    scheduler = AsyncIOScheduler()
    scheduler.add_job(checkin_daily, "cron", hour=0, minute=10)
    scheduler.add_job(refresh_clash_config, "interval", days=15)
    scheduler.add_job(refresh_clash_subscription, "interval", minutes=10)
    scheduler.start()

    try:
        loop.run_forever()
    except (KeyboardInterrupt, SystemExit):
        loop.run_until_complete(close_requests())
