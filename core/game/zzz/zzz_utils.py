from playwright.async_api import Page

from ... import brswer
from ... import ocr
from ... import types
from ... import utils
from ... import config
from ... import img_cv

from ...log import logger as log

from enum import Enum


class Game_Status(Enum):
    Street = "街区"
    Quick_Book = "快捷手册"

# 检测游戏当前状态


async def check_game_status(page: Page, ocr_result: types.OCR_Results):
    log.info("检查游戏状态")
    for ocr_result_item in ocr_result:
        if "星期" in ocr_result_item.txt:
            game_status = Game_Status.Street
            break
        elif "QUICK" in ocr_result_item.txt:
            game_status = Game_Status.Quick_Book
            break
    log.info(f"当前游戏状态为: {game_status}")
    return game_status


# 返回街区
async def return_to_streets(page: Page, ocr_result: types.OCR_Results):

    cv_result = await img_cv.mach_template(str(config.SCREENSHOT_PATH), "./core/template/tc.png")

    cv_box_center = utils.get_cv_box_center(cv_result)
    if cv_box_center:
        log.info(f"在 {cv_box_center} 找到退出按钮")
        x, y = cv_box_center
        await brswer.click_video(page, x, y)

    else:
        await utils.ocr_click_txts(page, ocr_result, ["X", "x"])


async def agree_teleport(page: Page) -> bool:
    for i in range(5):
        await brswer.screen_shot(page)
        ocr_output = await ocr.ocr_image()
        if ocr_output is None:
            log.error("OCR 返回结果为空")
            continue
        if await utils.get_ocr_txt_position(ocr_output, "传送"):
            log.info("当前正在同意传送页面")
            await utils.ocr_click_txts(page, ocr_output, ["确认"])
            return True
        await page.wait_for_timeout(1000)
    raise Exception("无法进入传送页面")
