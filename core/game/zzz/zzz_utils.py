from playwright.async_api import Page

from ... import broswer
from ... import ocr
from ... import types
from ... import utils
from ... import config
from ... import img_cv

from ...log import logger as log

from enum import StrEnum


class Game_Status(StrEnum):
    Street = "街区"
    Quick_Book = "快捷手册"
    Loading = "加载中"
    Unknown = "未知"

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
        elif "NOW LOADING" in ocr_result_item.txt:
            game_status = Game_Status.Loading
            break
        else:
            game_status = Game_Status.Unknown
    log.info(f"当前游戏状态为: {game_status}")
    return game_status


# 返回街区
async def return_to_streets(page: Page, ocr_result: types.OCR_Results):

    cv_result = await img_cv.match_template(str(config.SCREENSHOT_PATH), "./core/template/tc.png")

    cv_box_center = utils.get_cv_box_center(cv_result)
    if cv_box_center:
        log.info(f"在 {cv_box_center} 找到退出按钮")
        x, y = cv_box_center
        await broswer.click_video(page, x, y)

    else:
        await utils.ocr_click_txts(page, ocr_result, ["X", "x"])


async def agree_teleport(page: Page) -> bool:
    for i in range(5):
        await broswer.screen_shot(page)
        ocr_output = await ocr.ocr_image()
        log.debug(f"第{i+1}次检查同意传送页面")
        if await utils.match_ocr_txt(ocr_output, ["传送"]):
            log.info("当前正在同意传送页面")
            await utils.ocr_click_txts(page, ocr_output, ["确认"])
            return True
        await utils.sleep(page, 1)
    log.warning("没有找到同意传送页面")
    return False


async def wait_for_teleport(page: Page) -> bool:
    for i in range(60):
        await broswer.screen_shot(page)
        ocr_output = await ocr.ocr_image()
        game_status = await check_game_status(page, ocr_output)
        if game_status == Game_Status.Street:
            log.info("已到达目的地")
            return True
        await utils.sleep(page, 1)
    return False


# 点击弹窗确认按钮
async def click_confirm(page: Page, ocr_result: types.OCR_Results):
    for i in range(5):
        await broswer.screen_shot(page)
        ocr_output = await ocr.ocr_image()
        log.debug(f"第{i+1}次检查确认按钮")
        if await utils.ocr_click_txts(page, ocr_output, ["确认"]):
            return True
        await utils.sleep(page, 1)
    log.warning("没有找到确认按钮")
    return False