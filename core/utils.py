from playwright.async_api import Page

from . import browser, config, img_cv, ocr, types, retry
from .log import logger as log


async def sleep(page: Page, seconds: float):
    await page.wait_for_timeout(seconds * 1000)


async def screen_shot_and_ocr(page: Page) -> types.OCR_Results:
    await browser.screen_shot(page)
    ocr_output = await ocr.ocr_image()
    return ocr_output


async def get_ocr(
    page: Page, ocr_output: types.OCR_Results | None = None
) -> types.OCR_Results:
    if ocr_output is None:
        ocr_output = await screen_shot_and_ocr(page)
    return ocr_output


async def match_ocr_txts(
    ocr_output: types.OCR_Results, match_txts: list[str], exact: bool | None = None
):
    txt_positions: list[types.OCR_Result] = []
    for ocr in ocr_output:
        txt, box = ocr.txt, ocr.box
        for match_txt in match_txts:
            if exact:
                if match_txt == txt:
                    log.debug(f"精确匹配到文本 {match_txt}, 位置范围 {box}")
                    txt_positions.append(ocr)
            else:
                if match_txt in txt:
                    log.debug(f"匹配到文本 {match_txt} 于 {txt} , 位置范围 {box}")
                    txt_positions.append(ocr)
    log.debug(f"共匹配到文本列表 {match_txts} {len(txt_positions)} 次")
    return txt_positions


async def match_ocr_txt(
    ocr_output: types.OCR_Results, match_txts: list[str], exact: bool | None = None
) -> types.OCR_Result | None:
    text_positions = await match_ocr_txts(ocr_output, match_txts, exact)
    if len(text_positions) > 0:
        log.debug(f"匹配文本 {match_txts} 到 {len(text_positions)} 个位置，返回第一个")
        return text_positions[0]


async def ocr_click_txts(
    page: Page,
    ocr_output: types.OCR_Results,
    match_txts: list[str],
    exact: bool | None = None,
):
    result = await match_ocr_txt(ocr_output, match_txts, exact)
    if result is not None:
        x, y = get_box_center(result.box)
        await browser.click_video(page, x, y)
    return result


async def ocr_clicks_txts(
    page: Page,
    ocr_output: types.OCR_Results,
    match_txts: list[str],
    exact: bool | None = None,
):
    results = await match_ocr_txts(ocr_output, match_txts, exact)
    for result in results:
        x, y = get_box_center(result.box)
        await browser.click_video(page, x, y)
    return results


async def wait_txts_appear(
    page: Page,
    match_txts: list[str],
    exact: bool | None = None,
    retry_count_type: retry.RetryCountType = retry.RetryCountType.TIME,
    retry_count: int = 30,
    retry_interval: float = 1,
):
    @retry.retry(retry_count_type=retry_count_type, retry_count=retry_count)
    async def wait_once():
        ocr_output = await get_ocr(page)
        result = await match_ocr_txts(ocr_output, match_txts, exact)
        if len(result) > 0:
            return result
        log.info(f"未找到文本 {match_txts}，等待 {retry_interval} 秒后重试")
        await sleep(page, retry_interval)

    return await wait_once()


async def ocr_click_txts_retry_old(
    page: Page,
    match_txts: list[str],
    ocr_output: types.OCR_Results | None = None,
    exact: bool | None = None,
    retry_nums: int = 3,
    retry_interval: float = 1,
):
    for i in range(retry_nums):
        ocr_output = await get_ocr(page, ocr_output)
        result = await ocr_click_txts(page, ocr_output, match_txts, exact)
        if result is not None:
            return result
        ocr_output = None
        log.info(
            f"未找到文本 {match_txts}，等待 {retry_interval} 秒后重试 ({i + 1}/{retry_nums})"
        )
        await sleep(page, retry_interval)
    log.warning(f"尝试了 {retry_nums} 次，仍未找到文本 {match_txts}")
    return None


async def ocr_click_txts_retry(
    page: Page,
    match_txts: list[str],
    ocr_output: types.OCR_Results | None = None,
    exact: bool | None = None,
    retry_type: retry.RetryCountType = retry.RetryCountType.TIME,
    retry_count: int = 30,
    retry_interval: float = 1,
):
    @retry.retry(retry_count_type=retry_type, retry_count=retry_count)
    async def click_once():
        nonlocal ocr_output
        ocr_output = await get_ocr(page, ocr_output)
        result = await ocr_click_txts(page, ocr_output, match_txts, exact)
        if result is not None:
            return result
        ocr_output = None
        log.info(f"未找到文本 {match_txts}，等待 {retry_interval} 秒后重试")
        await sleep(page, retry_interval)

    return await click_once()


def get_box_center(box: list):
    x1, y1 = box[0]
    x2, y2 = box[3]
    center_x = (x1 + x2) / 2
    center_y = (y1 + y2) / 2
    return (float(center_x), float(center_y))


def get_cv_box_center(cv_result: types.CV_Result):
    x = cv_result.x + cv_result.width / 2
    y = cv_result.y + cv_result.height / 2
    return (x, y)


async def match_screenshot_cv_template(template_path: str, threshold: float = 0.75):
    cv_result = await img_cv.match_template(str(config.SCREENSHOT_PATH), template_path)
    if cv_result.score >= threshold:
        log.info(f"在 截图 找到模板 {template_path}")
        return cv_result
    return None


def get_ocr_box_in_range_x(
    ocr_output: types.OCR_Results, range_x: tuple[float, float]
) -> types.OCR_Results:
    func_result: list[types.OCR_Result] = []
    for ocr in ocr_output:
        txt, box = ocr.txt, ocr.box
        x, y = get_box_center(box)
        range_x_min, range_x_max = range_x
        if range_x_min < x < range_x_max:
            func_result.append(ocr)
    log.debug(f"匹配结果 {func_result}")
    return func_result


async def click_cv_template(page: Page, template_path: str, threshold: float = 0.75):
    # cv_result = await img_cv.match_template(str(config.SCREENSHOT_PATH), template_path)
    cv_result = await match_screenshot_cv_template(template_path, threshold)
    if cv_result:
        match_res = get_cv_box_center(cv_result)
        log.info(f"模板 {template_path} 中心在 {match_res}")
        x, y = match_res
        await browser.click_video(page, x, y)
        return (x, y)


async def click_cv_template_retry_old(
    page: Page,
    template_path: str,
    threshold: float = 0.75,
    retry_times: int = 5,
    retry_interval: int = 1,
):
    for i in range(retry_times):
        await browser.screen_shot(page)
        click_cv_result = await click_cv_template(page, template_path, threshold)
        if click_cv_result:
            return click_cv_result
        log.info(
            f"未找到模板 {template_path}，等待 {retry_interval} 秒后重试 ({i + 1}/{retry_times})"
        )
        await sleep(page, retry_interval)
    log.warning(f"尝试了 {retry_times} 次，仍未找到模板 {template_path}")
    return None


async def click_cv_template_retry(
    page: Page,
    template_path: str,
    threshold: float = 0.75,
    retry_count_type: retry.RetryCountType = retry.RetryCountType.TIME,
    retry_count: int = 15,
    retry_interval: int = 1,
):
    @retry.retry(retry_count_type=retry_count_type, retry_count=retry_count)
    async def click_once():
        await browser.screen_shot(page)
        click_cv_result = await click_cv_template(page, template_path, threshold)
        if click_cv_result:
            return click_cv_result
        log.info(f"未找到模板 {template_path}，等待 {retry_interval} 秒后重试")
        await sleep(page, retry_interval)

    return await click_once()


async def drag(
    page: Page, start: tuple[float, float], end: tuple[float, float], steps: int = 20
):
    log.info(f"从 {start} 拖动到 {end}")
    # video_dom = page.locator("video")
    await page.mouse.move(start[0], start[1])
    await page.mouse.down()
    await page.mouse.move(end[0], end[1], steps=steps)
    await page.mouse.up()
    log.info(f"完成拖动")

    return True


async def get_page_size(page: Page):
    video_dom = page.locator("video")
    bounding_box = await video_dom.bounding_box()
    if bounding_box:
        width = bounding_box["width"]
        height = bounding_box["height"]
        log.info(f"页面大小: {width}x{height}")
        return (width, height)
