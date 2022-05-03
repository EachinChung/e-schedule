import logging
from functools import wraps

from components.requests import post
from setting import setting

MARKDOWN_MSG = """
# [{mode}] e-schedule 告警


{msg}
"""


async def alert(msg):
    try:
        rsp = await post(
            setting.monitor.wecom,
            json={"msgtype": "markdown", "markdown": {"content": MARKDOWN_MSG.format(mode=setting.mode, msg=msg)}},
        )
        assert rsp.status_code == 200, f"发送告警失败, {rsp.status_code}"
        assert rsp.json().get("errcode") == 0, f"发送告警失败, {rsp.json()}"
    except BaseException as e:  # noqa: PIE786
        logging.exception("wecom robot fail, err: %s, msg: %s", e, msg)


def monitor(func):
    @wraps(func)
    async def do_func_and_alert(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except BaseException as err:  # noqa: PIE786
            logging.exception(err)
            await alert(err)

    return do_func_and_alert
