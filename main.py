import os
import uuid
import shutil
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional

from transcriber import transcribe_video
from video_processor import burn_captions
from xml_generator import generate_alight_motion_xml

BASE_DIR = Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "uploads"
EXPORT_DIR = BASE_DIR / "exports"
TEMP_DIR = BASE_DIR / "temp"
for d in (UPLOAD_DIR, EXPORT_DIR, TEMP_DIR):
    d.mkdir(exist_ok=True)

app = FastAPI()

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

app.mount("/media", StaticFiles(directory=str(UPLOAD_DIR)), name="media")
app.mount("/downloads", StaticFiles(directory=str(EXPORT_DIR)), name="downloads")

class WordItem(BaseModel):
    id: str
    text: str
    start: float
    end: float
    fontSize: Optional[int] = 48
    color: Optional[str] = "#FFFFFF"
    bgColor: Optional[str] = "transparent"
    fontFamily: Optional[str] = "Arial"
    bold: Optional[bool] = True
    x: Optional[float] = 0.5
    y: Optional[float] = 0.85

class ExportRequest(BaseModel):
    video_id: str
    words: List[WordItem]
    video_width: Optional[int] = 1080
    video_height: Optional[int] = 1920

@app.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1].lower() or ".mp4"
    video_id = uuid.uuid4().hex
    saved_name = f"{video_id}{ext}"
    saved_path = UPLOAD_DIR / saved_name

    with open(saved_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    transcript = transcribe_video(str(saved_path))
    words_with_ids = []
    for i, w in enumerate(transcript["words"]):
        words_with_ids.append({
            "id": f"w_{i}_{uuid.uuid4().hex[:6]}", "text": w["word"].strip(),
            "start": float(w["start"]), "end": float(w["end"]),
            "fontSize": 48, "color": "#FFFFFF", "bgColor": "transparent",
            "fontFamily": "Arial", "bold": True, "x": 0.5, "y": 0.85,
        })

    return {
        "video_id": video_id, "filename": saved_name, "media_url": f"/media/{saved_name}",
        "duration": transcript.get("duration", 0), "words": words_with_ids,
    }

@app.post("/export-video")
async def export_video(req: ExportRequest):
    source = list(UPLOAD_DIR.glob(f"{req.video_id}.*"))[0]
    out_name = f"{req.video_id}_captioned.mp4"
    out_path = EXPORT_DIR / out_name
    burn_captions(str(source), str(out_path), [w.model_dump() for w in req.words], req.video_width, req.video_height, str(TEMP_DIR))
    return {"download_url": f"/downloads/{out_name}"}

@app.post("/export-xml")
async def export_xml(req: ExportRequest):
    out_name = f"{req.video_id}_alight.xml"
    out_path = EXPORT_DIR / out_name
    generate_alight_motion_xml(str(out_path), [w.model_dump() for w in req.words], req.video_width, req.video_height)
    return {"download_url": f"/downloads/{out_name}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
