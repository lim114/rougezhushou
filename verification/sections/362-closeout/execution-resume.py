from pathlib import Path
import json
path=Path('.cache/close362.py');s=path.read_text('utf8')
existing=json.loads(Path('verification/sections/362.json').read_bytes())
assert json.loads(Path('DEVELOPMENT_CHECKPOINT.json').read_bytes())['completed_sections']==361
for name in('AGENTS.md','PROJECT_COMPLETED.md','WORK_IN_PROGRESS.md','PROJECT_REQUIREMENTS.md'):
 assert Path(name).read_text('utf8').count('<!-- section362-publication-pending -->')==1,name
prefix=s[:s.index("(ROOT/'verification/sections/362.json').write_bytes")]
ns={'__file__':str(path.resolve()),'__name__':'__closeout_resume__'};exec(compile(prefix,str(path), 'exec'),ns)
ns['now']=existing['at_Beijing'];ns['r']=existing
ns['details']=ns['change']+'\n\n'+ns['validation']+'\n\n'+ns['limits']+'\n\n'+ns['pending']
tail=s[s.index("s=(ROOT/'PROJECT_PROGRESS.md').read_text('utf8')"):]
exec(compile(tail,str(path)+'[resume-after-documents]', 'exec'),ns)
out=Path('verification/sections/362-closeout')
(out/'execution-resume.py').write_bytes(Path(__file__).read_bytes())
(out/'first-closeout-failure.json').write_text(json.dumps({'section':362,'first_attempt_error':'IndexError: list index out of range in todo-row lookup','reason':'Markdown non-table lines were not filtered','partial_public_documents_preserved':True,'previously_written_four_documents_not_repeated':True,'checkpoint_was_still361_before_resume':True,'private_state_untouched':True,'recovery':'Filter table rows and resume only from remaining todo/checkpoint/index portion'},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
