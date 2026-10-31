from pathlib import Path
import json,time
from hashlib import sha256
import numpy as np
from PIL import Image
import openvino as ov
import openvino_genai as genai
R=Path(__file__).resolve().parents[1];out=R/'.cache/vlm-public-semantic-results';out.mkdir(exist_ok=False)
prompt=(R/'.cache/vlm-public-reference-results/GPU/prompt.txt').read_text('utf8')
prompt+='\n字段区分：保密等级是分队徽章旁的等级，不能用指挥等级、护盾或希望数替代。只展示几个界面片段的介绍画面归为other，不能当作完整探索地图。'
(out/'prompt.txt').write_text(prompt,'utf8')
print(json.dumps({'stage':'compile'}),flush=True);started=time.perf_counter();pipe=genai.VLMPipeline(str(R/'.cache/vlm-qwen3-4b-int4-candidate'),'GPU');load_ms=(time.perf_counter()-started)*1000
rows=[]
for second in(60,44):
    frame=R/f'.cache/vlm-public-reference-frames/{second}.png';image=np.asarray(Image.open(frame).convert('RGB'))
    print(json.dumps({'stage':'generate','second':second}),flush=True);started=time.perf_counter()
    result=pipe.generate(prompt,images=[ov.Tensor(image[None])],max_new_tokens=320,do_sample=False)
    row={'second':second,'raw_text':result.texts[0],'generation_ms':(time.perf_counter()-started)*1000,'input_public_png_sha256':sha256(frame.read_bytes()).hexdigest()}
    rows.append(row);(out/'progress.json').write_text(json.dumps({'load_ms':load_ms,'rows':rows},ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps({'stage':'generated','second':second,'generation_ms':row['generation_ms']}),flush=True)
frame=R/'.cache/vlm-public-reference-frames/60.png';image=np.asarray(Image.open(frame).convert('RGB'));short_prompt='只判断图片页面类型，从探索地图、干员详情、商店、战斗、其他中选一项；只回答该类型名称。'
print(json.dumps({'stage':'classification_only'}),flush=True);started=time.perf_counter();result=pipe.generate(short_prompt,images=[ov.Tensor(image[None])],max_new_tokens=16,do_sample=False)
classification={'prompt':short_prompt,'raw_text':result.texts[0],'generation_ms':(time.perf_counter()-started)*1000,'input_public_png_sha256':sha256(frame.read_bytes()).hexdigest()}
v={'runtime_ran':True,'load_ms':load_ms,'rows':rows,'classification_only':classification,'public_inputs_only':True,'scope':'Semantic clarification developed on60;44 is a held-out introduction composite, not an independent real-game session. No expected numbers supplied in prompts. No production integration.'}
(out/'results.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps({'runtime_ran':True,'pairs':2,'classification_ms':classification['generation_ms']}),flush=True)
