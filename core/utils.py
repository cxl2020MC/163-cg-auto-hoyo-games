from pathlib import Path
from playwright.async_api import Page

from .brswer import click_video


from . import config, types


def get_img_file_path(file_name):
    return Path(config.CHANGE_IMG_DIR, file_name)

SCREENSHOT_PATH = get_img_file_path("screenshot.png")

async def get_ocr_txt_position(ocr_output: types.OCR_Results, match_txt: str):
    for ocr in ocr_output:
        txt, box = ocr.txt, ocr.box
        if match_txt in txt:
            print(f"匹配到文本 {match_txt} 于 {txt} , 位置范围 {box}")
            return (txt, box)


async def ocr_click_txts(page: Page, ocr_output: types.OCR_Results, texts: list[str]):
    for txt in texts:
        result = await get_ocr_txt_position(ocr_output, txt)
        if result is not None:
            _, box = result
            x, y = get_box_center(box)
            await click_video(page, x, y)
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
