from fastapi import FastAPI

from app.routers.health import router as health_router
from app.routers.scripts import router as scripts_router


app = FastAPI(title="ManJuFlow API")

app.include_router(health_router)
app.include_router(scripts_router)
