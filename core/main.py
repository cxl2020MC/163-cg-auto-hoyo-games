from playwright.async_api import async_playwright
from . import cg_163, config
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
            await zzz_main.main(page)
            await browser.close()