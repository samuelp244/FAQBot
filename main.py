import uvicorn
from fastapi import FastAPI
from src.routes import api_router

app = FastAPI(title="FAQ Bot API")

# Include all routes
app.include_router(api_router)

@app.get("/")
def root():
    return {"message": "Welcome to the FAQ Bot API"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=3001, reload=True)
