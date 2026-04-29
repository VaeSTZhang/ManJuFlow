from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.health import router as health_router
from app.routers.scripts import router as scripts_router
from app.routers.storyboards import router as storyboards_router
from app.routers.system import router as system_router


app = FastAPI(title="ManJuFlow API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(scripts_router)
app.include_router(storyboards_router)
app.include_router(system_router)
