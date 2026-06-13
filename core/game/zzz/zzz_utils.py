from enum import StrEnum

from playwright.async_api import Page

from ... import browser, types, utils, retry
from ...log import logger as log


class Game_Status(StrEnum):
    Street = "街区"
    Quick_Book = "快捷手册"
    Loading = "加载中"
    Agree_Model = "同意"
    Unknown = "未知"


# 检查游戏状态
async def check_game_status(page: Page, ocr_result: types.OCR_Results):
    log.info("检查游戏状态")
    if await is_in_street(ocr_result):
        game_status = Game_Status.Street
    elif await utils.match_ocr_txt(ocr_result, ["QUICK"]):
        game_status = Game_Status.Quick_Book
    elif await utils.match_ocr_txt(ocr_result, ["确定"], exact=True):
        game_status = Game_Status.Agree_Model
    elif await utils.match_ocr_txt(ocr_result, ["NOW LOADING"]):
        game_status = Game_Status.Loading
    else:
        game_status = Game_Status.Unknown
    log.info(f"当前游戏状态为: {game_status}")
    return game_status


# 返回街区
async def return_to_streets(page: Page, ocr_result: types.OCR_Results):
    cv_reslt = await utils.match_screenshot_cv_template("./core/template/tc.png", 0.65)
    if cv_reslt:
        cv_box_center = utils.get_cv_box_center(cv_reslt)
        log.info(f"在 {cv_box_center} 找到退出按钮")
        x, y = cv_box_center
        await browser.click_video(page, x, y)
    else:
        await utils.ocr_click_txts(page, ocr_result, ["X", "x"])


async def is_in_street(ocr_result: types.OCR_Results):
    if await utils.match_ocr_txt(ocr_result, ["星期"]):
        log.info("当前在街区")
        return True


@retry.retry(retry_count=120, raise_exception_error=Exception("传送加载超时"))
async def wait_for_teleport(page: Page):
    ocr_output = await utils.get_ocr(page)
    if await is_in_street(ocr_output):
        log.info("已到达目的地")
        return True


async def agree_teleport(page: Page):
    return await click_confirm(page)


# 点击弹窗确认按钮
@retry.retry(raise_exception_error=Exception("没有找到确认按钮"))
async def click_confirm(page: Page, ocr_output: types.OCR_Results | None = None):
    ocr_output = await utils.get_ocr(page, ocr_output)
    if await utils.ocr_click_txts(page, ocr_output, ["确认", "确定"], exact=True):
        return True
    # 重置ocr_output
    ocr_output = None
    await utils.sleep(page, 1)


async def click_interaction(page: Page):
    for i in range(5):
        await browser.screen_shot(page)
        log.debug(f"第{i+1}次检查交互按钮")
        if await utils.click_cv_template(page, "./core/template/jh.png"):
            return True
        await utils.sleep(page, 1)
    log.warning("没有找到交互按钮")
    return False
