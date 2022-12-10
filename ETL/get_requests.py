import asyncio

import aiohttp

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def fetch(s, url):
    async with s.get(url) as r:
        return False if r.status >= 400 else True


async def fetch_all(s, urls):
    tasks = []
    for url in urls:
        task = asyncio.create_task(fetch(s, url))
        tasks.append(task)
    res = await asyncio.gather(*tasks)
    return res


async def main(urls):
    async with aiohttp.ClientSession() as session:
        responses = await fetch_all(session, urls)

    return responses


def get_responses(urls):
    return asyncio.run(main(urls))
