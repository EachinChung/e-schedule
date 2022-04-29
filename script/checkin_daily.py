import asyncio
import logging

from aiohttp.typedefs import LooseCookies

from components.monitor import monitor
from components.requests import close_requests, post, register_requests
from components.retry import retry
from setting import setting


@retry(retries=3)
async def auth() -> LooseCookies:
    rsp = await post(
        f"{setting.account.airport}/auth/login",
        data={"email": setting.account.email, "passwd": setting.account.password, "code": ""},
    )
    details = rsp.json()
    if details.get("ret") != 1:
        msg = f"airport login failed {details.get('msg') or details}"
        logging.error(msg)
        raise ValueError(msg)

    logging.info("%s login success", setting.account.email)
    return rsp.cookies


@retry(retries=3, delay=30, step=30)
async def checkin(cookies: LooseCookies):
    rsp = await post(f"{setting.account.airport}/user/checkin", cookies=cookies)
    details = rsp.json()
    if details.get("ret") != 1 and details.get("msg") != "您似乎已经签到过了...":
        msg = f"checkin failed {details.get('msg') or details}"
        logging.error(msg)
        raise ValueError(msg)

    logging.info("%s checkin: %s", setting.account.email, details.get("msg"))


@monitor
async def checkin_daily():
    cookies = await auth()
    await checkin(cookies)


if __name__ == "__main__":
    logging.basicConfig(
        filename="checkin_daily.log",
        level=logging.INFO,
        format="[%(levelname)s] %(asctime)s - %(message)s",
    )

    loop = asyncio.get_event_loop()
    loop.run_until_complete(register_requests())
    loop.run_until_complete(checkin_daily())
    loop.run_until_complete(close_requests())
