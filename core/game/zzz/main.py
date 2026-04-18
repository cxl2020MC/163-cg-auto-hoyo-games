from playwright.async_api import Page

from . import zzz_utils

from ... import broswer
from ... import ocr
from ... import utils
from ... import config
from ... import push

from ...log import logger as log


async def main(page: Page, account: config._GameAccount):
    await goto_game_home(page, account)
    await quick_book_daily_task(page, account)


async def goto_game_home(page: Page, account: config._GameAccount):
    for _ in range(500):
        ocr_output = await utils.get_ocr(page)
        await utils.ocr_click_txts(page, ocr_output, ["点击进入游戏", "进入游戏", "点击登录", "重新登录"])
        await utils.ocr_click_txts(page, ocr_output, ["确定", "确认"], exact=True)
        if await utils.ocr_click_txts(page, ocr_output, ["今日到账", "惊喜补给"]):
            log.info("领取月卡奖励")
            await push.screen_shot_and_push(page, account, "月卡奖励")
        if await utils.match_ocr_txt(ocr_output, ["网络请求错误"]):
            log.warning("网络请求错误，尝试点击重试")
            await utils.ocr_click_txts(page, ocr_output, ["重试"], exact=True)
        if await utils.match_ocr_txt(ocr_output, ["星期"]):
            log.info("找到星期")
            return True

        await zzz_utils.return_to_streets(page, ocr_output)

        await utils.sleep(page, 1)
    log.error("没有找到星期")
    raise Exception("没有找到星期")


async def open_quick_book(page: Page):
    for _ in range(15):
        ocr_output = await utils.get_ocr(page)
        if await utils.match_ocr_txt(ocr_output, ["QUICK"]):
            log.info("当前正在快捷手册页面")
            if not await utils.match_ocr_txt(ocr_output, ["活跃度"]):
                await utils.ocr_click_txts(page, ocr_output, ["日常"])
                await utils.sleep(page, 2)
            return True
        else:
            log.info("当前不是快捷手册页面")
            # 刷新截图，防止二次点击，导致切换快捷手册页面
            await broswer.screen_shot(page)
            await utils.click_cv_template(page, "./core/template/kjsc.png")
        await utils.sleep(page, 1)
    return False


async def quick_book_daily_task(page: Page, account: config._GameAccount):
    for index in range(3):
        await quick_book_daily_task_main(page, index, account)
    await open_quick_book(page)
    await utils.click_cv_template(page, "./core/template/firework.png")
    await utils.sleep(page, 2)
    await push.screen_shot_and_push(page, account, "烟花任务完成")
    await zzz_utils.click_confirm(page)
    await close_kjsc(page)
    await goto_game_home(page, account)
    await ndcm_reward(page, account)


async def quick_book_daily_task_main(page: Page, index: int, account: config._GameAccount):
    await open_quick_book(page)
    ocr_output = await utils.get_ocr(page)
    match index:
        case 0:
            cofee_box = await utils.match_ocr_txt(ocr_output, ["咖啡"])
            if cofee_box:
                box = cofee_box.box
                res = utils.get_ocr_box_in_range_x(
                    ocr_output, (box[0][0], box[1][0]))
                await utils.ocr_click_txts(page, res, ["前往"])
                await zzz_utils.agree_teleport(page)
                await zzz_utils.wait_for_teleport(page)
                await zzz_utils.click_interaction(page)
                await utils.sleep(page, 3)
                await utils.ocr_click_txts_retry(page, ["一杯汀曼特调"])
                await utils.sleep(page, 2)
                await push.screen_shot_and_push(page, account, "咖啡任务完成")
                await zzz_utils.click_confirm(page)
        case 1:
            divine_box = await utils.match_ocr_txt(ocr_output, ["占卜"])
            if divine_box:
                box = divine_box.box
                res = utils.get_ocr_box_in_range_x(
                    ocr_output, (box[0][0], box[1][0]))
                await utils.ocr_click_txts(page, res, ["前往"])
                await zzz_utils.agree_teleport(page)
                await zzz_utils.wait_for_teleport(page)
                await zzz_utils.click_interaction(page)
                await utils.sleep(page, 3)
                for _ in range(10):
                    ocr_output = await utils.get_ocr(page)
                    if await utils.ocr_click_txts(page, ocr_output, ["开", "開"]):
                        break
                await utils.sleep(page, 2)
                for _ in range(10):
                    ocr_output = await utils.get_ocr(page)
                    if await utils.match_ocr_txt(ocr_output, ["滑动屏幕"]):
                        page_size = await utils.get_page_size(page)
                        if page_size:
                            await utils.drag(page, (page_size[0]*0.1, page_size[1]/2), (page_size[0]*0.9, page_size[1]/2))
                    else:
                        break
                await zzz_utils.click_confirm(page)
                await utils.sleep(page, 2)
                await push.screen_shot_and_push(page, account, "占卜任务完成")
                await zzz_utils.click_confirm(page)
                await goto_game_home(page, account)
        case 2:
            operate_box = await utils.match_ocr_txt(ocr_output, ["录像店经营"])
            if operate_box:
                box = operate_box.box
                res = utils.get_ocr_box_in_range_x(
                    ocr_output, (box[0][0], box[1][0]))
                await utils.ocr_click_txts(page, res, ["前往"])
                await zzz_utils.agree_teleport(page)
                await zzz_utils.wait_for_teleport(page)
                # 点击交互按钮
                await zzz_utils.click_interaction(page)
                await utils.sleep(page, 3)
                await utils.ocr_click_txts_retry(page, ["查看经营状况"])
                await utils.sleep(page, 3)
                await push.screen_shot_and_push(page, account, "开始录像店任务")
                await utils.click_cv_template_retry(page, "./core/template/tc2.png")
                await utils.sleep(page, 1)
                await utils.click_cv_template_retry(page, "./core/template/xzxcy.png")
                await zzz_utils.click_confirm(page)
                await utils.click_cv_template_retry(page, "./core/template/xzxclxd.png")
                await utils.sleep(page, 1)
                await utils.ocr_click_txts_retry(page, ["推荐上架"])
                await utils.sleep(page, 1)
                await utils.ocr_click_txts_retry(page, ["开始营业"])
                await utils.sleep(page, 1)
                await zzz_utils.click_confirm(page)
                await utils.sleep(page, 1)
                await push.screen_shot_and_push(page, account, "录像店任务完成")
                await zzz_utils.click_confirm(page)
                await goto_game_home(page, account)

        case _:
            log.error("无法识别的任务id")
            raise Exception("无法识别的任务id")


async def open_ndcm(page: Page):
    for _ in range(15):
        ocr_output = await utils.get_ocr(page)
        if await utils.match_ocr_txt(ocr_output, ["丽都城募"]):
            log.info("当前正在丽都城募页面")
            if not await utils.ocr_click_txts(page, ocr_output, ["开启丽都城募"]):
                return True
        else:
            log.info("当前不是丽都城募页面")
            await utils.click_cv_template(page, "./core/template/ndcm.png", threshold=0.7)
        await utils.sleep(page, 1)
    return False


async def ndcm_reward(page: Page, account: config._GameAccount):
    await open_ndcm(page)
    await utils.ocr_click_txts_retry(page, ["成长任务"])
    await utils.sleep(page, 2)
    await utils.ocr_click_txts_retry(page, ["全部领取"])
    await utils.sleep(page, 2)
    await push.screen_shot_and_push(page, account, "丽都城募奖励")


async def close_kjsc(page: Page):
    return await utils.click_cv_template_retry(page, "./core/template/kjsc_tc.png")
