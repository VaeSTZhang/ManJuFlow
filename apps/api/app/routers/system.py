from fastapi import APIRouter

from app.config import get_settings


router = APIRouter(prefix="/api/system", tags=["system"])


@router.get("/status")
def get_system_status() -> dict[str, str | bool]:
    settings = get_settings()
    script_generation_mode = settings.script_generation_mode
    llm_enabled = script_generation_mode == "llm" and settings.is_llm_enabled()

    return {
        "app_name": settings.app_name,
        "app_env": settings.app_env,
        "script_generation_mode": script_generation_mode,
        "llm_enabled": llm_enabled,
        "status": "ok",
    }
