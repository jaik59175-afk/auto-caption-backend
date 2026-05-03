import whisper
import torch

_MODEL = None

def _get_model():
    global _MODEL
    if _MODEL is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        _MODEL = whisper.load_model("base", device=device)
    return _MODEL

def transcribe_video(video_path: str) -> dict:
    model = _get_model()
    result = model.transcribe(video_path, word_timestamps=True, verbose=False, fp16=torch.cuda.is_available())
    words = []
    duration = 0.0
    for seg in result.get("segments", []):
        if seg.get("end", 0) > duration: duration = seg["end"]
        for w in seg.get("words", []) or []:
            text = (w.get("word") or "").strip()
            if text: words.append({"word": text, "start": float(w.get("start", seg["start"])), "end": float(w.get("end", seg["end"]))})
    return {"duration": duration, "words": words}
