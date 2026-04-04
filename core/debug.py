from . import main as core_main
from . import config
from .game.zzz import main as zzz_main
from .log import logger as log


async def main():
    accounts = config.config.accounts
    input_id = input(f"请输入要运行的账号id: ")
    for account in accounts:
        if str(account.id) != input_id:
            log.info(f"跳过账号id为 {account.id} 的账号")
            continue
        log.info(f"处理账号id为 {account.id} 的账号")
        await core_main.playwright_run(account.id, account, zzz_main.main)
  

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())