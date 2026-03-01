import aiohttp
from .config import config


async def push_message(title: str, content: str):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            config.push_url,
            json={
                "token": config.push_token,
                "title": title,
                "content": content,
            },
        ) as response:
            response.raise_for_status()
            return await response.json()