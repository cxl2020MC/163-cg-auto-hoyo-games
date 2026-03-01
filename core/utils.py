from pathlib import Path
from playwright.async_api import Page

from . import broswer


from . import config, types, img_cv
from .log import logger as log


def get_img_file_path(file_name):
    return Path(config.CHANGE_IMG_DIR, file_name)


SCREENSHOT_PATH = get_img_file_path("screenshot.png")


async def sleep(page: Page, seconds: int):
    await page.wait_for_timeout(seconds * 1000)

async def match_ocr_txts(ocr_output: types.OCR_Results, match_txts: list[str]):
    txt_positions: list[types.OCR_Result] = []
    for ocr in ocr_output:
        txt, box = ocr.txt, ocr.box
        for match_txt in match_txts:
            if match_txt in txt:
                log.debug(f"匹配到文本 {match_txt} 于 {txt} , 位置范围 {box}")
                txt_positions.append(ocr)
    log.debug(f"共匹配到文本列表 {match_txts} {len(txt_positions)} 次")
    return txt_positions


async def match_ocr_txt(ocr_output: types.OCR_Results, match_txts: list[str]) -> types.OCR_Result | None:
    text_positions = await match_ocr_txts(ocr_output, match_txts)
    if len(text_positions) > 0:
        return text_positions[0]


async def ocr_click_txts(page: Page, ocr_output: types.OCR_Results, match_txts: list[str]):
    result = await match_ocr_txt(ocr_output, match_txts)
    if result is not None:
        x, y = get_box_center(result.box)
        await broswer.click_video(page, x, y)
    return result


def get_box_center(box: list):
    x1, y1 = box[0]
    x2, y2 = box[3]
    center_x = (x1 + x2) / 2
    center_y = (y1 + y2) / 2
    return (float(center_x), float(center_y))


def get_cv_box_center(cv_result: types.CV_Result, threshold: float = 0.8):
    if cv_result.score > threshold:
        x = cv_result.x + cv_result.width / 2
        y = cv_result.y + cv_result.height / 2
        return (x, y)


def get_ocr_box_in_range_x(ocr_output: types.OCR_Results, range_x: tuple[float, float]):
    func_result: list[types.OCR_Result] = []
    for ocr in ocr_output:
        txt, box = ocr.txt, ocr.box
        x, y = get_box_center(box)
        range_x_min, range_x_max = range_x
        if range_x_min < x < range_x_max:
            func_result.append(ocr)
    log.debug(f"匹配结果 {func_result}")
    return func_result


async def click_cv_template(page: Page, template_path: str, threshold: float = 0.8):
    cv_result = await img_cv.match_template(str(config.SCREENSHOT_PATH), template_path)
    match_res = get_cv_box_center(cv_result, threshold)
    if match_res:
        log.info(f"在 {match_res} 找到 {template_path}")
        x, y = match_res
        await broswer.click_video(page, x, y)
        return True
