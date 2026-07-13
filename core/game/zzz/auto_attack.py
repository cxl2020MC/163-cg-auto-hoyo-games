import asyncio

from playwright.async_api import Page


from ... import browser, config, utils, img_cv, retry
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


class Auto_Attack:
    def __init__(self, page: Page, account: config._GameAccount):
        self.page = page
        self.account = account
        self.attack_status = Attack_Status.Not_Start
        self.skill_status_color_thresholds: dict[
            Skill_Status, tuple[float, float, float]
        ] = {}

    async def init(self):
        skill_status_img_paths = {
            Skill_Status.Ready: "./core/template/attack/skill_ready.png",
            Skill_Status.Ysg_Ready: "./core/template/attack/skill_ysg_ready.png",
        }
        for type, path in skill_status_img_paths.items():
            color = await img_cv.get_color_in_image(path)
            self.skill_status_color_thresholds[type] = color

    async def auto_attack(self):
        await utils.ocr_click_txts_retry(self.page, ["下一步"], exact=True)
        await utils.sleep(self.page, 1)
        await utils.ocr_click_txts_retry(self.page, ["出战"], exact=True)

        await self.wait_attack_ready()

        while True:
            await self.check_battle_end()
            if self.attack_status == Attack_Status.End:
                log.info("战斗结束，退出自动攻击")
                break
            skill_status = await self.get_skill_status()
            if skill_status in [Skill_Status.Ready, Skill_Status.Ysg_Ready]:
                await self.click_skill()
            else:
                await self.click_attack()

    async def check_battle_end(self):
        ocr_output = await utils.get_ocr(self.page)
        if await utils.match_ocr_txt(ocr_output, ["结果"]):
            log.info("战斗已结束")
            self.attack_status = Attack_Status.End
            return True

    @retry.retry(retry_count=120)
    async def wait_attack_ready(self):
        await browser.screen_shot(self.page)
        if await utils.match_screenshot_cv_template(
            "./core/template/attack/attack.png", 0.65
        ):
            log.info("进入战斗")
            return True

    async def click_skill(self, delay: float = 0):
        # await utils.click_cv_template(page, "./core/template/attack/skill.png", 0.65)
        await browser.get_video_element(self.page).press("e", delay=delay)

    async def click_attack(self, delay: float = 0):
        await utils.click_cv_template(
            self.page, "./core/template/attack/attack.png", 0.65
        )

    async def get_skill_status(self):
        skill_status = await img_cv.classify_state_by_color_range(
            str(config.SCREENSHOT_PATH),
            "./core/template/attack/skill_ready.png",
            self.skill_status_color_thresholds,
        )
        if not skill_status:
            skill_status = Skill_Status.Not_Ready
        log.debug(f"技能状态: {skill_status}")
        return skill_status
