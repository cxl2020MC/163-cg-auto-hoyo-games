from pathlib import Path
from playwright.async_api import Page

from . import brswer


from . import config, types, img_cv
from .log import logger as log


def get_img_file_path(file_name):
    return Path(config.CHANGE_IMG_DIR, file_name)


SCREENSHOT_PATH = get_img_file_path("screenshot.png")


async def match_ocr_txts(ocr_output: types.OCR_Results, match_txt: str):
    txt_positions: list[types.OCR_Result] = []
    for ocr in ocr_output:
        txt, box = ocr.txt, ocr.box
        if match_txt in txt:
            log.debug(f"匹配到文本 {match_txt} 于 {txt} , 位置范围 {box}")
            txt_positions.append(ocr)
    log.debug(f"共匹配到文本 {match_txt} {len(txt_positions)} 次")
    return txt_positions


async def match_ocr_txt(ocr_output: types.OCR_Results, match_txt: str) -> types.OCR_Result | None:
    text_positions = await match_ocr_txts(ocr_output, match_txt)
    if len(text_positions) > 0:
        return text_positions[0]


async def ocr_click_txts(page: Page, ocr_output: types.OCR_Results, texts: list[str]):
    for txt in texts:
        result = await match_ocr_txt(ocr_output, txt)
        if result is not None:
            x, y = get_box_center(result.box)
            await brswer.click_video(page, x, y)
    return ocr_output


def get_box_center(list):
    x1, y1 = list[0]
    x2, y2 = list[3]
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


async def cilck_cv_template(page: Page, template_path: str, threshold: float = 0.8):
    cv_result = await img_cv.mach_template(str(config.SCREENSHOT_PATH), template_path)
    match_res = get_cv_box_center(cv_result, threshold)
    if match_res:
        log.info(f"在 {match_res} 找到 {template_path}")
        x, y = match_res
        await brswer.click_video(page, x, y)
        return True
