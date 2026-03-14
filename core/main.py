from playwright.async_api import async_playwright, Page
from . import cg_163, config, push
from .game.zzz import main as zzz_main
from .log import logger as log
from collections.abc import Callable, Awaitable


async def main():
    accounts = config.config.accounts
    for id, account in accounts.items():
        log.info(f"处理账号id为 {id} 的账号")
        await playwright_run(id, account, zzz_main.main)
  

    
async def playwright_run(id, account: config._Account, main_func: Callable[[Page, config._Account], Awaitable[None]]):
    browser_data_path = f"./data/browser_data/{id}"
    log.info(f"浏览器数据路径: {browser_data_path}")
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(browser_data_path, headless=False, channel="msedge")
        if browser.pages:
            page = browser.pages[0]
        else:
            page = await browser.new_page()
        await cg_163.launch_game(page, account.username, account.password, account.game)
        await main_func(page, account)
        await push.send_all_messages()
        await browser.close()