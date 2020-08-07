#!/usr/bin/env python3.6

import tqdm
import asyncio
import aiohttp

# It was boring to find somewhere a set of different files,
# so here I just downloading the same file in each coroutine :-)
URL = 'https://ideco.ru/assets/files/IdecoUTM_Admin_Guide.pdf'
CHUNK = 1024 * 1024 # 1MB
COROUTINES_NUM = 3 # Set it to 10 if you wish

async def download(idx, progress_queue):
    async with aiohttp.ClientSession() as session:
        async with session.get(URL) as response:
            filename = f'{idx}-{URL.split("/")[-1]}'
            size = int(response.headers.get('content-length', 0)) or None
            position = await progress_queue.get()
            progressbar = tqdm.tqdm(
                desc=filename, total=size, position=position, leave=True)
            with open(filename, mode='wb') as f, progressbar:
                async for chunk in response.content.iter_chunked(CHUNK):
                    f.write(chunk)
                    progressbar.update(len(chunk))
            await progress_queue.put(position)

async def asynchronous():
    progress_queue = asyncio.Queue()
    [progress_queue.put_nowait(idx) for idx in range(COROUTINES_NUM)]
    tasks = [download(idx, progress_queue) for idx in range(COROUTINES_NUM)]
    await asyncio.wait(tasks)

def main():
    ioloop = asyncio.get_event_loop()
    ioloop.run_until_complete(asynchronous())
    ioloop.close()
    print('')

if __name__ == "__main__":
    main()
