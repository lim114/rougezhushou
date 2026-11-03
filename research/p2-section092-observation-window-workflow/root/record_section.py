import json,sys,subprocess
from pathlib import Path
from datetime import datetime,timezone
s=json.loads(Path(sys.argv[1]).read_text());n=s['number'];ref=f'p2-section-{n:03d}';receipt=f'verification/sections/{n:03d}.json'
assert subprocess.check_output(['git','branch','--show-current'],text=True).strip()=='codex/p2-development'
cp=json.loads(Path('DEVELOPMENT_CHECKPOINT.json').read_text());assert cp['completed_sections']==n-1
Path(receipt).write_text(json.dumps({'section':n,'completion_ref':ref,'branch':'codex/p2-development','validated_at':datetime.now(timezone.utc).isoformat(),**s['verification']},ensure_ascii=False,indent=2)+'\n')
cp['sections'].append({'number':n,'completion_ref':ref,'topic':s['topic'],'verification':receipt})
cp.update(completed_sections=n,next_section=n+1,next_action=s['next_action'],full_validation_due=n%5==0)
Path('DEVELOPMENT_CHECKPOINT.json').write_text(json.dumps(cp,ensure_ascii=False,indent=2)+'\n')
def edit(name,fn):
 p=Path(name);b=p.read_bytes();text=b.decode().replace('\r\n','\n');new=fn(text);p.write_bytes(new.replace('\n','\r\n').encode() if b'\r\n' in b else new.encode())
edit('WORK_IN_PROGRESS.md',lambda old:f'# 连续开发断点 · 第 {n} 节完成\n\n`codex/p2-development`，标签 `{ref}`。'+s['summary']+f'\n\n下一步：{s["next_action"]}。每五节全量检验后自动继续下一组，不等用户消息。P2完成后转P3；同问题三次未解决则搁置；低于15%额度完成当前检验后收尾，目前无额度API。见 `{receipt}` 与 `DEVELOPMENT_CHECKPOINT.json`。\n\n---\n\n'+old)
edit('PROJECT_COMPLETED.md',lambda old:f'# 连续开发 {n:03d} · {s["topic"]}\n\n'+s['summary']+f' 见 `{receipt}`。\n\n---\n\n'+old)
edit('BATCH_CONTINUOUS_P2.md',lambda old:old+f'\n## {n:03d} · {s["topic"]}\n\n'+s['summary']+f'\n\n验证 `{receipt}`。'+s.get('limitations','')+'\n')
