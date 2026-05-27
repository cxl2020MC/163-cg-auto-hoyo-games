import asyncio
import traceback
from typing import Coroutine, Any

from playwright.async_api import Page, expect

from .log import logger as log


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


def get_launch_game_url(game_code: str):
    return f"https://cg.163.com/?action_link=cloudgaming%3A%2F%2Fstartgame%3Fgame_code%3D{game_code}%26game_open_action%3Dthis_game"


async def launch_game(page: Page, game_code: str):
    await page.goto(get_launch_game_url(game_code))
    await check_login(page)
    # add_background_task(asyncio.create_task(check_cg_game_activity(page)))
    # add_background_task(asyncio.create_task(check_cg_game_home_activity(page)))
    # add_background_task(asyncio.create_task(check_cg_game_key_position(page)))
    # add_background_task(asyncio.create_task(
    #     select_cg_server_run_game_normal_mode(page)))
    # add_background_task(asyncio.create_task(agree_exit_cg_game(page)))
    # asyncio.create_task(check_cg_game_activity(page))
    # asyncio.create_task(check_cg_game_home_activity(page))
    # asyncio.create_task(check_cg_game_key_position(page))
    # asyncio.create_task(select_cg_server_run_game_normal_mode(page))
    # asyncio.create_task(agree_exit_cg_game(page))

    add_background_task(check_cg_game_activity(page), "check_cg_game_activity")
    add_background_task(check_cg_game_home_activity(page), "check_cg_game_home_activity")
    # add_background_task(check_cg_game_activity_v2(page), "check_cg_game_activity_v2")
    add_background_task(check_cg_game_key_position(page), "check_cg_game_key_position")
    add_background_task(select_cg_server_run_game_normal_mode(page), "select_cg_server_run_game_normal_mode")
    add_background_task(agree_exit_cg_game(page), "agree_exit_cg_game")



async def check_cg_game_activity(page: Page):
    log.debug("检查云游戏活动")
    # <button class="pc_close"></button>
    # loctor = page.locator("button.pc_close")
    loctor = page.locator("div.gameactivity")
    # <div class="gameactivity"><!----><div data-v-5eabf4e4="" class="confirm-shade iframe-confirm fadein is-run " style=""><div data-v-5eabf4e4="" class="cofirm confirm-transparent run-zj"><!----><div data-v-5eabf4e4="" class="cofirm-cont"><!----><div data-v-5eabf4e4="" class="confirm-main"><iframe data-v-5eabf4e4="" src="https://cloudgame.webapp.163.com/checkin/?activityid=69faebf7d3495da1fcca0eab&amp;source=run_page&amp;token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE3Nzg2Njc5NzUsIm5iZiI6MTc3ODY2Nzk3NSwianRpIjoiMzVmOGJjMTAtOWI2Zi00OWZlLTllYjYtMzY0MzhjYjNiZjEyIiwiaWRlbnRpdHkiOiI2OWUyZWRmMDIxMWVkZDEzODYwNjk1MjMiLCJmcmVzaCI6ZmFsc2UsInR5cGUiOiJhY2Nlc3MiLCJ1c2VyX2NsYWltcyI6eyJudW1iZXIiOjY4MjMyNjE4NCwidGltZXN0YW1wIjoxNzc4NjY3OTc1LCJzYWx0Ijo5NH19.NX8lkMiPtt26z-ypoH3flI_9r0UYl-8V7DLi8FH9ea8" allowfullscreen="allowfullscreen" allowtransparency="true" frameborder="0" style="width: 100%; height: 100%;"></iframe></div><div data-v-5eabf4e4="" class="cofirm-btns"></div></div></div></div><!----><div data-v-5eabf4e4="" class="confirm-shade" style="display: none;"><div data-v-5eabf4e4="" class="cofirm faq-confirm"><!----><div data-v-5eabf4e4="" class="cofirm-cont"><!----><div data-v-5eabf4e4="" class="faq-scroll"><div data-v-5eabf4e4="" class="faq-detail f14"><div data-v-7a997152="" class="htmltext" data-v-5eabf4e4=""></div></div></div><div data-v-5eabf4e4="" class="cofirm-btns"></div></div></div></div><!----><!----><!----><!----><!----><!----><div data-v-5eabf4e4="" class="confirm-shade frametips-confirm" style="display: none;"><div data-v-5eabf4e4="" class="cofirm"><!----><div data-v-5eabf4e4="" class="cofirm-cont"><!----><!----><div data-v-5eabf4e4="" class="confirm-main"></div><div data-v-5eabf4e4="" class="cofirm-btns"></div></div></div></div><div class="confirm-shade fadeout" style="display: none;"><div class="appointment landscape"><div class="appointbox"><!----><div class="appointdesc"><p class="f14"></p><button class="g-Btn g-Btn-green2">马上预约<i class="icon icon-arrow-white"></i></button></div></div><button class="slide-close"></button></div></div><!----><div class="confirm-shade" style="display: none;"><div class="port_resource_con"><p class="port_resource_tips"><span></span><i></i>点击空白处关闭<i class="right"></i><span></span></p><div class="port_resource_iframe" style=""><iframe allowfullscreen="allowfullscreen" allowtransparency="true" frameborder="0" style="width: 100%; height: 100%; transform: translate3d(0px, 0px, 1px);"></iframe><div class="port_resource_enter"><button class="g-Btn g-Btn-green2">前往活动页</button></div></div></div></div></div>
    try:
        await expect(loctor).to_be_visible(timeout=50000)
        activity_status = True
    except AssertionError:
        activity_status = False

    log.info(f"云游戏活动页面: {activity_status}")
    if activity_status:
        log.info("发现云游戏活动，点击关闭")
        await (page.locator("iframe").first.content_frame.get_by_role("button")).click()
        # frame = page.frame(url=r'.*')
        # log.debug(f"当前页面的iframe: {page.frames}")
        # if frame:
        #     log.info("找到云游戏活动框架，尝试在框架内点击关闭按钮")
        #     loctor = frame.locator(".pc_close")
        #     await expect(loctor).to_be_visible()
        #     log.info(f"在云游戏活动框架内找到关闭按钮 {loctor}，点击关闭")
        #     await loctor.click()
        # await page.evaluate('() => document.querySelector(".gameactivity").remove()')

    return activity_status


async def check_cg_game_activity_v2(page: Page):
    log.debug("检查云游戏活动")
    loctor = page.locator("div.gameactivity")
    for _ in range(3):
        try:
            await expect(loctor).to_be_visible(timeout=50000)
            activity_status = True
        except AssertionError:
            activity_status = False

        log.info(f"云游戏活动页面: {activity_status}")
        if activity_status:
            log.info("发现云游戏活动，点击关闭")
            await page.evaluate('() => document.querySelector(".gameactivity").remove()')
        else:
            break
        # return activity_status


async def check_cg_game_home_activity(page: Page):
    log.debug("检查云游戏主页活动")
    # <button data-v-437e421d="" class="slide-close"></button>
    # slide
    loctor = page.locator("div.slide")
    try:
        await expect(loctor).to_be_visible()
        home_activity_status = True
    except AssertionError:
        home_activity_status = False

    log.info(f"云游戏主页活动页面: {home_activity_status}")
    if home_activity_status:
        log.info("发现云游戏主页活动，点击关闭")
        loctor = page.locator("div.slide button.slide-close")
        await loctor.click()

    return home_activity_status


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


background_task: set[asyncio.Task] = set()


def add_background_task(corn: Coroutine[Any, Any, Any], task_name: str | None = None):
    asyncio_task = asyncio.create_task(corn)
    if task_name:
        asyncio_task.set_name(task_name)
    log.info(f"添加后台任务: {asyncio_task.get_name()} ，当前后台任务数量: {len(background_task)+1}")
    def task_done_callback(t: asyncio.Task):
        background_task.discard(t)
        try:
            t.result()
        except Exception:
            log.error(f"后台任务 {t.get_name()} 发生异常: {traceback.format_exc()}")
        else:
            log.info(f"后台任务 {t.get_name()} 已完成，当前后台任务列表: {[t.get_name() for t in background_task]}")
    asyncio_task.add_done_callback(task_done_callback)
    background_task.add(asyncio_task)
    log.debug(f"添加后台任务 {asyncio_task.get_name()} 已完成，当前后台任务列表: {[t.get_name() for t in background_task]}")
