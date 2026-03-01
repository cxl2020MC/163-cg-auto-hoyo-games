import aiohttp



async def push_message(title: str, content: str):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "",
            json={
                "title": title,
                "content": content,
            },
        ) as response: