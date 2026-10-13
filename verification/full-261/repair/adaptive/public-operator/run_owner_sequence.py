"""Current-owner guards on new public pixels, using unmodified real inference."""
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import sys
import time

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from rouge.catalog import operator_profiles
from rouge.recognition import ScreenReader
from rapidocr_onnxruntime.utils import OrtInferSession

OUT=Path(__file__).resolve().parent
baseline=cv2.imread(str(OUT/"public-baseline.png"))
profile=operator_profiles()["char_240_wyvern"]
assert profile["name"]=="香草" and "Vanilla" in profile["aliases"]
assert len(profile["skills"])==1 and not profile["modules"]
assert profile["phases"][0]["max_level"]==40
vanilla=baseline.copy()
name_rect=(35,484,173,535)
x0,y0,x1,y1=name_rect
vanilla[y0:y1,x0:x1]=32
pil=Image.fromarray(cv2.cvtColor(vanilla,cv2.COLOR_BGR2RGB))
font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",38)
bbox=font.getbbox("Vanilla")
ImageDraw.Draw(pil).text((40,490-bbox[1]),"Vanilla",font=font,fill=(255,255,255))
vanilla=cv2.cvtColor(np.array(pil),cv2.COLOR_RGB2BGR)
damaged=vanilla.copy()
damaged[307:331,1048:1084]=32
frames=[("fang_baseline",baseline,"char_123_fang",OUT/"public-baseline.png"),
        ("vanilla_current",vanilla,"char_240_wyvern",OUT/"public-owner-vanilla.png"),
        ("vanilla_control_damaged",damaged,"char_240_wyvern",OUT/"public-owner-vanilla-control-damaged.png")]
records=[]
for label,frame,owner,path in frames:
    if label!="fang_baseline":cv2.imwrite(str(path),frame)
    records.append({"label":label,"path":str(path.relative_to(ROOT)),"declared_owner":owner,
                    "png_sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
                    "pixel_sha256":hashlib.sha256(frame.tobytes()).hexdigest(),
                    "shape":list(frame.shape),"dtype":frame.dtype.str})
(OUT/"owner-sequence-frames.json").write_text(json.dumps({
    "fixture_kind":"new public synthetic; not a private screenshot",
    "original_230_sample":False,"sequence":records,"name_replace_rect":name_rect,
    "control_damage_rect":[1048,307,1084,331],
    "vanilla_fixed_profile":{"operator_id":"char_240_wyvern","name":"香草","alias":"Vanilla",
                             "phases_max_level":[p["max_level"] for p in profile["phases"]],
                             "skill_count":1,"modules":[]},
    "declared_values":{"level":40,"elite":0,"potential":6,"trust":100,
                        "skill_rank_1":3,"selected_skill":1},
},ensure_ascii=False,indent=2)+"\n")

phase="init"
events=[]
actual_call=OrtInferSession.__call__
def observe(session,tensor):
    started=time.perf_counter();result=actual_call(session,tensor)
    events.append({"phase":phase,"model":Path(session.session._model_path).name,
                   "input_shape":list(tensor.shape),"elapsed_ms":(time.perf_counter()-started)*1000})
    return result
OrtInferSession.__call__=observe
def source_hashes():
    return {name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
            for name in ("rouge/recognition.py","rouge/dynamic_ocr.py","rouge/page_ocr.py")}
source_before=source_hashes()
def projection(result):
    op=result.get("operator")
    return {"page":result.get("page"),"operator":None if op is None else {
        key:op.get(key) for key in ("id","scope","fields","skill_ranks","missing_fields","complete")}}
reader=ScreenReader()
results={}
for label,frame,owner,path in frames:
    phase="sequence:"+label
    observed=reader.read(frame)
    phase="fresh_uncached:"+label
    oracle=ScreenReader(cache_enabled=False,page_routing_enabled=False,page_ocr_enabled=False).read(frame)
    results[label]={"observed":observed,"fresh_uncached":oracle,
                    "matches_fresh_operator":projection(observed)==projection(oracle),
                    "declared_owner_seen":(observed.get("operator") or {}).get("id")==owner}
    print(json.dumps({"frame":label,"current_observation":projection(observed),
        "fresh_observation":projection(oracle),"matches_fresh_operator":results[label]["matches_fresh_operator"],
        "declared_owner_seen":results[label]["declared_owner_seen"],
        "routing":observed["performance"].get("routing"),"ocr":observed["performance"].get("ocr")},ensure_ascii=False),flush=True)
receipt={"fixture_kind":"new public synthetic real 3-frame current-owner sequence",
         "original_230_assert_verified":False,"rapidocr_onnxruntime":version("rapidocr-onnxruntime"),
         "source_hashes_before":source_before,"source_hashes_after":source_hashes(),
         "results":results,"actual_call_events":events}
(OUT/"before-owner-sequence.json").write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"source_unchanged":receipt["source_hashes_before"]==receipt["source_hashes_after"],
    "all_current_owners_and_fresh":all(x["matches_fresh_operator"] and x["declared_owner_seen"] for x in results.values())}),flush=True)
