from lxml import etree
from datetime import datetime

def generate_alight_motion_xml(output_path: str, words: list, width: int = 1080, height: int = 1920, fps: int = 30) -> str:
    duration = max((w["end"] for w in words), default=0.0)
    root = etree.Element("AlightMotionProject", version="4.3.0")
    meta = etree.SubElement(root, "ProjectInfo")
    for k, v in {"Name": "Unlimited Caption Studio Export", "Created": datetime.utcnow().isoformat(), "Width": str(width), "Height": str(height), "FrameRate": str(fps), "Duration": f"{duration:.3f}", "BackgroundColor": "#000000"}.items():
        etree.SubElement(meta, k).text = v

    layers = etree.SubElement(root, "Layers")
    for idx, w in enumerate(words):
        layer = etree.SubElement(layers, "TextLayer", id=str(w.get("id", f"layer_{idx}")), name=f"Word_{idx}_{w['text'][:12]}")
        etree.SubElement(layer, "StartTime").text = f"{float(w['start']):.3f}"
        etree.SubElement(layer, "EndTime").text = f"{float(w['end']):.3f}"
        etree.SubElement(layer, "Text").text = etree.CDATA(w["text"])
        
        style = etree.SubElement(layer, "Style")
        for k, v in {"FontFamily": w.get("fontFamily", "Arial"), "FontSize": str(w.get("fontSize", 48)), "FontColor": w.get("color", "#FFFFFF"), "BackgroundColor": w.get("bgColor", "transparent"), "Bold": "true" if w.get("bold") else "false", "Stroke": "#000000", "StrokeWidth": "3", "Alignment": "center"}.items():
            etree.SubElement(style, k).text = v

        transform = etree.SubElement(layer, "Transform")
        etree.SubElement(transform, "Position", x=f"{float(w.get('x', 0.5)) * width:.1f}", y=f"{float(w.get('y', 0.85)) * height:.1f}")
        for k, v in {"Scale": {"x": "1.0", "y": "1.0"}}.items(): etree.SubElement(transform, k, **v)
        for k, v in {"Rotation": "0", "Opacity": "1.0"}.items(): etree.SubElement(transform, k).text = v

        anim = etree.SubElement(layer, "Animations")
        etree.SubElement(anim, "Keyframe", property="Scale", time=f"{float(w['start']):.3f}").text = "0.6"
        etree.SubElement(anim, "Keyframe", property="Scale", time=f"{float(w['start']) + 0.1:.3f}").text = "1.0"

    etree.ElementTree(root).write(output_path, pretty_print=True, xml_declaration=True, encoding="UTF-8")
    return output_path
