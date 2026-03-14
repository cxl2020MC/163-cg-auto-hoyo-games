import aiohttp
import base64
import traceback
from datetime import datetime
from . import config
from . import broswer
from .log import logger as log
from playwright.async_api import Page

message_list = []

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
        except Exception:
            exc = traceback.format_exc()
            log.error(f"推送消息失败: {exc}")

async def add_message(group_id: int | None, title: str, content: str):
    message_list.append((group_id, title, content))
    log.info(f"消息推送已添加到队列，当前队列长度: {len(message_list)}")

async def send_all_messages():
    log.info(f"开始发送消息队列中的消息，当前队列长度: {len(message_list)}")
    for group_id, title, content in message_list:
        await push_message(group_id, title, content)
    message_list.clear()
    log.info(f"消息队列发送完成，当前队列长度: {len(message_list)}")


async def screen_shot_and_push(page: Page, account: config._Account, content: str):
    log.info("进行消息推送")
    screen_shot = await broswer.screen_shot(page)
    title = f"{account.id} - 游戏脚本截图"
    img_base64 = base64.b64encode(screen_shot).decode("utf-8")
    img_cqcode = f"[CQ:image,file=base64://{img_base64}]"
    time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    content = f"{content}\n{img_cqcode}\n{time_str}"
    await add_message(account.group_id, title, content)