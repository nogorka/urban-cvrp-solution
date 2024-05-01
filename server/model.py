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
