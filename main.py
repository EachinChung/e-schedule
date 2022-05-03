import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from components.redis import register_redis
from components.requests import close_requests, register_requests
from script.checkin_daily import checkin_daily
from script.refresh_clash_subscription import refresh_clash_subscription

if __name__ == "__main__":
    logging.basicConfig(
        filename="e-schedule.log",
        level=logging.INFO,
        format="[%(levelname)s] %(asctime)s - %(message)s",
    )

    loop = asyncio.get_event_loop()
    loop.run_until_complete(register_redis())
    loop.run_until_complete(register_requests())

    scheduler = AsyncIOScheduler()
    scheduler.add_job(checkin_daily, "cron", hour=0, minute=10)
    scheduler.add_job(refresh_clash_subscription, "interval", minutes=10)
    scheduler.start()

    try:
        loop.run_forever()
    except (KeyboardInterrupt, SystemExit):
        loop.run_until_complete(close_requests())
