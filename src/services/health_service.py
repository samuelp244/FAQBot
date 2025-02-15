from datetime import datetime

class HealthService:
    def check_health(self):
        return {
            "status": "ok",
            "timestamp": datetime.now().isoformat()
        }
