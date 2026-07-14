from playwright.async_api import Page, async_playwright

from . import browser, config
from . import main as core_main
from . import ocr, utils
from .game.zzz import main as zzz_main
from .log import logger as log


async def test(page: Page, account: config._GameAccount):
    # await zzz_main.goto_game_home(page, account)
    while True:
        await browser.screen_shot(page)
        ocr_outputs = await ocr.ocr_image()
        await utils.sleep(page, 1)


async def main():
    accounts = config.config.game_accounts

    for account in accounts:
        log.info(f"处理账号id为 {account.id} 的账号")
        await core_main.playwright_run(account.id, account, test)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
