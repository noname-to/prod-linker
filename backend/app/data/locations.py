import json
from math import ceil
from typing import List
from collections import defaultdict
from pprint import pprint as print

from dadata import DadataAsync
from shapely.geometry import Point, shape
from geopy.distance import geodesic
import numpy as np
import requests

from app import DADATA_API, DADATA_SECRET
from app.data import models

geojson = json.loads(open('./app/moscow.geojson').read())
shapes = [shape(x['geometry']) for x in geojson['features']]


def mean_coord(locations: List[models.Coords]) -> models.Coords:
    lats = [location.latitude for location in locations]
    longs = [location.longitude for location in locations]

    return models.Coords(latitude=sum(lats) / len(lats), longitude=sum(longs) / len(longs))


async def get_closest_meetings(meetings: List[models.Meeting], location: models.Coords) -> List[models.Meeting]:
    representative_bound_meetings = defaultdict(lambda: [])
    for meeting in meetings:
        representative_bound_meetings[meeting.representative].append(meeting)
        
    representative_middle_coord = {}
    for representative, meetings in representative_bound_meetings.items():
        representative_middle_coord[representative] = mean_coord([x.meeting_location for x in meetings])

    distances = {}
    for representative, midcord in representative_middle_coord.items():
        distances[representative] = get_straight_distance(midcord, location)
    
    max_bound = np.percentile(list(distances.values()), 50)
    distances = list(filter(lambda x: x[1] <= max_bound, distances.items()))

    res = []
    for distance in distances:
        res += representative_bound_meetings[distance[0]]

    return res


async def coords_from_addr(addr: str) -> models.Coords | None:
    async with DadataAsync(DADATA_API, DADATA_SECRET) as dadata:
        addrinfo = dadata.clean(name='address', source=addr)

    if addrinfo['qc_geo'] > 2:
        return None

    coords = models.Coords(latitude=addrinfo['geo_lat'], longitude=addrinfo['geo_lon'])

    return coords


async def addr_from_coords(coords: models.Coords) -> str | None:
    async with DadataAsync(DADATA_API, DADATA_SECRET) as dadata:
        coordinfo = await dadata.geolocate(name='address', lat=coords.latitude, lon=coords.longitude, radius_meters=50)

    if len(coordinfo) == 0:
        return None
    
    return coordinfo[0]['value']
        
    
def check_contains_in(coords: models.Coords) -> bool:
    map_point = Point(coords.longitude, coords.latitude)

    return any(x.contains(map_point) for x in shapes)


def get_straight_distance(coords_from: models.Coords, coords_to: models.Coords) -> float:
    return geodesic((coords_from.latitude, coords_from.longitude), (coords_to.latitude, coords_to.longitude)).km


async def fetch_route_length_km(coords_from: models.Coords, coords_to: models.Coords) -> float:
    user_agent_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
    }
    start_longitude, start_latitude = coords_from.longitude, coords_from.latitude
    end_longitude, end_latitude = coords_to.longitude, coords_to.latitude
    url = f'https://router.project-osrm.org/route/v1/driving/{start_longitude},{start_latitude};{end_longitude},{end_latitude}?steps=true'
    response = requests.get(url, headers=user_agent_headers)
    data = response.json()

    if data['code'] != 'Ok':
        return get_straight_distance(coords_from=coords_from, coords_to=coords_to)

    return data['routes'][0]['distance']


async def calculate_traveltime_minutes(coords_from: models.Coords, coords_to: models.Coords, is_car: bool) -> int:

    distance = get_straight_distance(coords_from=coords_from, coords_to=coords_to)

    # When using OSM
    # distance = await fetch_route_length_km(coords_from=coords_from, coords_to=coords_to)

    time_minutes = ceil(distance / (30 if is_car else 5) * 60)

    # print(time_minutes)

    return time_minutes

