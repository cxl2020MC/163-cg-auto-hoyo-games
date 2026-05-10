import asyncio
import base64
import traceback
from datetime import datetime
from pathlib import Path

import aiohttp
import anyio
from playwright.async_api import Page

from . import browser, config
from .log import logger as log

message_push_tasks = []


async def _onebot_v11_push_message(group_id: int, message: str):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{config.config.push_url}/send_group_msg",
            headers={
                "Authorization": f"Bearer {config.config.push_token}"
            },
            json={
                "token": config.config.push_token,
                "group_id": group_id,
                "message": message,
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
            content = f"{title}\n{content}"
            push_api_return = await _onebot_v11_push_message(group_id, content)
            log.info(f"消息推送成功，返回内容: {push_api_return}")
        except Exception:
            exc = traceback.format_exc()
            log.error(f"推送消息失败: {exc}")

async def add_message(group_id: int | None, title: str, content: str):
    task = asyncio.create_task(push_message(group_id, title, content))
    message_push_tasks.append(task)
    log.info(f"消息推送已添加到队列，当前队列长度: {len(message_push_tasks)}")

async def wait_all_messages_push():
    log.info(f"等待所有后台消息推送完成，当前队列长度: {len(message_push_tasks)}")
    for task in message_push_tasks:
        await task
    message_push_tasks.clear()
    log.info(f"消息队列发送完成，当前队列长度: {len(message_push_tasks)}")


async def screen_shot_and_push(page: Page, account: config._GameAccount, content: str):
    log.info("进行消息推送")
    screen_shot = await browser.screen_shot(page)
    title = f"{account.id} - 游戏脚本截图"
    img_base64 = base64.b64encode(screen_shot).decode("utf-8")
    img_cqcode = f"[CQ:image,file=base64://{img_base64}]"
    time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    content = f"{content}\n{img_cqcode}\n{time_str}"
    await add_message(account.group_id, title, content)

async def push_video(account: config._GameAccount, content: str, video_path: Path):
    log.info("进行视频消息推送")
    title = f"{account.id} - 游戏脚本视频"
    video_base64 = ""
    async with await anyio.open_file(video_path, "rb") as f:
        video_base64 = base64.b64encode(await f.read()).decode("utf-8")
    video_cqcode = f"[CQ:video,file=base64://{video_base64}]"
    time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    content = f"{content}\n{video_cqcode}\n{time_str}"
    await add_message(account.group_id, title, content)