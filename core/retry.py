from .log import logger as log

import time



def retry(retry_times: int = 10, raise_exception: bool = False):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            while time.time() - start_time < retry_times:
                result = await func(*args, **kwargs)
                if result:
                    return result
                log.info(f"函数 {func.__name__} 无返回值，重试 ({int(time.time() - start_time)} / {retry_times} s)")
            log.error(f"尝试了 {retry_times} 次，函数 {func.__name__} 仍然失败")
            if raise_exception:
                raise Exception(f"函数 {func.__name__} 在 {retry_times} 秒内未能成功执行")
            return None
        return wrapper
    return decorator