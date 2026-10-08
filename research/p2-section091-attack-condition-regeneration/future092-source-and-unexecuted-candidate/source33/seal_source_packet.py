"""Metadata seal only, no project execution."""
from pathlib import Path
import hashlib
import json

HERE=Path(__file__).resolve().parent


def sha(raw):return hashlib.sha256(raw).hexdigest()


binding=json.loads((HERE/'fixed-source-binding.json').read_text())
for item in binding['sources']:
    raw=Path(item['archive_path']).read_bytes()
    assert len(raw)==item['bytes'] and sha(raw)==item['sha256']
handoff={
    'format_version':1,'status':'FINAL_SOURCE_ONLY_CANDIDATE_IMMUTABLE_NOT_COMPLETED_SECTION',
    'directory':str(HERE),'fixed_root_commit':binding['actual_root_commit'],
    'findings':str(HERE/'source-findings.json'),'path_contract':str(HERE/'path-contract.json'),
    'producer_AST':str(HERE/'actual-Qt-producer-and-all-references.json'),
    'historical_finite_receipt':'historical-finite085-guard-receipt.json; original only, not reexecuted',
    'manifest':str(HERE/'public-source-manifest.json'),
    'complete_frozen_source_files':len(binding['sources']),
    'candidate_products_or_runtime_results_in_this_source_packet':False,
    'new_calls':{'API':0,'helper':0,'formatter':0,'constructor':0,'tests':0,'Qt':0,'Wine':0},
    'tracked_mutation':False,'native_mechanism_or_clock_invented':False,
    'positive_scope':'Window input refresh + explicit zero/effective observation length + exact range/mode tooltip workflow',
    'negative_scope':'Existing guards/alias histories retained; no new positive finite-window arithmetic bug confirmed',
    'external_candidate_dependency':'Prospective external UI/report projection only; preserve finalized91 app/report changes and require actual91 root transport before formal/API/Qt',
    'failures':'Original source transport128 + excerpt boundary1 + two read-only partner metadata preparation diagnostics preserved; each distinct issue1failure, zero product calls',
    'stopwrite':True
}
(HERE/'source-handoff.json').write_text(json.dumps(handoff,ensure_ascii=False,indent=2)+'\n')
files=[]
for p in sorted(HERE.rglob('*')):
    if p.is_file() and p.name!='public-source-manifest.json':
        raw=p.read_bytes();files.append({'source_path':str(p),'archive_path':p.relative_to(HERE).as_posix(),
                                        'bytes':len(raw),'sha256':sha(raw)})
mf={'format_version':1,'status':'FINAL_SOURCE_ONLY_WORKFLOW_CANDIDATE_STOPWRITE_NOT_COMPLETED_SECTION',
    'files':files,'file_count':len(files),'total_bytes':sum(f['bytes'] for f in files),
    'new_API_helper_formatter_ctor_tests_Qt_Wine_calls':0,'manifest_itself_excluded':True}
(HERE/'public-source-manifest.json').write_text(json.dumps(mf,ensure_ascii=False,indent=2)+'\n')
for f in files:
    r=(HERE/f['archive_path']).read_bytes();assert len(r)==f['bytes'] and sha(r)==f['sha256']
print(json.dumps({'status':'SOURCE_FINAL_STOPWRITE','files':len(files),'bytes':mf['total_bytes'],
                  'manifest_sha256':sha((HERE/'public-source-manifest.json').read_bytes()),
                  'handoff_sha256':sha((HERE/'source-handoff.json').read_bytes()),'new_calls':0}))
