from fastapi import APIRouter
from src.services.health_service import HealthService

router = APIRouter(tags=["health"])
health_service = HealthService()

@router.get("/health")
def health_check():
    return health_service.check_health()
