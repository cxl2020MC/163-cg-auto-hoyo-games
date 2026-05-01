import asyncio
import time
import traceback

import schedule

from core import main
from core.log import logger as log


def run(interval=1):
    while True:
        schedule.run_pending()
        time.sleep(interval)


def schedule_main():
    log.debug("执行定时任务")
    try:
        asyncio.run(main.main())
        log.debug("执行定时任务成功")
    except Exception:
        log.error(f"执行定时任务失败: {traceback.format_exc()}")


schedule.every().day.at("05:30").do(schedule_main)


if __name__ == "__main__":
    run()
