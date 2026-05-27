import traceback
from collections.abc import Awaitable, Callable

from playwright.async_api import BrowserContext, Page, async_playwright

from . import cg_163, config, game_map, push
from .game.hsr import main as hsr_main
from .game.zzz import main as zzz_main
from .log import logger as log

def get_game_main_func(game_name: str) -> Callable[[Page, config._GameAccount], Awaitable[None]]:
    match game_name:
        case config.GameEnum.jql:
            return zzz_main.main
        case config.GameEnum.hsr:
            return hsr_main.main
        case _:
            raise Exception(f"未找到游戏 {game_name} 的主函数")

async def main():
    game_accounts = config.config.game_accounts
    for game_account in game_accounts:
        log.info(f"处理账号id为 {game_account.id} 的账号")
        log.info(f"游戏: {game_account.game}, 服务器: {game_account.server}")
        run_main_func = get_game_main_func(game_account.game)

        try:
            await playwright_run(game_account.id, game_account, run_main_func)
        except Exception as e:
            log.error(
                f"账号id为 {game_account.id} 的账号运行发生错误，错误信息: {traceback.format_exc()}")


async def playwright_run(id, account: config._GameAccount, main_func: Callable[[Page, config._GameAccount], Awaitable[None]]):
    browser_data_path = f"data/browser_data/{id}"
    log.info(f"浏览器数据路径: {browser_data_path}")
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(browser_data_path, headless=False, channel="msedge", record_video_dir=f"data/videos/{id}", record_video_size={"width": 1280, "height": 720})

        if len(browser.pages) == 0:
            log.info("没有页面，创建新页面")
            page = await browser.new_page()
        else:
            log.info(f"使用已打开的页面，当前页面数量: {len(browser.pages)}")
            page = browser.pages[0]
        

        if page.video:
            log.info(f"视频录制路径: {await page.video.path()}")
            pagevideo_path = await page.video.path()
        else:
            log.warning("当前页面没有视频录制功能")
            pagevideo_path = None
        
        game_id = game_map.get_game_id_by_account(account)
        await cg_163.launch_game(page, game_id)

        await close_other_pages(browser, page)

        await main_func(page, account)
    if pagevideo_path:
        await push.push_video(account, "游戏脚本视频消息", pagevideo_path)
    await push.wait_all_messages_push()


async def close_other_pages(browser: BrowserContext, current_page: Page):
    log.info(f"关闭多余的页面，当前页面数量: {len(browser.pages)}")
    for page in browser.pages:
        if page != current_page:
            await page.close()
    log.info(f"剩余页面数量: {len(browser.pages)}")
