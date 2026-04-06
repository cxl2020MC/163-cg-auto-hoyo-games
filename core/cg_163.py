from .log import logger as log
from playwright.async_api import Page, expect
import asyncio


async def check_login(page: Page):
    log.debug("检查登录")
    # login_status = await page.get_by_text("登录").is_visible()
    try:
        await expect(page.get_by_text("登录")).to_be_visible()
        login_status = True
    except AssertionError:
        login_status = False

    log.info(f"登录状态: {login_status}")
    return login_status


async def auto_login(page: Page, phone, password):
    # await page.get_by_role("banner").get_by_text("登录").dispatch_event('click')
    await page.get_by_placeholder("手机号").fill(phone)
    await page.get_by_text("密码登录").first.dispatch_event('click')
    await page.get_by_placeholder("密码").fill(password)
    await page.get_by_role("button", name="登录").click()
    # await page.get_by_role("link", name="同意").click()
    await page.get_by_text("同意", exact=True).click()
    await page.get_by_role("button", name="登录").click()
    log.info("登录成功, 等待10秒")
    await page.wait_for_timeout(10000)


async def launch_game(page: Page, game_code: str = "jql_gjf"):
    await page.goto(f"https://cg.163.com/?action_link=cloudgaming%3A%2F%2Fstartgame%3Fgame_code%3D{game_code}%26game_open_action%3Dthis_game")
    await check_login(page)
    asyncio.create_task(check_cg_game_activity(page))
    asyncio.create_task(check_cg_game_key_position(page))
    asyncio.create_task(select_cg_server_run_game_normal_mode(page))
    asyncio.create_task(agree_exit_cg_game(page))


async def check_cg_game_activity(page: Page):
    log.debug("检查云游戏活动")
    loctor = page.locator(".pc_close")
    try:
        await expect(loctor).to_be_visible()
        activity_status = True
    except AssertionError:
        activity_status = False

    log.info(f"云游戏活动页面: {activity_status}")
    if activity_status:
        log.info("发现云游戏活动，点击关闭")
        await loctor.click()

    return activity_status


async def check_cg_game_key_position(page: Page):
    log.debug("检查云游戏按键位置")
    loctor = page.locator("div.keylayout")
    try:
        await expect(loctor).to_be_visible(timeout=50000)
        key_position_status = True
    except AssertionError:
        key_position_status = False

    log.info(f"云游戏按键位置页面: {key_position_status}")
    if key_position_status:
        log.info("发现云游戏按键位置页面，尝试关闭")
        await loctor.press("F12")

    return key_position_status


async def select_cg_server_run_game_normal_mode(page: Page):
    try:
        await expect(page.get_by_text("请选择服务器")).to_be_visible()
        normal_mode_status = True
    except AssertionError:
        normal_mode_status = False
    log.info(f"云游戏切换服务器页面: {normal_mode_status}")
    if normal_mode_status:
        log.info("发现云游戏切换服务器页面，尝试点击进入游戏")
        await page.locator(".serve_normal .icon.serve_select").click()
        await page.get_by_text("马上游玩").click()


async def agree_exit_cg_game(page: Page):
    try:
        await expect(page.get_by_text("退出并开启新游戏")).to_be_visible()
        normal_mode_status = True
    except AssertionError:
        normal_mode_status = False
    log.info(f"云游戏退出并开启新游戏页面: {normal_mode_status}")
    if normal_mode_status:
        log.info("发现云游戏退出并开启新游戏页面，尝试点击确定退出")
        await page.get_by_text("确定退出").click()


async def exit_cg_game(page: Page):
    await page.locator("body").press("Escape")
    await page.get_by_text("退出游戏").click()
    await page.get_by_text("确认", exact=True).click()
    return True
