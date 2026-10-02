import asyncio
import time

import httpx

URL = "http://127.0.0.1:8000/order"
CONCURRENCY = 5


async def time_one(client, index):
    start = time.perf_counter()
    await client.get(URL)
    elapsed = time.perf_counter() - start
    print(f"request {index}: {elapsed:.2f}s")
    return elapsed


async def main():
    start = time.perf_counter()
    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(
            *(time_one(client, i) for i in range(CONCURRENCY))
        )
    total = time.perf_counter() - start
    print(f"\n{CONCURRENCY} requests took {total:.2f}s total")
    print(f"each request blocked for ~3s; total ~= {CONCURRENCY} x 3s = {total:.2f}s")


if __name__ == "__main__":
    asyncio.run(main())