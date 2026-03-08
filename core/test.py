from playwright.async_api import async_playwright, Page
from . import cg_163, config, broswer, ocr
from .game.zzz import main as zzz_main
from .log import logger as log


async def main():
    accounts = config.config.accounts
    for id, account in accounts.items():
        log.info(f"处理账号id为 {id} 的账号")
        async with async_playwright() as p:
            browser = await p.chromium.launch_persistent_context(f"./data/browser_data/{id}", headless=False, channel="msedge")
            if browser.pages:
                page = browser.pages[0]
            else:
                page = await browser.new_page()
            await cg_163.launch_game(page, account.username, account.password)
            await test(page)
            await browser.close()


async def test(page: Page):
    await zzz_main.goto_game_home(page)
    while True:
        await broswer.screen_shot(page)
        ocr_output = await ocr.ocr_image()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

