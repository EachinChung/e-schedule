from asyncio import sleep
from functools import wraps
from traceback import format_exc
from typing import Callable, List, Union

from loguru import logger


class MaxRetriesException(BaseException):
    def __init__(self, func: Callable, retries: int, errors: List[BaseException]):
        self.func = func
        self.retries = retries
        self.errors = errors

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"{self.func.__name__} has been retried {self.retries} times\n\n{display_errors(self.errors)}"


def display_errors(errors: List[BaseException]) -> str:
    return "\n".join(str(e) for e in errors)


def retry(retries: int = 5, delay: Union[int, float] = 0, step: Union[int, float] = 0):
    """函数执行出现异常时自动重试的简单装饰器

    >>> @retry(retries=2, delay=60, step=60)
    >>> def func():
    >>>     ...

    :param retries: 最多重试次数
    :param delay: 每次重试的延迟，单位秒
    :param step: 每次重试后延迟递增，单位秒
    """

    def retry_decorator(func: Callable):
        @wraps(func)
        async def do_func_and_retries(*args, **kwargs):
            times = 1
            errors = []
            nonlocal delay, step, retries

            while times <= retries:
                try:
                    logger.info("call the {} {} times", func.__name__, times)
                    return await func(*args, **kwargs)
                except BaseException as err:  # noqa: PIE786
                    logger.warning(
                        "call the {} {} times err: {}, traceback: {}", func.__name__, times, err, format_exc()
                    )
                    errors.append(err)
                    times += 1
                    if (delay > 0 or step > 0) and times < retries:
                        await sleep(delay)
                        delay += step
            else:
                err = MaxRetriesException(func, retries, errors)
                raise err

        return do_func_and_retries

    return retry_decorator
