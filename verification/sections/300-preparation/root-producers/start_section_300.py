import json, subprocess
from pathlib import Path
from datetime import datetime, timezone
from hashlib import sha256

ROOT = Path(__file__).resolve().parents[1]
def read(name): return json.loads((ROOT / name).read_bytes())
def write(name, data):
    (ROOT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf8')

assert subprocess.check_output(['git','branch','--show-current'], cwd=ROOT, text=True).strip() == 'codex/p2-development'
assert not subprocess.check_output(['git','status','--porcelain'], cwd=ROOT)
head = subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip()
assert head == '796c5d406a8d4ac36d924ce6d70db9081267ef68'
cp = read('DEVELOPMENT_CHECKPOINT.json')
assert cp['completed_sections'] == 299 and cp['next_section'] == 300
proof = read('verification/sections/299-publication.json')
assert proof['passed'] and proof['commit'] == '982edb2b6f3b54bec43345d019266eccb9e2317a'
target = ROOT / 'verification/sections/300-preparation'
assert not target.exists()
target.mkdir(parents=True)
before = target / 'before'
before.mkdir()
for name in ('DEVELOPMENT_CHECKPOINT.json','WORK_IN_PROGRESS.md','rouge/node_catalog_view.py'):
    dest = before / name
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes((ROOT/name).read_bytes())
scope = {'section':300,'kind':'functional_scope_before_implementation',
 'started_utc':datetime.now(timezone.utc).isoformat(),'parent_commit':head,
 'remaining_item':'P3节点事件与掉落：已绑定选项的后续条件效果与奖励资料',
 'new_capability':'呼吸的红苔两个精确选项，手动查阅下一地区希望的沃土的三档属性与战胜随机零件说明；按已知正常难度标注文献阶段，保留实际生成、附着与奖励未知。',
 'acceptance':['两项完整身份与原文分别绑定，不补空原入口、不把说明段或快逃当选项。',
   '正常2–5、6–11、12–15文献阶段与三档攻击/生命值可查；未知、0/1、非法难度和非正常模式不默认阶段。',
   '直接资源、下一区域条件属性、战胜随机零件分别说明；不造实际节点、完整池、数量、生成概率或实际领取。',
   '默认不选；仅目标事件提供入口；同范围刷新保留页签、选区、非零滚动，跨范围或来源失效清旧信息，恢复后不自动选回。',
   '旧38事件/190场景资源、资格、17typed与原目录数据不改；独立窗口读数不改干员计算和本局记忆。',
   '相关必要检查与真实Windows窗口验证；每节源码、回执、要求与索引普通推送并实际核对远端。'],
 'excluded':['安眠跨事件确定排程','当前服务器实际生成或执行绑定','低难度强制天气的生成/阶段结论','路线建议','天气注入预计面板','识别优化'],
 'supporting_evidence_audit':'.cache/p3-300-evidence-audit/READY.json',
 'supporting_evidence_audit_sha256':sha256((ROOT/'.cache/p3-300-evidence-audit/READY.json').read_bytes()).hexdigest(),
 'source_supported_phase_reference_only':True,'current_server_execution_verified':False,
 'necessary_full_suite_rerun':False,'last_full_section':290,'next_full_section':305,
 'numeric_endpoint':None,'P3_complete':False}
write('verification/sections/300-preparation/scope.json',scope)
cp['active_section'] = {'section':300,'scope':'verification/sections/300-preparation/scope.json',
 'status':'implementation_not_yet_completed','functional_progress_claimed':False}
write('DEVELOPMENT_CHECKPOINT.json',cp)
old = (ROOT/'WORK_IN_PROGRESS.md').read_text(encoding='utf8')
(ROOT/'WORK_IN_PROGRESS.md').write_text('## 第300节进行中 · 红苔选择的下一地区影响\n\n仅按完整资料提供三档属性、文献阶段与条件奖励的手动阅读；实际生成与领取未知。尚未完成或发布，范围见 verification/sections/300-preparation/scope.json。\n\n' + old, encoding='utf8')
print(json.dumps({'section':300,'scope_saved_before_implementation':True,'parent_commit':head,'next_full':305}))
