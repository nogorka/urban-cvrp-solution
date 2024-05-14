from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.dal import save_route, get_route
from app.ga import ga
from app.model import RequestOptimizer

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://nogorka-cvrp.netlify.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

config = {
    'city_name': "Saint Petersburg, Russia",
    'graph_filename': "public/road_network_graph.pickle",
    'vehicle_capacity': 1000,
}

settings = {
    'population_size': 10,
    'generations': 10,
    'converge_threshold': 1e-08,
    'converge_patience': 5,
    'over_penalty_rate': 0.6,
    'under_penalty_rate': 0.3,
    'penalty_weight': 5,
    'bonus_rate': 1.8,
    'bonus_weight': 0.15,
    'desired_threshold': 2.7e05,
    'mutation_rate': 0.4,
    'relocation_rate': 0.7
}


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/optimize")
async def optimize_route(request: RequestOptimizer):
    config['vehicle_capacity'] = request.capacity
    route = ga(request.points, config, settings)
    optimal_route = save_route(route)
    return optimal_route


@app.get("/route")
async def optimize_route(id: str):
    optimal_route = get_route(id)
    return optimal_route


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
