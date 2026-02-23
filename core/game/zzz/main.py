from playwright.async_api import Page

from . import zzz_utils

from ... import brswer
from ... import ocr
from ... import utils

from ...log import logger as log


async def main(page: Page):
    await goto_game_home(page)
    await quick_book_daly_task(page)


async def goto_game_home(page: Page):
    for _ in range(1000):
        await brswer.screen_shot(page)
        ocr_output = await ocr.ocr_image()
        await utils.ocr_click_txts(page, ocr_output, ["点击进入", "点击登录", "确定", "今日到账"])
        if await utils.get_ocr_txt_position(ocr_output, "星期"):
            log.info("找到星期")
            return

        await zzz_utils.return_to_streets(page, ocr_output)

        await page.wait_for_timeout(1000)
    log.error("没有找到星期")
    raise Exception("没有找到星期")


async def open_quick_book(page: Page):
    for _ in range(10):
        await brswer.screen_shot(page)
        ocr_output = await ocr.ocr_image()
        if await utils.get_ocr_txt_position(ocr_output, "QUICK"):
            log.info("当前正在快捷手册页面")
            return True
        else:
            log.info("当前不是快捷手册页面")
            await utils.cilck_cv_template(page, "./core/template/kjsc.png")
        await page.wait_for_timeout(1000)
    return False


async def quick_book_daly_task(page: Page):
    for index in range(4):
        await quick_book_daly_task_main(page, index)
        # await open_quick_book(page)


async def quick_book_daly_task_main(page: Page, index: int):
    await open_quick_book(page)
    await brswer.screen_shot(page)
    ocr_output = await ocr.ocr_image()
    match index:
        case 0:
            cofee_box = await utils.get_ocr_txt_position(ocr_output, "咖啡")
            if cofee_box:
                text, box = cofee_box
                res = utils.get_ocr_box_in_range_x(
                    ocr_output, (box[0][0], box[1][0]))
                await utils.ocr_click_txts(page, res, ["前往"])
                await zzz_utils.agree_teleport(page)
                await zzz_utils.wait_for_teleport(page)
                await utils.cilck_cv_template(page, "./core/template/jh.png", 0.7)
                await page.wait_for_timeout(3000)
                await brswer.screen_shot(page)
                ocr_output = await ocr.ocr_image()
                await utils.ocr_click_txts(page, ocr_output, ["一杯汀曼特调"])
                await page.wait_for_timeout(3000)

        case _:
            log.error("无法识别的任务id")
            raise Exception("无法识别的任务id")
