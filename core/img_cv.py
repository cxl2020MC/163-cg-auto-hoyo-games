import cv2
import asyncio
import numpy as np

from . import types
from .log import logger as log

# def img_cv(img_path: str, template_path: str):
#     img = cv2.imread(img_path, cv2.IMREAD_COLOR_BGR)
#     template_img = cv2.imread(template_path, cv2.IMREAD_COLOR_BGR)
#     res = cv2.matchTemplate(img, template_img, cv2.TM_CCOEFF_NORMED)
#     return res


async def match_template(img_path: str, template_path: str, mask_path: str | None = None) -> types.CV_Result:
    img = await asyncio.to_thread(cv2.imread, img_path, cv2.IMREAD_COLOR_BGR)
    template_img = await asyncio.to_thread(cv2.imread, template_path, cv2.IMREAD_COLOR_BGR)
    mask_img = await asyncio.to_thread(cv2.imread, mask_path, cv2.IMREAD_GRAYSCALE) if mask_path else None
    assert img is not None
    assert template_img is not None
    res = cv2.matchTemplate(
        img, template_img, cv2.TM_CCOEFF_NORMED, mask=mask_img)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    height, width = template_img.shape[:2]
    x, y = max_loc
    result = types.CV_Result(x=x, y=y, width=width,
                             height=height, score=max_val)
    log.debug(f"图片 {template_path} 模板匹配结果：{result}")
    await asyncio.to_thread(cv2.rectangle, img, max_loc, (max_loc[0] + width, max_loc[1] + height), (0, 0, 255), 1)
    await asyncio.to_thread(cv2.imwrite, 'img/cv_res.png', img)
    return result


async def mach_template2(img_path: str, template_path: str):
    img = await asyncio.to_thread(cv2.imread, img_path, cv2.IMREAD_COLOR_BGR)
    template_img = await asyncio.to_thread(cv2.imread, template_path, cv2.IMREAD_COLOR_BGR)
    assert img is not None
    assert template_img is not None
    res = cv2.matchTemplate(img, template_img, cv2.TM_CCOEFF_NORMED)
    threshold = 0.8
    loc = np.where(res >= threshold)
    for pt in zip(*loc[::-1]):
        cv2.rectangle(img, pt, (pt[0] + template_img.shape[1],
                      pt[1] + template_img.shape[0]), (0, 0, 255), 2)
    cv2.imwrite('res.png', img)
    # height, width = template_img.shape[:2]
    # x, y = max_loc
    # result = types.CV_Result(x=x, y=y, width=width, height=height, score=max_val)
    # log.debug(f"图片模板匹配结果：{result}")
    # return result


async def generate_mask_image(img_path: str, output_path: str):
    img = await asyncio.to_thread(cv2.imread, img_path, cv2.IMREAD_COLOR_BGR)
    assert img is not None
    masked_img = cv2.threshold(cv2.cvtColor(
        img, cv2.COLOR_BGR2GRAY), 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    await asyncio.to_thread(cv2.imwrite, output_path, masked_img)

if __name__ == '__main__':
    img_path = r"img\screenshot.png"
    template_path = r"core\template\hsr\phone.png"
    mask_path = r"core\template\tc_mask.png"
    # img = cv2.imread(img_path, cv2.IMREAD_COLOR_BGR)
    # template_img = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
    asyncio.run(generate_mask_image(template_path, mask_path))
    res = asyncio.run(match_template(img_path, template_path, mask_path))
    print(res)
    # threshold = 0.8
    # loc = np.where( res >= threshold)
    # for pt in zip(*loc[::-1]):
    #     cv2.rectangle(img, pt, (pt[0] + template_img.shape[1], pt[1] + template_img.shape[0]), (0,0,255), 2)
    # cv2.imwrite('res.png', img)
    # print(res)
    # print(loc)
