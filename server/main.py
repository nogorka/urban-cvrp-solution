from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from server.dal import save_route, get_route
from server.ga import ga
from server.model import Point

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

config = {
    'city_name': "Saint Petersburg, Russia",
    'graph_filename': "../public/road_network_graph.pickle",
    'vehicle_capacity': 1000,
}


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/optimize")
async def optimize_route(points: list[Point]):
    route = ga(points, config)
    optimal_route = save_route(route)
    return optimal_route


@app.get("/route")
async def optimize_route(id: str):
    optimal_route = get_route(id)
    return optimal_route


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
