from .log import logger as log
from playwright.async_api import Page, expect
import asyncio


async def check_login(page: Page, phone, password):
    log.debug("检查登录")
    # login_status = await page.get_by_text("登录").is_visible()
    try:
        await expect(page.get_by_text("登录")).to_be_visible()
        login_status = True
    except AssertionError:
        login_status = False

    log.info(f"需要登录: {login_status}")
    if login_status:
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


async def launch_game(page: Page, cg_phone, cg_password, game_code: str = "jql_gjf"):
    await page.goto(f"https://cg.163.com/?action_link=cloudgaming%3A%2F%2Fstartgame%3Fgame_code%3D{game_code}%26game_open_action%3Dthis_game")
    await check_login(page, cg_phone, cg_password)
    asyncio.create_task(check_cg_game_activity(page))
    asyncio.create_task(check_cg_game_key_position(page))


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