from playwright.async_api import Page

from ... import browser, config, push, utils, retry
from ...log import logger as log
from . import zzz_utils, auto_attack


async def main(page: Page, account: config._GameAccount):
    await goto_game_home(page, account)
    # await pyjs(page, account)
    await quick_book_daily_task(page, account)
    await goto_game_home(page, account)
    await ndcm_reward(page, account)

# @retry.retry(retry_count=600, raise_exception=True, raise_exception_error=Exception("没有找到星期，进入游戏超时"))
async def goto_game_home(page: Page, account: config._GameAccount):
    for i in range(300):
        log.debug(f"第 {i} 次, 检查街区")
        ocr_output = await utils.get_ocr(page)
        await utils.ocr_click_txts(page, ocr_output, ["点击进入游戏", "进入游戏", "点击登录", "重新登录"])
        await utils.ocr_click_txts(page, ocr_output, ["确定", "确认"], exact=True)
        if await utils.ocr_click_txts(page, ocr_output, ["今日到账", "惊喜补给"]):
            log.info("领取月卡奖励")
            await push.screen_shot_and_push(page, account, "月卡奖励")
        elif await utils.match_ocr_txt(ocr_output, ["网络请求错误"]):
            log.warning("网络请求错误，尝试点击重试")
            await utils.ocr_click_txts(page, ocr_output, ["重试"], exact=True)
        elif await utils.ocr_click_txts(page, ocr_output, ["用户协议和隐私政策"], exact=True):
            log.info("尝试同意用户协议和隐私政策")
            for _ in range(3):
                await utils.click_cv_template_retry(page, "./core/template/agree_yhxy.png")
                await utils.sleep(page, 1)
            await utils.ocr_click_txts_retry(page, ["接受"], exact=True)
        if await zzz_utils.is_in_street(ocr_output):
            log.info("已到达街区")
            return True

        await zzz_utils.return_to_streets(page, ocr_output)
    
    raise Exception("找不到街区")


@retry.retry(raise_exception=True, raise_exception_error=Exception("打开快捷手册超时"))
async def open_quick_book(page: Page, quick_book_tab: str | None = None):
    ocr_output = await utils.get_ocr(page)
    if await utils.match_ocr_txt(ocr_output, ["QUICK"]):
    # if len(await utils.match_ocr_txts(ocr_output, ["日常", "目标", "训练"], exact=True)) >= 2:
        log.info("当前正在快捷手册页面")
        if not await utils.match_ocr_txt(ocr_output, ["活跃度"]):
            await utils.ocr_click_txts(page, ocr_output, ["日常"])
            await utils.sleep(page, 1)
            await browser.screen_shot(page)
        return True
    else:
        log.info("当前不是快捷手册页面")
        # 刷新截图，防止二次点击，导致切换快捷手册页面
        await browser.screen_shot(page)
        await utils.click_cv_template(page, "./core/template/kjsc.png")


async def quick_book_daily_task(page: Page, account: config._GameAccount):
    for index in range(3):
        await quick_book_daily_task_main(page, index, account)

    await open_quick_book(page)
    # await utils.click_cv_template_retry(page, "./core/template/firework.png", threshold=0.65)
    # await utils.click_cv_template_retry(page, "./core/template/firework2.png")
    await utils.ocr_click_txts_retry(page, ["今日最大活跃度"], exact=True)

    await utils.sleep(page, 2)
    await push.screen_shot_and_push(page, account, "烟花任务完成")
    await zzz_utils.click_confirm(page)
    await close_kjsc(page)
    await utils.sleep(page, 2)


async def quick_book_daily_task_main(page: Page, index: int, account: config._GameAccount):
    match index:
        case 0:
            account_game_config = config.get_account_game_config(
                account, config.ZZZGameConfig)
            if account_game_config and not account_game_config.cofee:
                log.info("跳过咖啡任务")
                return
            else:
                await quick_book_daily_task_coffee(page, account)

        case 1:
            # await quick_book_daily_task_divine(page, account)
            await quick_book_daily_task_cookie(page, account)
        case 2:
            await quick_book_daily_task_operate(page, account)
        case _:
            log.error("无法识别的任务id")
            raise Exception("无法识别的任务id")


async def quick_book_daily_task_coffee(page: Page, account: config._GameAccount):
    await open_quick_book(page)
    ocr_output = await utils.get_ocr(page)
    cofee_box = await utils.match_ocr_txt(ocr_output, ["次咖啡"])
    if cofee_box:
        box = cofee_box.box
        res = utils.get_ocr_box_in_range_x(
            ocr_output, (box[0][0], box[1][0]))
        await utils.ocr_click_txts(page, res, ["前往"])
        # await zzz_utils.agree_teleport(page)
        await zzz_utils.wait_for_teleport(page)
        await zzz_utils.click_interaction(page)
        await utils.sleep(page, 3)
        await utils.ocr_click_txts_retry(page, ["喝点什么"])
        await utils.sleep(page, 1)
        await utils.ocr_click_txts_retry(page, ["汀曼特调"])
        await utils.sleep(page, 1)
        await utils.ocr_click_txts_retry(page, ["跳过"])
        await utils.sleep(page, 2)
        await push.screen_shot_and_push(page, account, "咖啡任务完成")
        await zzz_utils.click_confirm(page)


async def quick_book_daily_task_divine(page: Page, account: config._GameAccount):
    await open_quick_book(page)
    ocr_output = await utils.get_ocr(page)
    divine_box = await utils.match_ocr_txt(ocr_output, ["次占卜"])
    if divine_box:
        box = divine_box.box
        res = utils.get_ocr_box_in_range_x(
            ocr_output, (box[0][0], box[1][0]))
        await utils.ocr_click_txts(page, res, ["前往"])
        # await zzz_utils.agree_teleport(page)
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


async def quick_book_daily_task_cookie(page: Page, account: config._GameAccount):
    await open_quick_book(page)
    ocr_output = await utils.get_ocr(page)
    cookie_box = await utils.match_ocr_txt(ocr_output, ["抽取饼铺盲盒"])
    if cookie_box:
        box = cookie_box.box
        res = utils.get_ocr_box_in_range_x(
            ocr_output, (box[0][0], box[1][0]))
        await utils.ocr_click_txts(page, res, ["前往"])
        # await zzz_utils.agree_teleport(page)
        await zzz_utils.wait_for_teleport(page)
        await zzz_utils.click_interaction(page)
        await utils.sleep(page, 3)
        await utils.click_cv_template_retry(page, "./core/template/zzz/daily/cookie.png")
        await utils.sleep(page, 3)
        for i in range(5):
            # ocr_output = await utils.get_ocr(page)
            # if await utils.match_ocr_txts(ocr_output, ["点击盲盒"]):
            #     break
            # await browser.click_video(page, x / 2, y / 2)
            ocr_output = await utils.get_ocr(page)
            if not await utils.ocr_click_txts(page, ocr_output, ["点击盲盒"]):
                break
            await utils.sleep(page, 1)

        await zzz_utils.click_confirm(page)
        await utils.sleep(page, 1)
        await zzz_utils.click_confirm(page)
        await goto_game_home(page, account)


async def quick_book_daily_task_operate(page: Page, account: config._GameAccount):
    await open_quick_book(page)
    ocr_output = await utils.get_ocr(page)
    operate_box = await utils.match_ocr_txt(ocr_output, ["今日录像店经营"])
    if operate_box:
        box = operate_box.box
        res = utils.get_ocr_box_in_range_x(
            ocr_output, (box[0][0], box[1][0]))
        await utils.ocr_click_txts(page, res, ["前往"])
        # await zzz_utils.agree_teleport(page)
        await zzz_utils.wait_for_teleport(page)
        # 切换目标
        await browser.get_video_element(page).press("d+w")
        await utils.sleep(page, 1)
        # 点击交互按钮
        await zzz_utils.click_interaction(page)
        await utils.sleep(page, 3)
        await utils.ocr_click_txts_retry(page, ["看看今日的经营"])
        await utils.sleep(page, 1)
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


async def open_ndcm(page: Page):
    for _ in range(15):
        ocr_output = await utils.get_ocr(page)
        if await utils.match_ocr_txt(ocr_output, ["丽都城募"]):
            log.info("当前正在丽都城募页面")
            if not await utils.ocr_click_txts(page, ocr_output, ["开启丽都城募"]):
                return True
        else:
            log.info("当前不是丽都城募页面")
            await utils.click_cv_template(page, "./core/template/ndcm.png")
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


async def open_function(page: Page, function_name: str):
    if await utils.click_cv_template_retry(page, "./core/template/kjgj.png"):
        await utils.sleep(page, 1)
        await utils.ocr_click_txts_retry(page, [function_name], exact=True)
        await utils.sleep(page, 1)
    #     return True
    # else:
    #     log.warning(f"没有找到 {function_name} 按钮")
    #     return False


async def open_xunlian(page: Page):
    await open_quick_book(page)
    await utils.ocr_click_txts_retry(page, ["训练"])
    await utils.sleep(page, 1)


async def pyjs(page: Page, account: config._GameAccount):
    await open_xunlian(page)
    await utils.ocr_click_txts_retry(page, ["前往"])
    await zzz_utils.agree_teleport(page)
    # await zzz_utils.wait_for_teleport(page)
    for i in range(60):
        ocr_output = await utils.get_ocr(page)
        # game_status = await check_game_status(page, ocr_output)
        # if game_status == Game_Status.Street:
        if await utils.match_ocr_txt(ocr_output, ["挑战等级"]):
            log.info("已到达目的地")
            break
        await utils.sleep(page, 1)

        Auto_Attack = auto_attack.Auto_Attack(page, account)
        await Auto_Attack.init()
        await Auto_Attack.auto_attack()
