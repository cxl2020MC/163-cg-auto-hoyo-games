from .log import logger as log
from playwright.async_api import Page


async def check_login(page: Page, phone, password):
    log.debug("等待页面加载完成")
    await page.wait_for_load_state("load")
    log.debug("检查登录")
    login_status = await page.get_by_text("登录").is_visible()
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

