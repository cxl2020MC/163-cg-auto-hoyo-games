from typing import Any, Callable
from .log import logger as log

import time



def time_retry(retry_times: int = 10, check_result: Callable[[Any], bool] = bool, raise_exception: bool = True, raise_exception_error: Exception | None = None):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            while time.time() - start_time < retry_times:
                result = await func(*args, **kwargs)
                if check_result(result):
                    return result
                log.info(f"函数 {func.__name__} 返回值不符合规则，重试 ({int(time.time() - start_time)}s / {retry_times}s)")
            log.error(f"尝试了 {retry_times} 次，函数 {func.__name__} 仍然失败")
            if raise_exception:
                if raise_exception_error:
                    raise raise_exception_error
                raise Exception(f"函数 {func.__name__} 在 {retry_times} 秒内未能成功执行")
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