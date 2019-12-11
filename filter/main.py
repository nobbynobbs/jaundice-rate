import aiohttp
import asyncio


async def fetch(session, url):
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.text()


async def fetch_article(url: str):
    async with aiohttp.ClientSession() as session:
        html = await fetch(session, url)
        print(html)


def main():
    asyncio.run(fetch_article('http://example.com'))


if __name__ == '__main__':
    main()
