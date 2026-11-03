"""A newly constructed public Fang page; never a recovered private screenshot."""
import hashlib
import json
from pathlib import Path
import sys
import time
from importlib.metadata import version

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from rouge.recognition import ScreenReader
from rouge.recognition_cache import CachedOCR
from rapidocr_onnxruntime.utils import OrtInferSession

# Observe actual calls without changing provider identity or returned values.
events = []
phase = "fixture_build"
original_session_call = OrtInferSession.__call__
def record_session_call(session, tensor):
    started = time.perf_counter()
    result = original_session_call(session, tensor)
    events.append({"phase": phase, "kind": "actual_onnx_inference",
                   "model": Path(session.session._model_path).name,
                   "input_shape": list(tensor.shape),
                   "elapsed_ms": (time.perf_counter()-started)*1000})
    return result
OrtInferSession.__call__ = record_session_call
original_cached_call = CachedOCR.__call__
def record_cached_call(engine, current, **kwargs):
    before = engine.cache.hits
    result = original_cached_call(engine, current, **kwargs)
    events.append({"phase": phase, "kind": "cached_ocr_request",
                   "input_shape": list(current.shape),
                   "exact_cache_hit": engine.cache.hits > before})
    return result
CachedOCR.__call__ = record_cached_call

OUT = Path(__file__).resolve().parent
control_root = ROOT / "rouge/data/page-features"
manifest_path = control_root / "manifest.json"
manifest = json.loads(manifest_path.read_text())
page = next(p for p in manifest["pages"] if p["page"] == "operator_detail")
image = np.full((703, 1280, 3), 32, np.uint8)
resources = []
for anchor in page["anchors"]:
    path = control_root / anchor["patch"]
    patch = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    x0, y0, x1, y1 = anchor["box"]
    image[y0:y1, x0:x1] = patch[:, :, None]
    resources.append({"path": str(path.relative_to(ROOT)), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})

font_path = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
draw = ImageDraw.Draw(pil)
def text(x, y, value, size, color=(255, 255, 255)):
    font = ImageFont.truetype(str(font_path), size)
    bbox = font.getbbox(value)
    draw.text((x, y-bbox[1]), value, font=font, fill=color)

text(460, 34, "PUBLIC SYNTHETIC FIXTURE", 24)
text(40, 490, "Fang", 38)
text(350, 535, "RANK3", 24)
text(1000, 180, "LV", 24)
text(998, 220, "40", 26)
text(1000, 260, "/40", 22)
text(125, 430, "100%", 24)
# Declared single skill is selected: a visible blue corner, not a mocked fact.
draw.rectangle((184, 514, 208, 530), fill=(0, 180, 255))
image = cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)

icon_path = ROOT / "rouge/data/ui-icons/potential-6.png"
icon = cv2.imread(str(icon_path), cv2.IMREAD_UNCHANGED)
icon = cv2.resize(icon, (90, 90), interpolation=cv2.INTER_AREA)
icon_rect = (1100, 240, 1190, 330)
x0, y0, x1, y1 = icon_rect
alpha = icon[:, :, 3:4].astype(np.float32) / 255
image[y0:y1, x0:x1] = np.round(icon[:, :, :3]*alpha + image[y0:y1, x0:x1]*(1-alpha)).astype(np.uint8)
resources.append({"path": str(icon_path.relative_to(ROOT)), "sha256": hashlib.sha256(icon_path.read_bytes()).hexdigest()})
cv2.imwrite(str(OUT / "public-baseline.png"), image)
changed = image.copy()
changed[y0:y1, x0:x1] = 32
cv2.imwrite(str(OUT / "public-icon-removed.png"), changed)
(OUT / "fixture-manifest.json").write_text(json.dumps({
    "fixture_kind": "new public synthetic operator panel",
    "original_230_sample": False,
    "declared_values": {"operator_id": "char_123_fang", "level": 40, "elite": 0,
                        "potential": 6, "trust": 100, "skill_rank_1": 3, "selected_skill": 1},
    "fixed_catalog": {"modules": []},
    "frame_shape": list(image.shape),
    "removed_icon_rect": icon_rect,
    "resources": resources,
    "draw_font": {"path": str(font_path), "sha256": hashlib.sha256(font_path.read_bytes()).hexdigest()},
    "static_control_bytes_preserved": all(np.array_equal(image[a["box"][1]:a["box"][3], a["box"][0]:a["box"][2]],
                                                       changed[a["box"][1]:a["box"][3], a["box"][0]:a["box"][2]])
                                         for a in page["anchors"]),
}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

results = {}
for label, kwargs in (("default", {}), ("legacy_dynamic", {"page_ocr_enabled": False})):
    reader = ScreenReader(**kwargs)
    records = {}
    for frame_label, frame in (("baseline", image), ("icon_removed", changed)):
        phase = label + ":" + frame_label
        result = reader.read(frame)
        records[frame_label] = result
        operator = result.get("operator") or {}
        print(json.dumps({"reader": label, "frame": frame_label, "page": result["page"],
                          "operator": operator.get("id"), "fields": operator.get("fields"),
                          "complete": operator.get("complete"), "missing_fields": operator.get("missing_fields"),
                          "performance": result["performance"]}, ensure_ascii=False), flush=True)
    results[label] = records

fresh = ScreenReader(cache_enabled=False, page_routing_enabled=False, page_ocr_enabled=False)
phase = "fresh_uncached:icon_removed"
results["fresh_uncached_icon_removed"] = fresh.read(changed)
(OUT / "recognition-results.json").write_text(json.dumps({
    "fixture_kind": "new public synthetic operator panel",
    "original_230_assert_verified": False,
    "rapidocr_onnxruntime": version("rapidocr-onnxruntime"),
    "results": results,
    "actual_call_events": events,
}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
summary = []
for call_phase in dict.fromkeys(event["phase"] for event in events):
    calls = [event for event in events if event["phase"] == call_phase]
    summary.append({"phase": call_phase,
                    "onnx_calls": sum(e["kind"] == "actual_onnx_inference" for e in calls),
                    "detector_calls": sum(e["kind"] == "actual_onnx_inference" and "det" in e["model"] for e in calls),
                    "recognizer_calls": sum(e["kind"] == "actual_onnx_inference" and "rec" in e["model"] for e in calls),
                    "requested_shapes": [e["input_shape"] for e in calls if e["kind"] == "cached_ocr_request"],
                    "actual_inference_ms": sum(e["elapsed_ms"] for e in calls if e["kind"] == "actual_onnx_inference")})
(OUT / "actual-work-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps(summary), flush=True)
