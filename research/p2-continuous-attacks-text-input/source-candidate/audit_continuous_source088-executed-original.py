"""Static shared-condition inventory and a frozen plan; zero project imports."""
import ast
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path

OUT=Path(__file__).resolve().parent
REPO=Path('/workspace/rougezhushou')
FIELD='continuous_attacks'


def proof(path):
    b=path.read_bytes();return {'source_path':str(path),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}


get_reads=[];literal_uses=[];source_index=[];extracts={}
for path in sorted((REPO/'rouge').rglob('*.py')):
    text=path.read_text();tree=ast.parse(text);source_index.append(proof(path))
    parents={child:(node,key) for node in ast.walk(tree) for key,value in ast.iter_fields(node)
             for child in (value if isinstance(value,list) else [value]) if isinstance(child,ast.AST)}
    for node in ast.walk(tree):
        if isinstance(node,ast.Constant) and node.value==FIELD:
            literal_uses.append({'path':str(path.relative_to(REPO)),'line':node.lineno,'parent_node':type(parents[node][0]).__name__})
        if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute) and node.func.attr=='get' and node.args and isinstance(node.args[0],ast.Constant) and node.args[0].value==FIELD:
            scope=[];current=node
            while current in parents:
                parent,edge=parents[current]
                if isinstance(parent,(ast.FunctionDef,ast.ClassDef)):scope.append(parent.name)
                if isinstance(parent,ast.If):scope.append({'if':ast.unparse(parent.test),'edge':edge,'line':parent.lineno})
                current=parent
            get_reads.append({'path':str(path.relative_to(REPO)),'line':node.lineno,'expression':ast.unparse(node),'ancestry_nearest_first':scope})
    if FIELD in text:
        extracts[str(path.relative_to(REPO))]=[{'line':i,'text':line} for i,line in enumerate(text.splitlines(),1)
           if any(abs(i-hit['line'])<=3 for hit in literal_uses if hit['path']==str(path.relative_to(REPO)))]
counts=Counter(r['path'] for r in get_reads)
assert dict(counts)=={'rouge/amiya_continuous_reference.py':1,'rouge/estimate.py':3,'rouge/operator_engine.py':6,'rouge/sp_events.py':1,'rouge/timing.py':1}
assert len(get_reads)==12
catalog_path=REPO/'rouge/data/catalog.json';profiles_path=REPO/'rouge/data/operator-profiles.json'
catalog=json.loads(catalog_path.read_bytes())['operators']
char_path=REPO/'.cache/p2-s1-binding/character_table.json'
skill_path=REPO/'.cache/p2-s1-binding/skill_table.json'
assert proof(char_path)['sha256']=='68e3a3b5ee0d407ce234afaa5867c6fda6379a6843c7d5317a7bbda4779f8697'
assert proof(skill_path)['sha256']=='86f4aa64c785f39727edd06d6dd8dfc1bdaefebe36f371c8e4ace5345ba0dc61dee1386ca'.replace('86f4aa64c785f39727edd06d6dd8dfc1bdaefebe36f371c8e4ace5345ba0dc61dee1386ca','86f4aa64c785f39727edd06d6dd8a4f27f371c8e4ace5345ba0dc61dee1386ca')
chars=json.loads(char_path.read_bytes());skills=json.loads(skill_path.read_bytes())
source_selection=[]
domains=[('legacy attack-SP','mechanist',1,{}),
         ('extended actual normal','char_4182_oblvns',3,{'module_id':'uniequip_002_oblvns','module_level':3}),
         ('natural Amiya hidden condition reference','char_002_amiya',1,{'timing_mode':'continuous'}),
         ('inactive legacy natural','silverash',3,{'timing_mode':'continuous'})]
cases=[]
for label,op,number,extra in domains:
    profile=catalog[op];selected=profile['skills'][number-1];raw_char=chars[profile['id']]
    raw_skill=skills[selected['id']]['levels'][9]
    source_selection.append({'public_operator':op,'actual_character_id':profile['id'],'skill_number':number,'rank':10,
                             'raw_character_skill_entry':raw_char['skills'][number-1],
                             'raw_skill_level':raw_skill,'curated_skill_level':selected['levels'][9],
                             'native_clock_binding_claimed':False})
    for value in (False,True,'false',''):
        cases.append({'index':len(cases)+1,'label':label,'value_label':repr(value),'input':{
            'operator':op,'skill':number,'elite':2,'level':60,'skill_rank':10,'potential':6,
            'base_attack':1097,'window_seconds':17.25,'timing_mode':'frames',**extra,FIELD:value}})
assert len(cases)==16
for name in ('PROJECT_PROGRESS.md','WORK_IN_PROGRESS.md','DEVELOPMENT_CHECKPOINT.json'):
    with (OUT/('bound-'+name)).open('xb') as f:f.write((REPO/name).read_bytes())
receipt={'status':'STATIC_CONFIRMED_TEXT_TRUTHINESS_GAP_PENDING_AUTHORIZED16_PUBLIC_PROBES',
         'captured_git_HEAD':subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),
         'git_worktree_boundary':'Current approved86 source bytes may precede its commit; current file hashes are the operative source binding.',
         'field':FIELD,'actual_literal_get_count':12,'get_counts':dict(counts),'get_reads':get_reads,
         'initial_13_get_estimate_corrected_by_exhaustive_AST':True,
         'schema_training_timing_guard':'No source literal str guard or conversion for this field; public scenario remains unchanged into condition reads.',
         'builtin_truthiness_not_project_calls':{repr(v):bool(v) for v in (False,True,'false','')},
         'producer':'QCheckBox defaultTrue and isChecked bool; hidden only by current sp_type==INCREASE_WHEN_ATTACK, which is not API qualification.',
         'consumer_boundaries':[
            'Legacy estimate: Attack-SP recharge/initial, frame recharge and actual normal count. Natural-only legacy without event/attack rules is an inactive control.',
            'Extended: natural Amiya condition/reference, natural+attack_sp rules, Attack-SP branches and actual normal gate. Source get alone is insufficient to demand all-owner/all-skill rejection.',
            'Periodic charge: incoming_interval branch takes precedence; outgoing credits only in the elif continuous branch.',
            'Event charge: field affects outgoing credits only with native_attack>0, not merely presence of event-SP rules; wait_next_attack can request a stream independently.',
            'Amiya continuous reference: bool(field) persists enabled-condition metadata even while actual clock remains unknown.',
            'Current final cycle can be masked after reads; UI visibility and final cycle do not prove inactivity.'
         ],'source_index':source_index,'targeted_source_excerpts':extracts,
         'selected_original_records':source_selection,'fixed_original_sources':[proof(char_path),proof(skill_path)],
         'curated_profile_sources':[proof(catalog_path),proof(profiles_path)],
         'old_error_order':'Existing preparation/training/timing/engine/report and83–86 text errors stay before any proposed late guard. Actual public confirmation pending; no universal outer error-order claim.',
         'minimum_product_scope_pending_runtime_confirmation':'One shared text condition contract at actual consumers after existing errors, preserving legal bool/nonstring aliases and genuinely inactive fields; no new SP formula, timer or mechanics.',
         'project_API_helper_tests_Qt_Wine':0,'tracked_edits':0}
(OUT/'continuous-condition-static088.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
(OUT/'continuous-public-plan16.json').write_text(json.dumps(cases,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':receipt['status'],'literal_get_reads':12,'public_plan':16,'project_calls':0}))
