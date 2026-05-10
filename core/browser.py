from playwright.async_api import Page

from . import config
from .log import logger as log


async def click_video(page: Page, x: float, y: float):
    log.info(f"点击位置 ({x}, {y})")
    return await page.locator("video").click(position={"x": x, "y": y})


async def screen_shot(page: Page):
    log.info("截图")
    video_dom = page.locator("video")
    return await video_dom.screenshot(path=config.SCREENSHOT_PATH)


