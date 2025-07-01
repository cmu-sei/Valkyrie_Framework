import os
import shutil
from fastapi import APIRouter, Request, HTTPException, File, UploadFile
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api/datasources", tags=["Data Sources"])

def get_upload_dir(request: Request) -> str:
    """config is saved into app state on load, but we must access it through the associated request object"""
    return request.app.state.config["general"]["raw_loc"]

@router.get("/")
def get_files(request: Request):
    upload_directory = get_upload_dir(request)
    files = []
    if os.path.exists(upload_directory):
        files = os.listdir(upload_directory)
    return {"files": files}

@router.post("/")
def upload_file(request: Request, file: UploadFile = File(...)):
    upload_directory = get_upload_dir(request)
    os.makedirs(upload_directory, exist_ok=True)
    file_location = f"{upload_directory}/{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return JSONResponse(content={"filename": file.filename})

@router.delete("/{name}")
def delete_file(request: Request, name: str):
    file_path = os.path.join(get_upload_dir(request), name)

    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    try:
        os.remove(file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")

    return {"message": f"{name} deleted"}