from typing import Any, Callable
from enum import StrEnum
from .log import logger as log

import time


class RetryCountType(StrEnum):
    TIME = "time"
    NUM = "num"


def retry(retry_count_type: RetryCountType = RetryCountType.TIME, retry_count: int = 30, check_result: Callable[[Any], bool] = bool, raise_exception: bool = False, raise_exception_error: Exception | None = None):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            while time.time() - start_time < retry_count:
                result = await func(*args, **kwargs)
                if check_result(result):
                    return result
                log.info(
                    f"函数 {func.__name__} 返回值 {result} 不符合规则，重试 ({int(time.time() - start_time)}/{retry_count}{"s" if retry_count_type == RetryCountType.TIME else ""})")
            error_msg = f"函数 {func.__name__} 在重试类型为 {retry_count_type} 的 {retry_count} 次重试内未能成功执行"
            log.error(error_msg)
            if raise_exception:
                raise raise_exception_error or Exception(error_msg)
            return None
        return wrapper
    return decorator


def check_return_value(retry_value: Any = None):
    def check_result_func(result):
        if result != retry_value:
            return True
        else:
            return False
    return check_result_func
