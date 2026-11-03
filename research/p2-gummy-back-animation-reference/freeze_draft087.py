import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parent
TREE=ROOT/'draft';BASELINE=ROOT/'baseline';PROJECT=Path('/workspace/rougezhushou')
TARGETS=['rouge/data/original-animation-references.json','tests/test_original_animation_048.py','tests/test_gummy_back_animation_reference.py']
RELATED=['tests.test_original_animation_048','tests.test_gummy_cooking_clock','tests.test_gummy_expected_clock','tests.test_next_attack_healing_reference','tests.test_friendly_scope_report']
sha=lambda raw:hashlib.sha256(raw).hexdigest()
source=[]
for rel in TARGETS:
    new=(TREE/rel).read_bytes()
    old_path=BASELINE/rel
    old=old_path.read_bytes() if old_path.exists() else None
    current_path=PROJECT/rel
    current=current_path.read_bytes() if current_path.exists() else None
    assert current==old,rel
    source.append({'path':rel,'draft_source_path':str(TREE/rel),'draft_bytes':len(new),'draft_sha256':sha(new),
      'baseline_bytes':len(old) if old is not None else None,'baseline_sha256':sha(old) if old is not None else None,
      'root_current_matches_baseline':True,'line_endings':'CRLF' if b'\r\n' in new else 'LF'})
unchanged=[]
for rel in ('rouge/animation_reference.py','rouge/timing.py','rouge/damage.py','rouge/operator_engine.py','rouge/estimate.py','rouge/reporting.py','scripts/build_original_animation_048.py','scripts/build_animation_selection_048.py'):
    old=(BASELINE/rel).read_bytes();new=(TREE/rel).read_bytes()
    assert old==new,rel
    unchanged.append({'path':rel,'bytes':len(new),'sha256':sha(new)})
patch=(ROOT/'product087.patch').read_bytes()
expected=set(TARGETS)
headers=[line.decode() for line in patch.splitlines() if line.startswith(b'diff --git ')]
assert len(headers)==3
for rel in TARGETS:assert 'diff --git a/'+rel+' b/'+rel in headers
counts=json.loads((ROOT/'matrix-comparison-receipt.json').read_text())
receipt={'version':1,'status':'AUTHOR_FROZEN_FORMAL_PENDING','frozen_at':datetime.now(timezone.utc).isoformat(),
    'author_baseline_commit':'9ef5a469673502754db3be320a8eece9a7fd18d4',
    'root_current_commit_at_apply_check':subprocess.check_output(['git','-C',str(PROJECT),'rev-parse','HEAD'],text=True).strip(),
    'source_files':source,'unchanged_author_consumer_sources':unchanged,
    'patch':{'source_path':str(ROOT/'product087.patch'),'bytes':len(patch),'sha256':sha(patch),'headers':headers,'root_apply_check_exit':0,'root_mutation_performed':False},
    'registry_proposal':{'path':'scripts/verify_cloud.py','new_MODULES_entry':'tests.test_gummy_back_animation_reference','registration_applied_in_author_or_root':False,'scope':'Root adds exactly one module while preserving the independent86 registry update; registry is not included in this patch'},
    'tests':{'new_module':'tests.test_gummy_back_animation_reference','new_tests':7,'new_passed':7,'new_API_calls_by_call_sites':11,
        'related_modules':RELATED,'related_tests':38,'related_passed':37,'historical_cache_skips':1,'related_API_calls':56},
    'matrix':counts,'initial_public_inspection_API_calls':4,'author_total_fresh_API_calls_so_far':138,
    'source_parser_and_download_calls_in_product_stage':0,'root_tracked_changes':0,'Qt_Wine_calls':0,
    'failed_preparation':'One plain Git diff --check false positive on retained CRLF, corrected with explicit cr-at-eol; no source/test change or API rerun. Optional local absent-path queries are recorded separately.',
    'source_packet_immutable':{'manifest_sha256':'db2679793321d9d4a0f817757c53d93f88a16c4d4261f65f54223f69fb8b5265','handoff_sha256':'c0d718050a376bac2a4fee314e8629aa01e65518f5e467501f5ef21a0aed04af'},
    'no_native_or_EOF_render_historical_root_cause_claim':True}
(ROOT/'author-freeze087.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'frozen_source':source,'patch_sha256':sha(patch),'API_calls':138},ensure_ascii=False))
