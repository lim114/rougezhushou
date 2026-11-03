"""Seal already captured evidence; no new product/API/test/GUI process."""
import hashlib
import json
import subprocess
from pathlib import Path

OUT=Path(__file__).resolve().parent
ROOT=Path('/workspace/rougezhushou')
BASE='b5a40f30683bfc0945decaabbd4db5914c28427f'


def sha(data):return hashlib.sha256(data).hexdigest()


def save(name,value):
    with (OUT/name).open('x',encoding='utf-8') as stream:
        json.dump(value,stream,ensure_ascii=False,indent=2,allow_nan=False)
        stream.write('\n')


def main():
    source=json.loads((OUT/'source-preparation-complete.json').read_bytes())
    assert source['passed'] is True and source['base_commit']==BASE and source['public_calls']==0
    summary=json.loads((OUT/'first-public-probe-summary.json').read_bytes())
    assert summary['passed'] is True and summary['new_public_calls']==summary['accepted']==36 and summary['errors']==0
    rows=[json.loads(line) for line in (OUT/'first-public-probes.jsonl').read_text().splitlines()]
    assert len(rows)==36
    for index,row in enumerate(rows,1):
        assert row['index']==index and row['outcome']=='accepted'
        assert row['input_typed_before']==row['input_typed_after']
        assert row['input_unchanged'] is True and row['catalog_unchanged'] is True
        assert set(row['reports'])=={'estimate','user','technical'}
    for i,group in enumerate(summary['groups']):
        false,true,text=rows[i*3:i*3+3]
        assert false['result_typed']!=true['result_typed']
        assert true['result_typed']==text['result_typed']
        assert true['reports']==text['reports']
        assert group['bool_values_differ'] is True
        assert group['text_false_exactly_equals_true'] is True
        assert group['text_false_reports_exactly_equal_true'] is True
    excerpts=['rouge/operator_engine.py','rouge/operator_options.py','rouge/app.py','rouge/damage.py',
              'rouge/reporting.py','rouge/estimate.py','rouge/run_modifiers.py','scripts/build_catalog.py']
    exact=[]
    for name in excerpts:
        expected=subprocess.check_output(['git','-C',str(ROOT),'show',BASE+':'+name])
        data=(OUT/'source-excerpts'/name).read_bytes()
        assert data==expected,name
        exact.append({'git_path':name,'sha256':sha(data),'bytes':len(data),
                      'git_blob':subprocess.check_output(['git','-C',str(ROOT),'rev-parse',BASE+':'+name]).decode().strip()})
    save('frozen-source-excerpt-byte-proof.json',{'passed':True,'base_commit':BASE,'files':exact,'new_public_calls':0})
    save('saved-evidence-reassertion.json',{'passed':True,'saved_rows':36,'saved_groups':12,
         'new_public_calls':0,'result_typed_and_all_three_reports_exact':True,'tests_run':0,'gui_calls':0,'wine_calls':0})
    save('source-handoff.json',{'status':'source_preparation_complete_waiting_for_next_stage_authorization',
         'planned_section':86,'base_commit':BASE,'branch':'codex/p2-development',
         'source_commit':'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add','owners':8,'fields':12,
         'original_skill_levels_checked':240,'module_identity_and_parts_bindings_checked':12,
         'module_semantic_audit_repeated':False,'public_probe_calls':36,'accepted':36,'errors':0,
         'all_groups_legal_bools_differ':True,'all_text_false_results_and_three_reports_equal_true':True,
         'typed_tree_before_json_encoding':True,'all_input_and_catalog_unchanged':True,
         'tests_run':0,'gui_calls':0,'wine_calls':0,'tracked_mutations':False,'product_draft_created':False,
         'native_clock_attachment_or_unknown_mechanism_verification':False,
         'source_preparation_attempts':2,'source_preparation_failures':1,
         'source_preparation_failure_repaired':'catalog intentionally filters null-label candidates; preserve entire raw groups but compare named candidates according to frozen builder',
         'source_preparation_failure_public_calls_started':0,'product_failures':0,
         'read_discovery_path_error_preserved':True,
         'direct_field_get_consumers':17,
         'boundary_report':'CONSUMER_BOUNDARIES.md','producer_receipt':'actual-qt-producer-static-closure.json',
         'complete_original_extract':'original-eight-owner-closure.json','complete_probe_data':'first-public-probes.jsonl',
         'limits':['Only 12 qualified no-module E2 cases, 3 values per field, frames mode; not a cross-product matrix.',
                   'Original hidden scripts, attachment disputes, tick clocks, native ordering and live game behavior remain unknown.',
                   'Qualified Oblvns module override needs whole-public consumer qualification in later authorized matrix.',
                   'Existing later numerical/timing/event-SP errors must keep precedence over new string rejection.',
                   'Wait for completed full-085 and root authorization before matrix or product draft; use current root commit for any later integration.'],
         'next_action':'Wait; no additional API, tests, GUI, Wine, matrix or tracked edits authorized in this preparation.',
         'reconstructable_baseline_note':f"baseline tree omitted from public manifest; all {source['git_frozen_files']} frozen py/json byte hashes and Git blobs retained in baseline-git-object-freeze.json. Exact core source files retained as excerpts."})
    names=['prepare_source.py','prepare-source-attempt-1.py','preparation-diagnostic-attempt-1.json',
           'preparation-attempt-1.log','read-discovery-diagnostic.json','probe_existing_public.py','seal_source_handoff.py',
           'baseline-git-object-freeze.json','original-source-hash-receipt.json','original-eight-owner-closure.json',
           'actual-qt-producer-static-closure.json','frozen-public-consumer-ast.json','source-first-public-probe-plan.json',
           'source-preparation-complete.json','first-public-probes.jsonl','first-public-probe-summary.json',
           'CONSUMER_BOUNDARIES.md','frozen-source-excerpt-byte-proof.json','saved-evidence-reassertion.json','source-handoff.json']
    names += ['source-excerpts/'+name for name in excerpts]
    files=[]
    for name in names:
        data=(OUT/name).read_bytes()
        files.append({'source_path':str(OUT/name),'archive_path':name,'sha256':sha(data),'bytes':len(data)})
    save('archivable-public-manifest.json',{'format_version':1,'base_commit':BASE,
         'stage':'preparation_only_not_completed_section','files':files,
         'excluded':['baseline/** reconstructable from fixed Git objects and byte receipt','__pycache__/**'],
         'public_data_only':True,'count':len(files),'bytes':sum(row['bytes'] for row in files)})
    manifest=(OUT/'archivable-public-manifest.json').read_bytes()
    print(json.dumps({'passed':True,'files':len(files),'bytes':sum(row['bytes'] for row in files),
                      'handoff_sha256':sha((OUT/'source-handoff.json').read_bytes()),
                      'manifest_sha256':sha(manifest),'new_public_calls':0}))


if __name__=='__main__':main()
