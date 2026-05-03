from playwright.async_api import Page

from ... import broswer, config, push, utils
from ...log import logger as log

# from . import zzz_utils


async def main(page: Page, account: config._GameAccount):
    await goto_game_home(page, account)
    await quick_book_daily_task(page, account)
    await reward_daily_task(page, account)


async def goto_game_home(page: Page, account: config._GameAccount):
    for _ in range(200):
        ocr_output = await utils.get_ocr(page)
        await utils.ocr_click_txts(page, ocr_output, ["开始游戏", "点击进入"])
        if await utils.ocr_click_txts(page, ocr_output, ["列车补给"]):
            log.info("领取月卡奖励")
            await push.screen_shot_and_push(page, account, "月卡奖励")

        if await utils.match_screenshot_cv_template("./core/template/hsr/phone.png"):
            log.info("找到手机图标")
            return True

        if await utils.click_cv_template(page, "./core/template/hsr/close.png"):
            log.info("找到关闭按钮，点击关闭")

        await utils.sleep(page, 1)
    raise Exception("进入游戏超时")


async def open_phone(page: Page):
    for _ in range(15):
        ocr_output = await utils.get_ocr(page)
        if await utils.match_ocr_txt(ocr_output, ["旅情事记"]):
            log.info("当前正在手机界面")
            return True
        else:
            log.info("当前不是手机界面")
            # 刷新截图，防止二次点击，导致切换手机界面
            await broswer.screen_shot(page)
            await utils.click_cv_template(page, "./core/template/hsr/phone.png")
        await utils.sleep(page, 1)
    return False


async def open_entrust(page: Page):
    await open_phone(page)
    await utils.ocr_click_txts_retry(page, ["委托"])


async def open_quick_book(page: Page):
    ocr_result = await utils.get_ocr(page)
    if not await utils.match_ocr_txt(ocr_result, ["星际和平指南"], exact=True):
        await open_phone(page)
        await utils.ocr_click_txts_retry(page, ["指南"])
        await utils.sleep(page, 1)


async def toggle_quick_book_to_scsy_page(page: Page):
    result = await utils.click_cv_template_retry(page, "./core/template/hsr/kjsc_scsy.png")
    # if await switch_quick_book_task(page, "累计消耗120点"):
    #     await utils.sleep(page, 1)
    #     await utils.ocr_click_txts_retry(page, ["培养目标"])
    #     await utils.sleep(page, 1)
    #     return True
    # return False
    return result


async def quick_book_daily_task(page: Page, account: config._GameAccount):
    await daily_entrust(page, account)
    await close(page)
    await start_character_development(page, account)


async def daily_entrust(page: Page, account: config._GameAccount):
    await open_entrust(page)
    for i in range(5):
        ocr_output = await utils.get_ocr(page)
        log.debug(f"第{i+1}次检查领取奖励")
        if await utils.ocr_click_txts(page, ocr_output, ["领取奖励"], exact=True):
            await utils.sleep(page, 2)
            await push.screen_shot_and_push(page, account, "今日委托")
            await confirm_to_receive_reward(page)
            await close(page)
            return True


async def confirm_to_receive_reward(page: Page):
    await utils.ocr_click_txts_retry(page, ["点击空白处关闭"])


async def start_character_development(page: Page, account: config._GameAccount):
    await open_quick_book(page)
    await toggle_quick_book_to_scsy_page(page)

    await utils.ocr_click_txts_retry(page, ["进入"])
    await utils.sleep(page, 2)
    await auto_attack(page, account)
    await close(page)


async def close(page: Page):
    await utils.click_cv_template_retry(page, "./core/template/hsr/close.png")


async def auto_attack(page: Page, account: config._GameAccount):
    add_btn_pos = await utils.click_cv_template_retry(page, "./core/template/hsr/add_number.png")
    if not add_btn_pos:
        # log.error("没有找到增加次数按钮，无法进行自动战斗")
        raise Exception("没有找到增加次数按钮，无法进行自动战斗")

    for i in range(1, 8):
        await broswer.click_video(page, *add_btn_pos)
        log.info(f"第 {i+1} 次点击增加次数按钮")
    await utils.ocr_click_txts_retry(page, ["挑战"], exact=True)
    await utils.sleep(page, 2)
    await utils.ocr_click_txts_retry(page, ["开始挑战"], exact=True)
    await utils.sleep(page, 2)
    for i in range(300):
        ocr_output = await utils.get_ocr(page)
        if await utils.match_ocr_txt(ocr_output, ["单攻", "群攻"]):
            log.info("自动战斗可能未开启，尝试开启自动战斗")
            await utils.click_cv_template_retry(page, "./core/template/hsr/open_auto_attack.png")
        if await utils.match_ocr_txt(ocr_output, ["挑战失败", "挑战成功"]):
            log.info("挑战已结束")
            await push.screen_shot_and_push(page, account, "挑战结果")
            await utils.ocr_click_txts_retry(page, ["退出关卡"])
            # await close(page)
            await goto_game_home(page, account)
            return True
        await utils.sleep(page, 1)


async def reward_mrwt(page: Page, account: config._GameAccount):
    # await open_quick_book(page)
    for i in range(6):
        ocr_output = await utils.get_ocr(page)
        log.debug(f"第 {i+1} 次检查领取每日奖励")
        if await utils.ocr_click_txts(page, ocr_output, ["领取"], exact=True):
            log.info("找到每日委托奖励")
            break
        await utils.sleep(page, 1)
    await utils.sleep(page, 1)

    await push.screen_shot_and_push(page, account, "领取每日委托奖励")


async def reward_daily_task(page: Page, account: config._GameAccount):
    await open_quick_book(page)
    for i in range(4):
        ocr_output = await utils.get_ocr(page)
        log.debug(f"第 {i+1} 次检查领取每日奖励")
        if await utils.ocr_click_txts(page, ocr_output, ["领取"], exact=True):
            log.info("找到每日委托奖励")
    await utils.sleep(page, 1)
    await broswer.screen_shot(page)
    await utils.click_cv_template_retry(page, "./core/template/hsr/daily_task_reward.png")
    await confirm_to_receive_reward(page)
    await push.screen_shot_and_push(page, account, "领取每日委托奖励")


async def switch_quick_book_task(page: Page, task_name: str):
    ocr_output = await utils.get_ocr(page)
    task_box = await utils.match_ocr_txt(ocr_output, [task_name])
    if task_box:
        box = task_box.box
        res = utils.get_ocr_box_in_range_x(
            ocr_output, (box[0][0], box[1][0]))
        return await utils.ocr_click_txts(page, res, ["前往"])
