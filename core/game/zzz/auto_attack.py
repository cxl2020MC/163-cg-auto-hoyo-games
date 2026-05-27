import asyncio

from playwright.async_api import Page



from ... import browser, config, ocr, push, utils
from ...log import logger as log

from enum import StrEnum

class Attack_Status(StrEnum):
    Not_Start = "未开始"
    Attacking = "战斗中"
    End = "战斗结束"

class Skill_Status(StrEnum):
    Not_Ready = "未准备好"
    Ready = "准备好"
    Ysg_Ready = "叶瞬光-准备好"


async def auto_attack(page: Page, account: config._GameAccount):
    await utils.ocr_click_txts_retry(page, ["下一步"], exact=True)
    await utils.sleep(page, 1)
    await utils.ocr_click_txts_retry(page, ["出战"], exact=True)
    for i in range(61):
        if await utils.match_screenshot_cv_template("./core/template/attack/attack.png", 0.65):
            log.info("进入战斗")
            break
        log.info(f"等待进入战斗...({i}/60)")
        await utils.sleep(page, 1)
    # await push.screen_shot_and_push(page, account, "战斗开始")
    attack_status = Attack_Status.Not_Start

    async def wait_battle_end():
        for _ in range(600):
            ocr_output = await utils.get_ocr(page)
            if await utils.match_ocr_txt(ocr_output, ["结果"]):
                log.info("战斗已结束")
                attack_status = Attack_Status.End

    asyncio.create_task(wait_battle_end())

    while True:
        if attack_status == Attack_Status.End:
            break

        await browser.screen_shot(page)
        


async def click_skill(page: Page, delay: float = 0):
    # await utils.click_cv_template(page, "./core/template/attack/skill.png", 0.65)
    await browser.get_video_element(page).press("e", delay=delay)


async def get_skill_status(page: Page) -> Skill_Status:
    if await utils.match_screenshot_cv_template("./core/template/attack/skill.png"):
        game_status = Skill_Status.Ready
    elif await utils.match_screenshot_cv_template("./core/template/attack/skill_ysg.png"):
        game_status = Skill_Status.Ysg_Ready
    else:
        game_status = Skill_Status.Not_Ready
    log.info(f"当前技能状态为: {game_status}")
    return game_status
