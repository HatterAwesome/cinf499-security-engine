# Specfic imports
import os
import shutil
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
# Method for creating the FastAPI title and version name
app = FastAPI(
    title="CINF 499 AI Security Placement Engine",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# File uploading directory
UPLOAD_DIR = Path("../data/sample_blueprints")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@app.get("/")
def read_root():
    return {"status": "online", "system": "AI Low-Voltage Placement Engine"}
# Uploading blueprints from the user side
@app.post("/api/v1/blueprints/upload")
async def upload_blueprint(file: UploadFile = File(...)):
    # Extensions allowed for file uploads
    allowed_extensions = {".pdf", ".png", ".jpg", ".jpeg"}
    file_ext = Path(file.filename).suffix.lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type '{file_ext}'. Upload PDF or image CAD formats."
        )

    destination_path = UPLOAD_DIR / file.filename
    with open(destination_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "filename": file.filename,
        "status": "uploaded",
        "file_path": str(destination_path)
    }