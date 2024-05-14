import json
from typing import List

from pydantic import BaseModel


class Point(BaseModel):
    adress: str
    free_volume: int
    id: int
    lat: float
    long: float
    purpose: str
    total_volume: int
    type: str


class RequestOptimizer(BaseModel):
    capacity: int
    points: List[Point]


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Point):
            return {
                'adress': obj.adress,
                'free_volume': obj.free_volume,
                'id': obj.id,
                'lat': obj.lat,
                'long': obj.long,
                'purpose': obj.purpose,
                'total_volume': obj.total_volume,
                'type': obj.type
            }
        return json.JSONEncoder.default(self, obj)
