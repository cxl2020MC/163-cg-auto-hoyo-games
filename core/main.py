from playwright.async_api import async_playwright, Page
from . import cg_163, config, push
from .game.zzz import main as zzz_main
from .log import logger as log
from collections.abc import Callable, Awaitable


async def main():
    accounts = config.config.accounts
    for account in accounts:
        log.info(f"处理账号id为 {account.id} 的账号")
        await playwright_run(account.id, account, zzz_main.main)
  

    
async def playwright_run(id, account: config._Account, main_func: Callable[[Page, config._Account], Awaitable[None]]):
    browser_data_path = f"./data/browser_data/{id}"
    log.info(f"浏览器数据路径: {browser_data_path}")
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(browser_data_path, headless=False, channel="msedge", record_video_dir=f"data/videos/{id}", record_video_size={"width": 1280, "height": 720})
        page = await browser.new_page()
        if page.video:
            log.info(f"视频录制路径: {await page.video.path()}")
        await cg_163.launch_game(page, account.username, account.password, account.game)
        if len(browser.pages) > 1:
            log.info(f"关闭多余的页面，当前页面数量: {len(browser.pages)}")
            for p in browser.pages:
                if p != page:
                    await p.close()
        await main_func(page, account)
        await push.wait_all_messages_push()
        await browser.close()