import asyncio

import cv2
import numpy as np

from . import types
from .log import logger as log

# def img_cv(img_path: str, template_path: str):
#     img = cv2.imread(img_path, cv2.IMREAD_COLOR_BGR)
#     template_img = cv2.imread(template_path, cv2.IMREAD_COLOR_BGR)
#     res = cv2.matchTemplate(img, template_img, cv2.TM_CCOEFF_NORMED)
#     return res


async def match_template(img_path: str, template_path: str, mask_path: str | None = None, *, flag: int = cv2.IMREAD_COLOR, method: int = cv2.TM_CCOEFF_NORMED) -> types.CV_Result:
    img = await asyncio.to_thread(cv2.imread, img_path, flag)
    template_img = await asyncio.to_thread(cv2.imread, template_path, flag)
    mask_img = await asyncio.to_thread(cv2.imread, mask_path, cv2.IMREAD_GRAYSCALE) if mask_path else None
    assert img is not None
    assert template_img is not None
    cv2.TM_CCORR_NORMED
    res = cv2.matchTemplate(
        img, template_img, method, mask=mask_img)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    height, width = template_img.shape[:2]
    x, y = max_loc
    result = types.CV_Result(x=x, y=y, width=width,
                             height=height, score=max_val)
    log.debug(f"图片 {template_path} 模板匹配结果：{result}")
    await asyncio.to_thread(cv2.rectangle, img, max_loc, (max_loc[0] + width, max_loc[1] + height), (0, 0, 255), 1)
    await asyncio.to_thread(cv2.imwrite, 'img/cv_res.png', img)
    return result

async def match_template_v2(img: cv2.typing.MatLike, template_img: cv2.typing.MatLike, mask_img: cv2.typing.MatLike | None = None, *, method: int = cv2.TM_CCOEFF_NORMED) -> types.CV_Result:
    res = cv2.matchTemplate(
        img, template_img, method, mask=mask_img)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    height, width = template_img.shape[:2]
    x, y = max_loc
    result = types.CV_Result(x=x, y=y, width=width,
                             height=height, score=max_val)
    log.debug(f"图片 {template_path} 模板匹配结果：{result}")
    await asyncio.to_thread(cv2.rectangle, img, max_loc, (max_loc[0] + width, max_loc[1] + height), (0, 0, 255), 1)
    await asyncio.to_thread(cv2.imwrite, 'img/cv_res.png', img)
    return result


async def match_template2(img_path: str, template_path: str, mask_path: str | None = None):
    img = await asyncio.to_thread(cv2.imread, img_path, cv2.IMREAD_COLOR_BGR)
    template_img = await asyncio.to_thread(cv2.imread, template_path, cv2.IMREAD_COLOR_BGR)
    mask_img = await asyncio.to_thread(cv2.imread, mask_path, cv2.IMREAD_GRAYSCALE) if mask_path else None

    assert img is not None
    assert template_img is not None
    res = cv2.matchTemplate(
        img, template_img, cv2.TM_CCOEFF_NORMED, mask=mask_img)
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


async def load_image(img_path: str, flag: int = cv2.IMREAD_COLOR):
    img = await asyncio.to_thread(cv2.imread, img_path, flag)
    assert img is not None
    return img


async def load_cv_img(img_path: str, template_path: str, mask_path: str | None = None, *, flag: int = cv2.IMREAD_COLOR):
    img = await asyncio.to_thread(cv2.imread, img_path, flag)
    template_img = await asyncio.to_thread(cv2.imread, template_path, flag)
    mask_img = await asyncio.to_thread(cv2.imread, mask_path, cv2.IMREAD_GRAYSCALE) if mask_path else None
    assert img is not None
    assert template_img is not None
    return img, template_img, mask_img

# async def detect_skill_by_shape(img_path: str, template_path: str) -> tuple[bool, int, int]:
#     """
#     基于形状检测技能位置，忽略颜色差异
#     返回: (是否找到, x坐标, y坐标)
#     """
#     img = await asyncio.to_thread(cv2.imread, img_path, cv2.IMREAD_COLOR_BGR)
#     template_img = await asyncio.to_thread(cv2.imread, template_path, cv2.IMREAD_COLOR_BGR)
#     assert img is not None
#     assert template_img is not None

#     # 转灰度后进行边缘检测
#     img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#     template_gray = cv2.cvtColor(template_img, cv2.COLOR_BGR2GRAY)

#     # 使用高斯模糊提高鲁棒性
#     img_gray = cv2.GaussianBlur(img_gray, (5, 5), 0)
#     template_gray = cv2.GaussianBlur(template_gray, (5, 5), 0)

#     # 模板匹配
#     res = cv2.matchTemplate(img_gray, template_gray, cv2.TM_CCOEFF_NORMED)
#     min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

#     threshold = 0.7  # 调整这个值以平衡准确性和识别率
#     found = max_val >= threshold

#     if found:
#         log.debug(f"技能位置检测: 得分={max_val:.3f}, 坐标=({max_loc[0]}, {max_loc[1]})")
#     else:
#         log.debug(f"未检测到技能 (最高得分={max_val:.3f})")

#     return found, max_loc[0], max_loc[1]

# cv2.typing.MatLike


async def get_color_in_roi(img: cv2.typing.MatLike, template_img: cv2.typing.MatLike):
    """
    获取ROI的主要颜色（平均颜色）
    返回: (B, G, R) 三通道平均值
    """
    # img = await asyncio.to_thread(cv2.imread, img_path, cv2.IMREAD_COLOR_BGR)
    # template_img = await asyncio.to_thread(cv2.imread, template_path, cv2.IMREAD_COLOR_BGR)
    # assert img is not None
    # assert template_img is not None

    cv_result = await match_template_v2(img, template_img)
    if not cv_result:
        return None

    h, w = cv_result.height, cv_result.width
    roi = img[cv_result.y:cv_result.y+h, cv_result.x:cv_result.x+w]

    # 计算ROI的平均颜色
    avg_color = cv2.mean(roi)[:3]  # 获取BGR三通道
    return avg_color


async def classify_state_by_color(img_path: str, template_path: str, color_ranges: dict[str, tuple]) -> str | None:
    """
    根据颜色分类状态
    color_ranges: {"未准备好": (B_min, G_min, R_min, B_max, G_max, R_max), ...}
    返回: 状态名称 或 None
    """

    img, template_img, _ = await load_cv_img(img_path, template_path)
    color = await get_color_in_roi(img, template_img)
    if color is None:
        return None

    b, g, r = color

    # 检查每个颜色范围
    for state_name, (b_min, g_min, r_min, b_max, g_max, r_max) in color_ranges.items():
        if b_min <= b <= b_max and g_min <= g <= g_max and r_min <= r <= r_max:
            log.info(f"技能状态识别: {state_name}, 颜色=BGR({b},{g},{r})")
            return state_name

    log.warning(f"未能识别的颜色: BGR({b},{g},{r})")
    return None

async def classify_state_by_color_v2(img_path: str, template_path: str, color_ranges: dict[str, tuple[tuple[int, int], tuple[int, int], tuple[int, int]]]) -> str | None:
    """
    根据颜色分类状态
    color_ranges: {"未准备好": (B_min, B_max), (G_min, G_max), (R_min, R_max)}, ...}
    返回: 状态名称 或 None
    """

    img, template_img, _ = await load_cv_img(img_path, template_path)
    color = await get_color_in_roi(img, template_img)
    if color is None:
        return None

    b, g, r = color

    # 检查每个颜色范围
    for state_name, (b_range, g_range, r_range) in color_ranges.items():
        b_min, b_max = b_range
        g_min, g_max = g_range
        r_min, r_max = r_range

        if b_min <= b <= b_max and g_min <= g <= g_max and r_min <= r <= r_max:
            log.info(f"技能状态识别: {state_name}, 颜色=BGR({b},{g},{r})")
            return state_name

    log.warning(f"未能识别的颜色: BGR({b},{g},{r})")
    return None

if __name__ == '__main__':
    img_path = r"img\screenshot copy 20.png"
    template_path = r"core\template\attack\skill_ysg.png"
    mask_path = r"core\template\tc_mask.png"
    # img = cv2.imread(img_path, cv2.IMREAD_COLOR_BGR)
    # template_img = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
    # asyncio.run(generate_mask_image(template_path, mask_path))
    # res = asyncio.run(match_template(img_path, template_path, mask_path))
    # for i in [cv2.TM_CCOEFF_NORMED, cv2.TM_CCORR_NORMED, cv2.TM_SQDIFF_NORMED, cv2.TM_CCOEFF, cv2.TM_CCORR, cv2.TM_SQDIFF]:
    #     res = asyncio.run(match_template(img_path, template_path, method=i))
    #     print(f"Method {i}: {res}")
    async def test_color_in_roi():
        img, template_img, _ = await load_cv_img(img_path, template_path)
        return await get_color_in_roi(img, template_img)
    res = asyncio.run(test_color_in_roi())
    print(res)
    # threshold = 0.8
    # loc = np.where( res >= threshold)
    # for pt in zip(*loc[::-1]):
    #     cv2.rectangle(img, pt, (pt[0] + template_img.shape[1], pt[1] + template_img.shape[0]), (0,0,255), 2)
    # cv2.imwrite('res.png', img)
    # print(res)
    # print(loc)
