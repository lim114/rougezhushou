"""Before-change receipts using the new public Fang fixture and actual inference."""
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import sys
import time

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from rouge.recognition import ScreenReader
from rouge.viewport import prepare_frame
from rapidocr_onnxruntime.utils import OrtInferSession

OUT = Path(__file__).resolve().parent
source_files = ["rouge/recognition.py", "rouge/dynamic_ocr.py", "rouge/page_ocr.py", "rouge/operator_recognition.py"]
def hashes():
    return {name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in source_files}
source_before = hashes()
baseline = cv2.imread(str(OUT/"public-baseline.png"))
frames = {"baseline": baseline, "icon_removed": cv2.imread(str(OUT/"public-icon-removed.png"))}
control = baseline.copy()
control_rect = (1048, 307, 1084, 331)
x0,y0,x1,y1 = control_rect
control[y0:y1, x0:x1] = 32
frames["control_damaged"] = control
pil = Image.fromarray(cv2.cvtColor(baseline, cv2.COLOR_BGR2RGB))
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
text = "PUBLIC OVERLAY 261"
box = font.getbbox(text)
ImageDraw.Draw(pil).text((470, 160-box[1]), text, font=font, fill=(255,255,255))
frames["exterior_overlay"] = cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)
prepared,_ = prepare_frame(baseline)
geometry = np.full((1800,3200,3), 8, np.uint8)
h,w = prepared.shape[:2]
geometry[100:100+h, 500:500+w] = prepared
frames["geometry_changed"] = geometry

frame_records = {}
for name, frame in frames.items():
    path = OUT / ("public-"+name.replace("_","-")+".png")
    if name == "baseline": path = OUT/"public-baseline.png"
    if name == "icon_removed": path = OUT/"public-icon-removed.png"
    cv2.imwrite(str(path), frame)
    frame_records[name] = {"path": str(path.relative_to(ROOT)),
        "png_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "pixel_sha256": hashlib.sha256(frame.tobytes()).hexdigest(),
        "shape": list(frame.shape), "dtype": frame.dtype.str}
(OUT/"frames.json").write_text(json.dumps({
    "fixture_kind": "new public synthetic Fang panel and explicit transformations",
    "original_230_sample": False,
    "baseline_values": json.loads((OUT/"fixture-manifest.json").read_text())["declared_values"],
    "frames": frame_records,
    "control_damage_rect": control_rect,
    "overlay_text": text,
    "geometry": {"canvas": [3200,1800], "padding_value": 8, "offset": [500,100],
                 "embedded_frame": "prepare_frame(public-baseline.png)"},
}, ensure_ascii=False, indent=2)+"\n")

events = []
phase = "initialization"
original_call = OrtInferSession.__call__
def observe_call(session, tensor):
    start = time.perf_counter()
    result = original_call(session, tensor)
    events.append({"phase": phase, "model": Path(session.session._model_path).name,
                   "input_shape": list(tensor.shape),
                   "elapsed_ms": (time.perf_counter()-start)*1000})
    return result
OrtInferSession.__call__ = observe_call

def projection(result):
    operator=result.get("operator")
    if operator is None:return {"page": result.get("page"), "operator": None}
    return {"page": result.get("page"), "operator": {
        key:operator.get(key) for key in ("id","scope","fields","skill_ranks","missing_fields","complete")}}

receipts = {}
for scenario in ("icon_removed", "control_damaged", "exterior_overlay", "geometry_changed"):
    receipt = {}
    for strategy,kwargs in (("default",{}),("legacy_dynamic",{"page_ocr_enabled":False})):
        reader=ScreenReader(**kwargs)
        pair={}
        for name,frame in (("baseline",baseline),(scenario,frames[scenario])):
            phase=strategy+":"+scenario+":"+name
            result=reader.read(frame)
            pair[name]=result
            print(json.dumps({"phase":phase,"observation":projection(result),
                "ocr":result["performance"].get("ocr"),"routing":result["performance"].get("routing")},ensure_ascii=False),flush=True)
        receipt[strategy]=pair
    phase="fresh_uncached:"+scenario
    fresh=ScreenReader(cache_enabled=False,page_routing_enabled=False,page_ocr_enabled=False)
    oracle=fresh.read(frames[scenario])
    receipt["fresh_uncached"]=oracle
    receipt["matches_fresh_operator"]={strategy:projection(receipt[strategy][scenario])==projection(oracle)
                                       for strategy in ("default","legacy_dynamic")}
    receipts[scenario]=receipt
    print(json.dumps({"scenario":scenario,"fresh_observation":projection(oracle),
                      "matches_fresh_operator":receipt["matches_fresh_operator"]},ensure_ascii=False),flush=True)

summary=[]
for p in dict.fromkeys(event["phase"] for event in events):
    calls=[e for e in events if e["phase"]==p]
    summary.append({"phase":p,"detector_calls":sum("det" in e["model"] for e in calls),
        "recognizer_calls":sum("rec" in e["model"] for e in calls),
        "classifier_calls":sum("cls" in e["model"] for e in calls),
        "actual_inference_ms":sum(e["elapsed_ms"] for e in calls)})
output={"fixture_kind":"new public synthetic; not recovered private sample",
    "original_230_assert_verified":False,"source_hashes_before":source_before,
    "source_hashes_after":hashes(),"rapidocr_onnxruntime":version("rapidocr-onnxruntime"),
    "actual_call_instrumentation":"Calls the original OrtInferSession method; provider types, results and cache configuration unchanged.",
    "scenarios":receipts,"actual_call_events":events,"actual_work_summary":summary}
(OUT/"before-scenarios.json").write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"source_unchanged":output["source_hashes_before"]==output["source_hashes_after"],
    "all_match_fresh":all(all(v["matches_fresh_operator"].values()) for v in receipts.values())},ensure_ascii=False),flush=True)
