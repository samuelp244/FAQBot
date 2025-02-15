from fastapi import APIRouter
from src.controllers.health_controller import router as health_router

api_router = APIRouter()

# Include all controller routers here
api_router.include_router(health_router)
