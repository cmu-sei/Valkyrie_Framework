from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api", tags=["Application"])

@router.get("/")
def server_info():
    return {"title": "", "version": "1.0.0", "description": ""}

# === configuration ===

@router.get("/configuration")
def get_configuration():
    s = ServerConfiguration(
        some_value="default_value"
    )
    return s

class ServerConfiguration(BaseModel):
    some_value: str

@router.post("/configuration")
def update_configuration():
    return {"config": ""}
