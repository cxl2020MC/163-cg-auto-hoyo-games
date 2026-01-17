from playwright.async_api import Page

from ... import brswer
from ... import ocr
from ... import utils
from ... import config
from ... import img_cv
from ...log import logger as log


async def main(page: Page):
    for _ in range(1000):
        await brswer.screen_shot(page)
        ocr_output = await ocr.ocr_image()
        if ocr_output is None:
            continue
        await utils.ocr_click_txts(page, ocr_output, ["点击进入", "点击登录", "确定", "今日到账"])
        if await utils.get_ocr_txt_position(ocr_output, "星期"):
            log.info("找到星期")

        cv_result = await img_cv.mach_template(str(config.SCREENSHOT_PATH), "./core/template/tc.png")
        
        cv_box_center = utils.get_cv_box_center(cv_result)
        if cv_box_center:
            log.info(f"在 {cv_box_center} 找到退出按钮")
            x, y = cv_box_center
            await brswer.click_video(page, x, y)

        await page.wait_for_timeout(1000)


async def open_quick_book(page: Page):
    for _ in range(1000):
        await brswer.screen_shot(page)
        ocr_output = await ocr.ocr_image()
        if ocr_output is None:
            continue
        if await utils.get_ocr_txt_position(ocr_output, "QUICK"):
            log.info("当前正在快捷手册页面")

        cv_result = await img_cv.mach_template(str(config.SCREENSHOT_PATH), "./core/template/kjsc.png")
        match_res = utils.get_cv_box_center(cv_result)
        if match_res:
            log.info(f"在 {match_res} 找到返回按钮")
            x, y = match_res
            await brswer.click_video(page, x, y)
