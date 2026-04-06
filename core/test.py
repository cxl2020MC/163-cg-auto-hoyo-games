from playwright.async_api import async_playwright, Page
from . import config, broswer, ocr
from .game.zzz import main as zzz_main
from .log import logger as log

from . import main as core_main


async def test(page: Page, account: config._GameAccount):
    await zzz_main.goto_game_home(page, account)
    while True:
        await broswer.screen_shot(page)
        ocr_output = await ocr.ocr_image()

async def main():
    accounts = config.config.accounts
    for account in accounts:
        log.info(f"处理账号id为 {account.id} 的账号")
        await core_main.playwright_run(account.id, account, test)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

