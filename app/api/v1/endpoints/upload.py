from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from typing import Any
import uuid
import os
import shutil
from fastapi.encoders import jsonable_encoder

router = APIRouter()

@router.post("/image", response_model=dict)
async def upload_image(
    file: UploadFile = File(...),
) -> Any:
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File provided is not an image.")
    
    file_ext = os.path.splitext(file.filename)[1]
    if not file_ext:
        file_ext = ".jpg"
    
    filename = f"upload_{uuid.uuid4().hex}{file_ext}"
    
    # Store locally for now (in static/uploads)
    app_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..")
    upload_dir = os.path.join(app_dir, "..", "static", "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Could not save file")
        
    return jsonable_encoder({
        "success": True,
        "data": {
            "url": f"{settings.BACKEND_URL}/static/uploads/{filename}"
        },
        "message": "Image uploaded successfully"
    })
