from fastapi import FastAPI
import uvicorn

from server.dal import save_route
from server.ga import ga
from server.model import Point

app = FastAPI()

config = {
    'city_name': "Saint Petersburg, Russia",
    'graph_filename': "../public/road_network_graph.pickle",
    'vehicle_capacity': 3000,
}


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/optimize")
async def optimize_route(points: list[Point]):
    route = ga(points, config)
    optimal_route = save_route(route)
    return optimal_route


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
