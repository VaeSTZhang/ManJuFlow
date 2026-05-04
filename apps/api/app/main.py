from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.documents import router as documents_router
from app.routers.health import router as health_router
from app.routers.images import router as images_router
from app.routers.prompts import router as prompts_router
from app.routers.scripts import router as scripts_router
from app.routers.storyboards import router as storyboards_router
from app.routers.system import router as system_router
from app.routers.uploads import router as uploads_router


app = FastAPI(title="Dramora API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents_router)
app.include_router(health_router)
app.include_router(images_router)
app.include_router(prompts_router)
app.include_router(scripts_router)
app.include_router(storyboards_router)
app.include_router(system_router)
app.include_router(uploads_router)
