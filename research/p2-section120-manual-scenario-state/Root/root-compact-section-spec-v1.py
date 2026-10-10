"""Root prepares an explicit public archive list; actual save/push stay separate."""
import argparse,json
from pathlib import Path
p=argparse.ArgumentParser()
for k in ('section','guard','topic','slug','summary','next-action'):p.add_argument('--'+k,required=True)
for k in ('exit','receipt','packet','file','actual'):p.add_argument('--'+k,action='append',default=[])
a=p.parse_args();n=int(a.section);B=Path('/workspace/.continuation')
def located(name):
 q=(B/name).resolve();assert B in q.parents and q.exists() and not q.is_symlink();return q
entries=[]
def add(q,d):
 assert q.is_file() and not q.is_symlink();assert '__pycache__' not in q.parts and 'public-state' not in q.parts
 entries.append({'source':str(q),'destination':d})
for kind,names in (('Source',a.packet),('Actual',a.actual)):
 for name in names:
  base=located(name);assert base.is_dir()
  for q in sorted(base.rglob('*')):
   if q.is_file() and '__pycache__' not in q.parts and 'public-state' not in q.parts:add(q,kind+'/'+name+'/'+q.relative_to(base).as_posix())
for name in dict.fromkeys([*a.file,*a.exit,*a.receipt,a.guard,'root-compact-section-spec-v1.py','root-section-publish-v3.py']):add(located(name),'Root/'+name)
previous=f'section{n-1:03d}-publication-v1.json';add(located(previous),'prior-publication.json')
assert len({x['destination'] for x in entries})==len(entries)
archive=f'research/p2-section{n:03d}-{a.slug}'
spec={'section':n,'source_guard':str(located(a.guard)),'archive':archive,'topic':a.topic,'public_evidence':entries,
 'exit_files':[str(located(x)) for x in a.exit],'pass_receipts':[str(located(x)) for x in a.receipt],
 'previous_publication':str(located(previous)),
 'section_receipt':{'functional_changes':[a.summary],'validation_scope':'相关 Linux/Wine 回归、实际公开调用和真实窗口；证据逐项封存。测试为功能修复附加验证。','native_windows_game_chat_verified':False},
 'archive_readme':a.summary+'\n\n逐项原始终码、原件/候选、完整实际调用及窗口记录在此归档；Wine 是兼容验证。原生Windows、游戏、聊天和未迁移样本仍未验证。',
 'next_action':a.next_action,
 'completed_paragraph':a.summary+' 本节相关检查和窗口检验已闭合，原始证据见 '+archive+'；准备真实逐节commit/push。',
 'work_paragraph':a.summary+' 本节检查及公开证据已封存，下一步：'+a.next_action}
out=B/f'root-section{n:03d}-save-spec-v1.json';assert not out.exists();out.write_text(json.dumps(spec,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'section':n,'explicit_public_files':len(entries),'saved':False,'commit_created':False}))
