import asyncio
from playwright.async_api import async_playwright

from rapidocr import RapidOCR
from rapidocr.utils.output import RapidOCROutput

engine = RapidOCR()




async def main():
    async with async_playwright() as p:
        # browser = await p.chromium.launch(headless=False, channel="msedge")
        browser = await p.chromium.launch_persistent_context("./data/browser_data/1", headless=False, channel="msedge")
        page = await browser.new_page()
        # await page.goto("https://cg.163.com")
        await page.goto("https://cg.163.com/?action_link=cloudgaming%3A%2F%2Fstartgame%3Fgame_code%3Djql_gjf%26game_open_action%3Dthis_game")

        print(await page.title())
        # await page.get_by_role("button").click()
        # await page.get_by_role("banner").get_by_text("登录").dispatch_event('click')
        if await page.get_by_text("登录").is_visible():
            await page.get_by_placeholder("手机号").fill("13725027949")
            await page.get_by_text("密码登录").first.dispatch_event('click')
            await page.get_by_placeholder("密码").fill("Qq365538151")
            await page.get_by_role("button", name="登录").click()
            # await page.get_by_role("link", name="同意").click()
            await page.get_by_text("同意", exact=True).click()
            await page.get_by_role("button", name="登录").click()

            await page.wait_for_timeout(10000)

        video_dom = page.locator("video")
        print(video_dom)
        keybord_dom = page.locator("videoInput")
        for i in range(1000):
            # await video_dom.screenshot(path="screenshot.png")
            img_url = "screenshot.png"
            await page.screenshot(path=img_url)
            result = engine(img_url, use_det=True, use_cls=True, use_rec=True)
            print(result)
            if isinstance(result, RapidOCROutput):
                if not result.txts: 
                    continue
                elif result.boxes is None: 
                    continue
                print(list(zip(result.txts, result.boxes)))
                for txt in result.txts:
                    if "点击" in txt:
                        print("点击屏幕")
                        await video_dom.click(position={"x": 100, "y": 100})
            result.vis("vis_det_rec.jpg")
            await page.wait_for_timeout(1000)


        await page.wait_for_timeout(100000)
        await browser.close()



if __name__ == "__main__":
    asyncio.run(main())

