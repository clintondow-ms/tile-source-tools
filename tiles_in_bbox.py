import datetime
import math
import time

import aiohttp
import asyncio

BASE = 'https://t-azmaps.azurelbs.com/map/tile'
KEY = 'FrvcIwC_84Jv5g8mZ4ezpk8-oVae6vVzufnDlydufyU'
TILESET = 'microsoft.imagery.v2'
ZOOM = 18

def deg2num(lat_deg, lon_deg, zoom):
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return (xtile, ytile)

x1, y1 = deg2num(1.4573315578297326, 103.61384090712352, ZOOM)
x2, y2 = deg2num(1.255231937623705, 104.08890835543093, ZOOM)

async def main():
    jobs = []

    async with aiohttp.ClientSession() as session:
        for x in range(x1, x2+1):
            for y in range(y1, y2+1):
                url = f'{BASE}?subscription-key={KEY}&api-version=2.0&tilesetId={TILESET}&zoom={ZOOM}&x={x}&y={y}'
                job = session.get(url)
                jobs.append(job)
        print(f"{len(jobs)} jobs")
        for i in range(0, len(jobs), 3000):
            print(f"Chunk {i}-{i+3000}")
            jobs_chunk = jobs[i:i+3000]
            await asyncio.gather(*jobs_chunk)
            time.sleep(10)

print("Singapore")
print(f"Start: {datetime.datetime.now()}")
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
asyncio.run(main())
print(f"End: {datetime.datetime.now()}")
