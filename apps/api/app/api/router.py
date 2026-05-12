from fastapi import APIRouter

from app.api.routes import assets, generate, health, projects

api_router = APIRouter(prefix="/api")
api_router.include_router(health.router)
api_router.include_router(projects.router)
api_router.include_router(assets.router)
api_router.include_router(generate.router)
