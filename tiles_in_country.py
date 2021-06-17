import asyncio
import datetime
import json
import math
import os
import tempfile
import time
from multiprocessing import Pool

import aiohttp
from shapely.geometry import Point, shape

API = 'api-version=2.0'
BASE = 'https://t-azmaps.azurelbs.com/map/tile'
COUNTRY = "Kenya"
CHUNK_SIZE = 2000
KEY = 'FrvcIwC_84Jv5g8mZ4ezpk8-oVae6vVzufnDlydufyU'
LOG_CHUNK_SIZE = 400000
TILESET = 'microsoft.imagery.v2'
TMP_DIR = "C:/Users/cdow/Desktop/test/"
ZOOM = 15

sub = f'subscription-key={KEY}'
url = f'{BASE}?{sub}&{API}&tilesetId={TILESET}&zoom={ZOOM}'


def deg2num(lat_deg, lon_deg, zoom):
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return (xtile, ytile)


def num2deg(xtile, ytile, zoom):
    n = 2.0 ** zoom
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = math.degrees(lat_rad)
    return (lat_deg, lon_deg)


async def send_requests(data):    
    jobs = []
    session = aiohttp.ClientSession()
    async with session:
        for x, y in data:
            endpoint = url + f'&x={x}&y={y}'
            job = session.get(endpoint)
            jobs.append(job)
        await asyncio.gather(*jobs)
        
with open("..\geo-countries\data\countries.geojson") as geojson_file:
    data = json.load(geojson_file)

features = data['features']
country = [f for f in features if f['properties']['ADMIN'] == COUNTRY][0]
buffer = shape(country['geometry']).buffer(0.02)
envelope = buffer.envelope
coords = envelope.exterior.coords
p1, p2 = coords[1], coords[3]
x1, y1 = deg2num(p2[1], p2[0], ZOOM)
x2, y2 = deg2num(p1[1], p1[0], ZOOM)
tiles_in_envelope = []
for x in range(x1, x2+1):
    for y in range(y1, y2+1):
        tiles_in_envelope.append((x, y))
print("Tiles in envelope: " + str(len(tiles_in_envelope)))
tiles_in_buffer = []
for tile in tiles_in_envelope:
    coord = num2deg(tile[0], tile[1], ZOOM)
    point = Point(coord[1], coord[0])
    if point.within(buffer):
        tiles_in_buffer.append(tile)
print("Tiles in buffer: " + str(len(tiles_in_buffer)))
for i in range(0, len(tiles_in_buffer), CHUNK_SIZE):
    file = tempfile.NamedTemporaryFile(delete=False, dir=TMP_DIR)
    chunk = tiles_in_buffer[i:i+CHUNK_SIZE]
    data = json.dumps(chunk)
    file.write(bytes(data, 'utf-8'))
print(COUNTRY)
print(datetime.datetime.now())
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
requests_sent = 0
# Loop to deal with networking issues for large number of requests
while len(os.listdir(TMP_DIR)) > 0:
    for file in os.listdir(TMP_DIR):
        file = TMP_DIR + file
        try:
            with open(file, 'r') as chunk:
                data = json.load(chunk)
                asyncio.run(send_requests(data))
            os.remove(file)
            # Pause and timestamp every 400k requests due to log size limit
            requests_sent += CHUNK_SIZE
            if requests_sent >= LOG_CHUNK_SIZE:
                print(datetime.datetime.now())
                print("Pausing...")
                time.sleep(120)
                print(datetime.datetime.now())
        except:
            print("Error " + file)
            continue
print(datetime.datetime.now())
