from . import config
from . import main as core_main
from .game.zzz import main as zzz_main
from .log import logger as log


async def main():
    accounts = config.config.game_accounts
    input_id = input(f"请输入要运行的账号id: ")
    input_game = input(f"请输入要运行的游戏: ")
    input_server = input(f"请输入要运行的服务器: ")
    for account in accounts:
        if str(account.id) != input_id or account.game != input_game or account.server != input_server:
            log.info(f"跳过账号: {account}")
            continue
        log.info(f"处理账号: {account}")
        await core_main.playwright_run(account.id, account, zzz_main.main)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
