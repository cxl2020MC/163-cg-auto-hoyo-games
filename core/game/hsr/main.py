from playwright.async_api import Page

# from . import zzz_utils

from ... import broswer
from ... import ocr
from ... import utils
from ... import config
from ... import push

from ...log import logger as log


async def main(page: Page, account: config._GameAccount):
    await goto_game_home(page, account)
    await quick_book_daily_task(page, account)


async def goto_game_home(page: Page, account: config._GameAccount):
    for _ in range(200):
        ocr_output = await utils.get_ocr(page)
        await utils.ocr_click_txts(page, ocr_output, ["开始游戏", "点击进入"])
        if await utils.ocr_click_txts(page, ocr_output, ["列车补给"]):
            log.info("领取月卡奖励")
            await push.screen_shot_and_push(page, account, "月卡奖励")
        if await utils.match_ocr_txt(ocr_output, ["状态效果"]):
            log.info("找到状态效果")
            return

        await utils.sleep(page, 1)
    raise Exception("没有找到状态效果")


async def open_phone(page: Page):
    for _ in range(15):
        ocr_output = await utils.get_ocr(page)
        if await utils.match_ocr_txt(ocr_output, ["旅情事记"]):
            log.info("当前正在手机界面")
            return True
        else:
            log.info("当前不是手机界面")
            # 刷新截图，防止二次点击，导致切换手机界面
            await broswer.screen_shot(page)
            await utils.click_cv_template(page, "./core/template/hsr/phone.png")
        await utils.sleep(page, 1)
    return False


async def open_entrust(page: Page):
    await open_phone(page)
    ocr_output = await utils.get_ocr(page)
    await utils.ocr_click_txts(page, ocr_output, ["委托"])


async def quick_book_daily_task(page: Page, account: config._GameAccount):
    await daily_entrust(page, account)
    # await open_quick_book(page)
    # await utils.click_cv_template(page, "./core/template/firework.png")
    # await utils.sleep(page, 2)
    # await push.screen_shot_and_push(page, account, "烟花任务完成")
    # await utils.sleep(page, 5)


async def daily_entrust(page: Page, account: config._GameAccount):
    await open_entrust(page)
    for i in range(5):
        ocr_output = await utils.get_ocr(page)
        log.debug(f"第{i+1}次检查领取奖励")
        if await utils.ocr_click_txts(page, ocr_output, ["领取奖励"]):
            await utils.sleep(page, 2)
            await push.screen_shot_and_push(page, account, "今日委托")


async def confirm_to_receive_reward(page: Page):
    for i in range(5):
        ocr_output = await utils.get_ocr(page)
        log.debug(f"第{i+1}次检查确认领取奖励")
        if await utils.ocr_click_txts(page, ocr_output, ["点击空白处关闭"]):
            return True
        await utils.sleep(page, 1)
