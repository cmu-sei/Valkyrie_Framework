import os
import shutil
from fastapi import APIRouter, HTTPException, File, UploadFile
from fastapi.responses import JSONResponse

UPLOAD_DIR = "/tmp"
router = APIRouter(prefix="/api/datasources", tags=["Data Sources"])

@router.get("/")
def get_files():
    files = os.listdir(UPLOAD_DIR)
    return {"files": files}

@router.post("/")
def upload_file(file: UploadFile = File(...)):
    file_location = f"{UPLOAD_DIR}/{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return JSONResponse(content={"filename": file.filename})

@router.delete("/{name}")
def delete_file(name: str):
    file_path = os.path.join(UPLOAD_DIR, name)

    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    try:
        os.remove(file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")

    return {"message": f"{name} deleted"}