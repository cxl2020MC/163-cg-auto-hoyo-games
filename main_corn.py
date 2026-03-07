from core import main
from core.log import logger as log
import asyncio
import schedule
import time


def run(interval=1):
    while True:
        schedule.run_pending()
        time.sleep(interval)


def schedule_main():
    log.debug("执行定时任务")
    try:
        asyncio.run(main.main())
        log.debug("执行定时任务成功")
    except Exception as e:
        log.error(f"执行定时任务失败: {e}")


schedule.every().day.at("6:00").do(schedule_main)


if __name__ == "__main__":
    run()
