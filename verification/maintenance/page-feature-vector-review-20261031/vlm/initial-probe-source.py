from pathlib import Path
import json,sys,time
from hashlib import sha256
import numpy as np
from PIL import Image
import openvino as ov
import openvino_genai as genai

R=Path(__file__).resolve().parents[1];device=sys.argv[1]
out=R/'.cache/vlm-public-reference-results'/device;out.mkdir(parents=True,exist_ok=False)
model=R/'.cache/vlm-qwen3-4b-int4-candidate'
manifest=json.loads((model/'download-complete.json').read_bytes());assert manifest['passed']
frame=R/'.cache/vlm-public-reference-frames/60.png'
prompt='''只依据这张图片读取信息，不要推测未显示的游戏状态。只返回一个JSON对象，不加解释或代码块。
page_type从exploration_map、operator_detail、shop、combat、other中选一项。
字段为：page_type，area_name（区域中文名），floor（区域层数），target_life_current（当前目标生命），target_life_max（目标生命上限），operator_count（干员总数），relic_count（收藏品总数），confidentiality_level（保密等级），squad_name（分队中文名称），visible_node_types（画面中能读出的不同节点名称列表）。看不清或不能从画面确认的字段写null，不要依据图标猜分队名称。数字字段用整数。'''
(out/'prompt.txt').write_text(prompt,'utf8')
started=time.perf_counter();print(json.dumps({'stage':'compile','device':device}),flush=True)
pipe=genai.VLMPipeline(str(model),device)
load_ms=(time.perf_counter()-started)*1000;rows=[]
for repeat in range(2):
    image=np.asarray(Image.open(frame).convert('RGB'))
    print(json.dumps({'stage':'generate','device':device,'repeat':repeat,'load_ms':load_ms}),flush=True)
    started=time.perf_counter();result=pipe.generate(prompt,images=[ov.Tensor(image[None])],max_new_tokens=320,do_sample=False)
    elapsed_ms=(time.perf_counter()-started)*1000;text=result.texts[0]
    # Preserve the actual response even when it is malformed or incorrect.
    row={'repeat':repeat,'generation_ms':elapsed_ms,'raw_text':text,'input_size':[image.shape[1],image.shape[0]],'input_public_png_sha256':sha256(frame.read_bytes()).hexdigest()}
    rows.append(row);(out/'progress.json').write_text(json.dumps({'load_ms':load_ms,'rows':rows},ensure_ascii=False,indent=2)+'\n','utf8')
    print(json.dumps({'stage':'generated','repeat':repeat,'generation_ms':elapsed_ms,'characters':len(text)}),flush=True)
value={'runtime_ran':True,'device':device,'load_ms':load_ms,'rows':rows,'model_revision':manifest['revision'],'openvino':ov.__version__,'genai':genai.get_version(),
    'only_public_reference_image_used':True,'private_game_capture_used':False,'local_inference_not_remote_chat':True,'not_production_integration_or_whole_accuracy_proof':True}
(out/'results.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n','utf8')
print(json.dumps({'runtime_ran':True,'device':device,'repeats':len(rows)}),flush=True)
