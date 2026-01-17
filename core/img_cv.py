import cv2
import asyncio

from . import types
from .log import logger as log

# def img_cv(img_path: str, template_path: str):
#     img = cv2.imread(img_path, cv2.IMREAD_COLOR_BGR)
#     template_img = cv2.imread(template_path, cv2.IMREAD_COLOR_BGR)
#     res = cv2.matchTemplate(img, template_img, cv2.TM_CCOEFF_NORMED)
#     return res


async def mach_template(img_path: str, template_path: str):
    img = await asyncio.to_thread(cv2.imread, img_path, cv2.IMREAD_COLOR_BGR)
    template_img = await asyncio.to_thread(cv2.imread, template_path, cv2.IMREAD_COLOR_BGR)
    assert img is not None
    assert template_img is not None
    res = cv2.matchTemplate(img, template_img, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    height, width = template_img.shape[:2]
    x, y = max_loc
    result = types.CV_Result(x=x, y=y, width=width, height=height, score=max_val)
    log.debug(f"图片模板匹配结果：{result}")
    return result


if __name__ == '__main__':
    img_path = r".\img\screenshot.png"
    template_path = r".\core\template\tc.png"
    # img = cv2.imread(img_path, cv2.IMREAD_COLOR_BGR)
    # template_img = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
    res = asyncio.run(mach_template(img_path, template_path))
    print(res)
    # threshold = 0.8
    # loc = np.where( res >= threshold)
    # for pt in zip(*loc[::-1]):
    #     cv2.rectangle(img, pt, (pt[0] + template_img.shape[1], pt[1] + template_img.shape[0]), (0,0,255), 2)
    # cv2.imwrite('res.png', img)
    # print(res)
    # print(loc)
