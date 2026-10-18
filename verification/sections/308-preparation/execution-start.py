from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json,subprocess
ROOT=Path(__file__).resolve().parents[1]
assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()=='codex/p2-development'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()=='aae2340ba4689dd54097f84db4942af21e0d88f8'
def enc(v):return (json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf8')
p=ROOT/'DEVELOPMENT_CHECKPOINT.json';c=json.loads(p.read_bytes());assert(c['completed_sections'],c['next_section'])==(307,308)
c['historical_before308_batch']=c['current_batch'];c['active_section']={'number':308,'status':'source_reading_not_accepted','remaining_todo':'Fixed battle map point mapping: two new images with no current direct or regular projection','planned_change':'一步之遥、彼处水如酒的低地逐格位置参考，覆盖普通与紧急四个真实别名','acceptance':'Both independent first complete67 readings frozen before any comparison; strict4px and unreadable rejection; original107 direct and12/24 regular intact; actual new-cell click/resize/refresh/unknown no mapping; native fixture and original project app; sources/requirements/index ordinary publication with real remote check','full_map_calibration_claimed':False}
c['current_batch']={'start':308,'end':None,'status':'P3_SECTION308_IN_PROGRESS','completed_sections':307,'next_section':308,'next_section_started':True,'next_full_validation_after':320,'batch_closed':False,'target_origin':'User authorized P3 continuation; no numeric stopping target','receipt':'verification/sections/307.json'}
c['batch_status']='P3_SECTION308_IN_PROGRESS';p.write_bytes(enc(c))
out=ROOT/'verification/sections/308-preparation';out.mkdir()
record={'section':308,'at_utc':datetime.now(timezone.utc).isoformat(),'stage':'planned_functional_scope_not_completed','previous_section_receipt':'verification/sections/307.json','active_scope':c['active_section'],'source_only_request':{'file':'.cache/p3-308-reader-inputs/REQUESTS.json','sha256':'498066fea45d23b4ab1651f088046720d84df9f1bd430f3828c6c370221ee49d','total_requests':67},'readers_are_separate_agent_contexts_not_humans':True,'absolute_bitmap_position_accuracy_verified':False,'latest_usage':{'tool':'mcp__codex_app.get_usage_limits','used_percent':5,'remaining_percent':95,'window_minutes':10080,'other_window':None,'below15':False},'private_or_game_or_chat_operations':False}
(out/'start.json').write_bytes(enc(record));(out/'execution-start.py').write_bytes(Path(__file__).read_bytes())
p=ROOT/'WORK_IN_PROGRESS.md';s=p.read_text('utf8');p.write_bytes(('## 当前进行第308节 · 两张新固定地图的低地位置参考（尚未完成）\n\n一步之遥、彼处水如酒共67完整低地请求，两份独立首次读数冻结后才比较，严格4像素准入、遮挡不明保留未知；不拟合或外推，不宣称完整地图校准。此前已交付仍为第307节，320定期全量保留。验收、原测试窗口、要求/索引与普通发布核对尚待实际完成。\n\n以下为已交付历史。\n\n'+s).encode('utf8'))
