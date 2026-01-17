from rapidocr import RapidOCR
# from rapidocr.utils.output import RapidOCROutput
from rapidocr.main import RapidOCROutput
import asyncio
from dataclasses import dataclass

from . import utils, types, config


engine = RapidOCR()

_image_path = config.SCREENSHOT_PATH



async def ocr_image_old(image_path: str = str(_image_path)) -> RapidOCROutput | None:
    result = await asyncio.to_thread(engine, image_path)
    print(result)
    await asyncio.to_thread(result.vis, str(utils.get_img_file_path("vis_det_rec.jpg")))
    if isinstance(result, RapidOCROutput):
        return result


async def ocr_image(image_path: str = str(_image_path)) -> types.OCR_Results | None:
    result = await asyncio.to_thread(engine, image_path)
    print(result)
    await asyncio.to_thread(result.vis, str(utils.get_img_file_path("vis_det_rec.jpg")))
    if isinstance(result, RapidOCROutput):
        result = to_ocr_result(result)
        return result


def to_ocr_result(result: RapidOCROutput) -> types.OCR_Results | None:
    if not result.txts or result.boxes is None or not result.scores:
        return None
    return map(lambda x: types.OCR_Result(*x), zip(result.txts, result.boxes, result.scores))
