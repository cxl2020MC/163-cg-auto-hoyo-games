import aiohttp
import base64
from . import config
from . import broswer
from .log import logger as log
from playwright.async_api import Page


async def _push_message(group_id: int, title: str, content: str):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            config.config.push_url,
            json={
                "token": config.config.push_token,
                "group_id": group_id,
                "title": title,
                "content": content,
            },
        ) as response:
            response.raise_for_status()
            return await response.json()
        
async def push_message(group_id: int | None, title: str, content: str):
    if not config.config.push_token or not config.config.push_url:
        return
    if group_id is None:
        return
    else:
        try:
            await _push_message(group_id, title, content)
        except Exception as e:
            log.error(f"推送消息失败: {e}")

async def screen_shot_and_push(page: Page, account: config._Account, content: str):
    log.info("进行消息推送")
    screen_shot = await broswer.screen_shot(page)
    title = f"{account.id} - 游戏截图"
    img_base64 = base64.b64encode(screen_shot).decode("utf-8")
    img_cqcode = f"[CQ:image,file=base64://{img_base64}]"
    content = f"{content}\n{img_cqcode}"
    await push_message(account.group_id, title, content)
    log.info("消息推送完成")