from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/datasources", tags=["Data Sources"])

@router.get("/")
def get_files():
    return {"files": []}

@router.post("/")
def create_new_file():
    return {"message": "ok"}