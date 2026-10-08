"""Freeze source/plan/scripts before any authorized public call."""
import ast
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent


def sha(raw):return hashlib.sha256(raw).hexdigest()


names=['PLAN092.md','source-qualification-note092.json','public-inputs092.json',
       'actual91-transport-proof092.json','maintained730-git-and-current-hashes092.json',
       'candidate/rouge/app.py','candidate/rouge/reporting.py','candidate-flow092.patch',
       'run_public092.py','native_codec092.py','prepare_author092.py',
       'root-attempt-boundary091-immutable.json','old49-manifest-immutable.json','old49-candidate-static-proof-immutable.json']
files=[]
for name in names:
    p=HERE/name;raw=p.read_bytes()
    if p.suffix=='.py':ast.parse(raw.decode(),filename=str(p))
    files.append({'source_path':str(p),'archive_path':name,'bytes':len(raw),'sha256':sha(raw)})
freeze={'format_version':1,'status':'FROZEN_ZERO_CALL_PLAN_AND_SOURCE_BEFORE_EIGHT_PUBLIC_MAX',
        'actual_root_commit':'59961ec3d633ac91b01014fb06b357d45e5979f7','actual_root_tag':'p2-section-091',
        'files':files,'file_count':len(files),
        'budget':{'baseline_public_max':4,'draft_public_max':4,'all_public_max':8,
                  'external_text_requests_max':24,'report_modes_per_success':['estimate','default','technical'],
                  'actual_internal_formatter_entries':'Profiler observed; not derived','extra_error_mirror_tests':0},
        'calls_at_freeze':{'API':0,'helper':0,'formatter':0,'tests':0,'Qt':0,'Wine':0},
        'no_fifth_case_or_cartesian':True,'root_sole_tracked_and_actual_Qt':True,
        'previous_partial_attempt_rule_failure_preserved':'root-attempt-boundary091-immutable.json',
        'only_source_statics_so_far':'Actual91+730hash/known49 verification, source qualifications, script/productAST and inheritedexactinverse; not runtime proof'}
(HERE/'pre-public-freeze092.json').write_text(json.dumps(freeze,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':freeze['status'],'freeze_sha256':sha((HERE/'pre-public-freeze092.json').read_bytes()),
                  'files':len(files),'API_before':0,'maximum_API':8,'maximum_external_texts':24}))
