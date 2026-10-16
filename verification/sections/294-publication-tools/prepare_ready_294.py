"""Only syntax, source selection, and public-receipt schema checks; no output tool runs."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import ast,json
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def load(p):return json.loads((ROOT/p).read_bytes())
scripts=['stage_section_294.py','push_section_294.py','verify_publication_294.py','finish_publication_294.py']
for name in scripts:
    source=(HERE/name).read_text(encoding='utf8')
    ast.parse(source,filename=name)
    assert 'parents[2]'in source
    assert '6b59ad14e30226fab12d1f3447da96b80208ff63'not in source
    assert "['git','commit'"not in source and '--force'not in source
assert "'HEAD:refs/heads/codex/p2-development'"in(HERE/'push_section_294.py').read_text()
assert "new=[name for name in promotion['promoted']"in(HERE/'stage_section_294.py').read_text()
section=load('verification/sections/294.json')
necessary=load(section['necessary_validation']['receipt'])
native=load(section['native_windows_validation']['receipt'])
assert section['section']==294 and section['prior_commit']=='48eeb454e23fffee084fe7b6c7f9667b9216131d'
assert section['cloud_published']is False and section['next_section']==295
assert necessary['exit_code']==0 and native['passed']is True
for value in (necessary,native):
    assert value['source_sha256_before']==value['source_sha256_after']
    for name,digest in value['source_sha256_after'].items():
        assert not name.startswith(('.cache/','.local/')) and name!='local-settings.json'
        assert sha256((ROOT/name).read_bytes()).hexdigest()==digest
assert len(native['checks'])==native['unique_checks']
assert isinstance(native['successful_assertion_executions_including_repeated_guards'],int)
assert section['partial_scope_after']==[10,18,58]
assert section['whole_map_stage_image_gaps_unchanged']==[81,59]
assert section['full_validation']['after_section']==290 and section['full_validation']['full_suite_rerun']is False
names=scripts+['prepare_tools_294.py','prepare_ready_294.py','RUN_PLAN.md','BASELINE.json','first-preparation-tool-error.json']
result={'kind':'SECTION294_PUBLICATION_CACHE_PREPARATION_ONLY','prepared_utc':datetime.now(timezone.utc).isoformat(),
 'static_AST_and_current_public_receipt_schema_checked':True,'publication_tools_executed':False,
 'Git_mutations_or_push_or_GUI_tests_executed_by_preparation':False,
 'parent_commit':'48eeb454e23fffee084fe7b6c7f9667b9216131d',
 'functional_commit':None,'metadata_commit':None,'remote_ref':None,'publication_passed':None,
 'observed_existing_validation_only':{'necessary_methods':section['necessary_validation']['methods_run'],
  'necessary_source_files':len(necessary['source_sha256_after']),'native_unique_checks':native['unique_checks'],
  'native_repeated_assertions':native['successful_assertion_executions_including_repeated_guards'],
  'native_source_files':len(native['source_sha256_after'])},
 'files':{name:{'sha256':sha256((HERE/name).read_bytes()).hexdigest(),'bytes':(HERE/name).stat().st_size}for name in names},
 'first_preparation_errors_preserved':'first-preparation-tool-error.json'}
with(HERE/'READY.json').open('xb')as f:f.write((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode())
print(json.dumps({'cache_preparation_only':True,'all_four_scripts_AST_valid':True,
 'actual_publication_or_Git_mutation':False,'READY_sha256':sha256((HERE/'READY.json').read_bytes()).hexdigest()}))
