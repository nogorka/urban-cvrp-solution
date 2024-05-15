from typing import Optional
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv

from app.dal import save_route, get_route_by_id, get_recent_routes
from app.ga import ga
from app.model import RequestOptimizer

load_dotenv()

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
    'graph_filename': "road_network_graph.pickle",
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
    try:
        if request.points and request.capacity:
            config['vehicle_capacity'] = request.capacity
            route = ga(request.points, config, settings)
            optimal_route = await save_route(route)
            return optimal_route
        else:
            raise HTTPException(status_code=404, detail="No points or capacity")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/route")
async def get_route(id: Optional[str] = None, amount: Optional[int] = Query(None, ge=1)):
    if id:
        try:
            route = await get_route_by_id(id)
            if route is None:
                raise HTTPException(status_code=404, detail="Route not found")
            return route
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    elif amount:
        try:
            routes = await get_recent_routes(amount)
            if routes is None:
                raise HTTPException(status_code=404, detail="No routes found")
            return routes
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    else:
        raise HTTPException(status_code=400, detail="Invalid query parameters")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
