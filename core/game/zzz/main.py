from playwright.async_api import Page

from . import zzz_utils

from ... import broswer
from ... import ocr
from ... import utils

from ...log import logger as log


async def main(page: Page):
    await goto_game_home(page)
    await quick_book_daily_task(page)


async def goto_game_home(page: Page):
    for _ in range(1000):
        await broswer.screen_shot(page)
        ocr_output = await ocr.ocr_image()
        await utils.ocr_click_txts(page, ocr_output, ["点击进入", "点击登录", "确定", "今日到账"])
        if await utils.match_ocr_txt(ocr_output, ["星期"]):
            log.info("找到星期")
            return

        await zzz_utils.return_to_streets(page, ocr_output)

        await utils.sleep(page, 1)
    log.error("没有找到星期")
    raise Exception("没有找到星期")


async def open_quick_book(page: Page):
    for _ in range(10):
        await broswer.screen_shot(page)
        ocr_output = await ocr.ocr_image()
        if await utils.match_ocr_txt(ocr_output, ["QUICK"]):
            log.info("当前正在快捷手册页面")
            return True
        else:
            log.info("当前不是快捷手册页面")
            await utils.click_cv_template(page, "./core/template/kjsc.png")
        await utils.sleep(page, 1)
    return False


async def quick_book_daily_task(page: Page):
    for index in range(2):
        await quick_book_daily_task_main(page, index)
    await open_quick_book(page)
    await utils.click_cv_template(page, "./core/template/firework.png")
    await utils.sleep(page, 5)


async def quick_book_daily_task_main(page: Page, index: int):
    await open_quick_book(page)
    await broswer.screen_shot(page)
    ocr_output = await ocr.ocr_image()
    match index:
        case 0:
            cofee_box = await utils.match_ocr_txt(ocr_output, ["咖啡"])
            if cofee_box:
                box = cofee_box.box
                res = utils.get_ocr_box_in_range_x(
                    ocr_output, (box[0][0], box[1][0]))
                await utils.ocr_click_txts(page, res, ["前往"])
                await zzz_utils.agree_teleport(page)
                await zzz_utils.wait_for_teleport(page)
                await utils.click_cv_template(page, "./core/template/jh.png", 0.7)
                await utils.sleep(page, 3)
                await broswer.screen_shot(page)
                ocr_output = await ocr.ocr_image()
                await utils.ocr_click_txts(page, ocr_output, ["一杯汀曼特调"])
                await utils.sleep(page, 1)
                await zzz_utils.click_confirm(page)
        case 1:
            divine_box = await utils.match_ocr_txt(ocr_output, ["占卜"])
            if divine_box:
                box = divine_box.box
                res = utils.get_ocr_box_in_range_x(
                    ocr_output, (box[0][0], box[1][0]))
                await utils.ocr_click_txts(page, res, ["前往"])
                await zzz_utils.agree_teleport(page)
                await zzz_utils.wait_for_teleport(page)
                await utils.click_cv_template(page, "./core/template/jh.png", 0.7)
                await utils.sleep(page, 3)
                await broswer.screen_shot(page)
                ocr_output = await ocr.ocr_image()
                for _ in range(10):
                    if await utils.ocr_click_txts(page, ocr_output, ["开", "開"]):
                        break
                    await utils.sleep(page, 1)
                for _ in range(5):
                    if await utils.match_ocr_txt(ocr_output, ["滑动屏幕"]):
                        page_size = await utils.get_page_size(page)
                        if page_size:
                            await utils.drag(page, (page_size[0]*0.1, page_size[1]/2), (page_size[0]*0.9, page_size[1]/2))
                    await utils.sleep(page, 1)
                await zzz_utils.click_confirm(page)
                await zzz_utils.click_confirm(page)
                await utils.sleep(page, 3)
                await utils.click_cv_template(page, "./core/template/tc.png")



        case _:
            log.error("无法识别的任务id")
            raise Exception("无法识别的任务id")
