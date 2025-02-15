from fastapi import APIRouter
from src.controllers.health_controller import router as health_router
from src.controllers.document_controller import router as document_router
from src.controllers.query_controller import router as query_router

api_router = APIRouter()

# Include all controller routers here
api_router.include_router(health_router)
api_router.include_router(document_router)
api_router.include_router(query_router)
