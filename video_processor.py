import subprocess
import shlex
from pathlib import Path

def _escape_text(s: str) -> str:
    return s.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'").replace(",", "\\,").replace("[", "\\[").replace("]", "\\]").replace("%", "\\%")

def _hex_to_ffmpeg_color(hex_color: str, alpha: float = 1.0) -> str:
    if not hex_color or hex_color.lower() == "transparent": return "black@0.0"
    h = hex_color.lstrip("#")
    if len(h) == 3: h = "".join(c * 2 for c in h)
    return f"0x{h.upper()}@{alpha}"

def burn_captions(input_path: str, output_path: str, words: list, width: int = 1080, height: int = 1920, temp_dir: str = "./temp") -> str:
    Path(temp_dir).mkdir(exist_ok=True)
    if not words:
        subprocess.run(shlex.split(f'ffmpeg -y -i "{input_path}" -c copy "{output_path}"'), check=True)
        return output_path

    filters = []
    for w in words:
        text, start, end = _escape_text(w["text"]), float(w["start"]), float(w["end"])
        font_size, color, bg = int(w.get("fontSize", 48)), _hex_to_ffmpeg_color(w.get("color", "#FFFFFF")), w.get("bgColor", "transparent")
        cx, cy = float(w.get("x", 0.5)) * width, float(w.get("y", 0.85)) * height
        parts = [f"text='{text}'", f"fontsize={font_size}", f"fontcolor={color}", f"x={int(cx)}-text_w/2", f"y={int(cy)}-text_h/2", "borderw=3", "bordercolor=black@0.85", f"enable='between(t,{start},{end})'"]
        if bg and bg.lower() != "transparent": parts.extend(["box=1", f"boxcolor={_hex_to_ffmpeg_color(bg, 0.6)}", "boxborderw=10"])
        filters.append("drawtext=" + ":".join(parts))

    cmd = ["ffmpeg", "-y", "-i", input_path, "-vf", ",".join(filters), "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", output_path]
    subprocess.run(cmd, capture_output=True, text=True, check=True)
    return output_path
