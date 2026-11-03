"""Root-only exact108 application; Source preparation does not certify runtime.

Only two local replacements and one new test are writable. The publication and
original750 observation are actual required inputs, not fabricated future pins.
Original healthy Gold is a required separately reviewed runtime receipt.
"""
import argparse
import ast
from copy import deepcopy
import datetime
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path('/workspace/rougezhushou')
BASE = Path('/workspace/.continuation')
PACKET = BASE/'section108-active-zone-consumer-source-v1'
SELECTOR = 'tests.test_zone_environment_input_108'
TEST_PATH = 'tests/test_zone_environment_input_108.py'
ENV_PATH = 'rouge/enemy_environment.py'
CLOUD_PATH = 'scripts/verify_cloud.py'
FULL_PATH = 'scripts/verify_full_available.py'
OLD_GUARD_SHA = '409249b384daf8c38d1b7576de70ce8b5e0a4c3a387bba3da07cdb84a5f75de0'
MANIFEST_SHA = 'b30b13905de8cd94e43f7f393eff45c79d999c358727cdec9901634e22e35e4d'
TRANSPORT_SHA = '7df1d49d0927c33b59a67dc005cad7ef0fb300d92f7c75327f2839c4b2cfbb2c'
TEST_SHA = 'da7a739664f19e55186a8e12581bbb72c85a08a4d1640c9299bcd51943ba8b59'
CONSUMER_REVIEW_SHA = '01b59d0cde0ae8e8708c631b7cc31adc86a79f590930c0bf2716f2b8af385b3e'
OLD_107_TEST_SHA = '2c5eab4be5f484ca3eaf45d19eeb1f1067661a36c42ea41297a5ad1ec22ecc51'
FULL_SHA = 'ccb75fedbb97a601fb496457ad5655f9e389c2ff3d66453b23d4ada01ca2c63f'
ORIGINAL_SHA = 'caadc9ecfd748e1172820abe460735b0563210e1c25312482e0d2a541ac5a790'
GOLD_RUNNER_SHA = 'f58960664bec2b82de8446b693f9f17c9c78e48dd1ae54e72c5cf65db7204bdb'
GOLD_FACT_SHA = 'af66d1b06a98b46660a501c67144a074c330213d05c11c0241d28be63dda42d9'
GOLD_MANIFEST_SHA = 'c04d75073fb2c60c0d69190a402eeb8f9044f7e406fc57e7f36aa1359f48e9e1'
GOLD_PACKET = BASE/'section108-window-source-v2'
GOLD_FINAL_REVIEW_SHA = 'a62df7711e6c86dfaecc9e092d0f49c4c1e62037102500cc19439a20e6ea2f33'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def source_map():
    return {p.relative_to(ROOT).as_posix():sha(p.read_bytes())
            for folder in ('rouge','tests','scripts') for p in sorted((ROOT/folder).rglob('*'))
            if p.is_file() and p.suffix in ('.py','.json') and '__pycache__' not in p.parts}


def unique_assignment(tree,name):
    found = [n for n in tree.body if isinstance(n,ast.Assign)
             and any(isinstance(t,ast.Name) and t.id == name for t in n.targets)]
    assert len(found) == 1
    return found[0]


def assignment(raw,name):
    return ast.literal_eval(unique_assignment(ast.parse(raw),name).value)


def selector_union(full_raw,cloud_modules,core_raw):
    tree = ast.parse(full_raw)
    extra = ast.literal_eval(unique_assignment(tree,'NEW_MODULES').value)
    assert type(extra) is tuple and len(extra) == 41
    main = [n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name == 'main']
    assert len(main) == 1
    imports = [n for n in ast.walk(main[0]) if isinstance(n,ast.ImportFrom)
               and n.module == 'verify_cloud' and [(v.name,v.asname) for v in n.names] == [('MODULES',None)]]
    assert len(imports) == 1
    sets = [n for n in ast.walk(main[0]) if isinstance(n,ast.Assign)
            and any(isinstance(t,ast.Name) and t.id == 'selectors' for t in n.targets)]
    expected = ast.parse("list(dict.fromkeys(historical['test_modules'] + list(NEW_MODULES) + list(MODULES)))",mode='eval').body
    assert len(sets) == 1 and ast.dump(sets[0].value,include_attributes=False) == ast.dump(expected,include_attributes=False)
    historical = json.loads(core_raw)['test_modules']
    assert type(historical) is list
    return list(dict.fromkeys(historical+list(extra)+list(cloud_modules)))


def cloud_AST(original,candidate):
    old,new = ast.parse(original),ast.parse(candidate)
    before,after = unique_assignment(old,'MODULES'),unique_assignment(new,'MODULES')
    old_modules,new_modules = ast.literal_eval(before.value),ast.literal_eval(after.value)
    assert type(old_modules) is type(new_modules) is tuple
    assert len(old_modules) == 118 and len(new_modules) == 119
    assert SELECTOR not in old_modules and new_modules == (SELECTOR,)+old_modules
    after.value = deepcopy(before.value)
    assert ast.dump(old,include_attributes=False) == ast.dump(new,include_attributes=False)
    return old_modules,new_modules


def main():
    assert GOLD_FINAL_REVIEW_SHA is not None, 'Unsealed final Gold review prevents application'
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('prior-publication','original-dir','original-exit','original-runner',
                 'gold-receipt','gold-exit','gold-runner','gold-source-review'):
        parser.add_argument('--'+name,required=True)
    args = parser.parse_args()
    target = BASE/'resume108-applied-source-v1.json'
    assert not target.exists()
    assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip() == 'codex/p2-development'
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip()
    head = subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    publication_path = Path(args.prior_publication).resolve()
    assert publication_path.parent == BASE and publication_path.name.startswith('section107-publication-')
    publication_raw = publication_path.read_bytes()
    publication = json.loads(publication_raw)
    assert publication['section'] == 107 and publication['kind'] == 'ACTUAL_COMMIT_PUSH_REMOTE_EQUAL_CLEAN'
    assert publication['local_HEAD'] == publication['remote_HEAD'] == head
    assert publication['commit_primary_exit'] == publication['push_primary_exit'] == 0
    assert publication['clean'] is True and publication['source_files'] == 750 and publication['next_section'] == 108
    cp_raw = (ROOT/'DEVELOPMENT_CHECKPOINT.json').read_bytes()
    cp = json.loads(cp_raw)
    assert cp['completed_sections'] == 107 and cp['next_section'] == 108 and cp['full_validation_due'] is False
    assert cp['next_full_validation_after'] == cp['current_batch_commit_policy']['next_full_validation_after'] == 110
    closure = json.loads((ROOT/'verification/full-105/closure.json').read_bytes())
    assert cp['last_full_validation'] == cp['current_full105_checkpoint'] == closure
    assert closure['after_section'] == 105 and closure['batch_validation_closed'] is True
    assert closure['available_checks_passed'] is True and closure['full095_deferred_preserved'] is True
    assert closure['actual_gui_attempts'] == 2 and closure['actual_gui_checks'] == 4283 and closure['saved_states'] == 52
    guard_path = BASE/'resume107-applied-source-v2.json'
    guard_raw = guard_path.read_bytes()
    assert sha(guard_raw) == OLD_GUARD_SHA
    guard = json.loads(guard_raw)
    assert guard['section'] == 107 and guard['source_count'] == len(guard['source_sha256']) == 750
    assert source_map() == guard['source_sha256']
    assert guard['source_sha256']['tests/test_aglna_gravity_weight_107.py'] == OLD_107_TEST_SHA
    assert set(guard['source_additional_sha256']) == {'CORE_0.70_VERIFICATION.json'}
    core_path = ROOT/'CORE_0.70_VERIFICATION.json'
    core_raw = core_path.read_bytes()
    assert sha(core_raw) == guard['source_additional_sha256']['CORE_0.70_VERIFICATION.json']
    original_dir = Path(args.original_dir).resolve()
    original_exit = Path(args.original_exit).resolve()
    original_runner = Path(args.original_runner).resolve()
    assert original_dir == BASE/'section108-original-zone-actual-linux-v2'
    assert original_exit == BASE/(original_dir.name+'.exit-code') and original_exit.read_bytes() == b'0\n'
    original_raw = (original_dir/'observations.json').read_bytes()
    assert len(original_raw) == 640662 and sha(original_raw) == ORIGINAL_SHA
    original = json.loads(original_raw)
    original_runner_raw = original_runner.read_bytes()
    assert original['kind'] == 'ROOT_ACTUAL_ORIGINAL108_ZONE_CONSUMERS'
    assert original['observation_only'] is True and original['product_pass'] is False
    assert original['observation_complete'] is original['source_and_CORE_unchanged'] is True
    assert original['source_before'] == original['source_after'] == guard['source_sha256']
    assert original['source_guard_sha256'] == sha(guard_raw)
    assert original['CORE_before'] == original['CORE_after'] == sha(core_raw)
    assert original['runner_sha256'] == sha(original_runner_raw)
    assert original['groups'] == 8 and original['planned_calculation_cases'] == 47 and original['planned_previews'] == 8
    assert len(original['rows']) == 55 and original['actual_explicit_consumer_calls'] == len(original['calls'])
    assert original['actual_native_records'] == len(original['native_records'])
    # Original malformed consumers legitimately errored; observation0 != productPASS.
    assert original['consumer_error_count'] == sum(call['error'] is not None for call in original['calls'])
    assert original['blocked_phase_count'] == sum(len(row.get('blocked_phases',[])) for row in original['rows'])
    assert original['native_windows_verified'] is original['Qt_executed'] is original['ocr_executed'] is False
    assert original['game_chat_sampling_executed'] is original['private_state_access'] is False
    # Final frozen108 Window Source schema; actual Gold success remains required.
    gold_manifest_raw = (GOLD_PACKET/'SOURCE_MANIFEST.json').read_bytes()
    assert sha(gold_manifest_raw) == GOLD_MANIFEST_SHA
    gold_manifest = json.loads(gold_manifest_raw)
    assert gold_manifest['STOPWRITE'] is True and gold_manifest['Runtime_executed'] is gold_manifest['product_pass'] is False
    assert len(gold_manifest['payloads']) == 10
    for name,pin in gold_manifest['payloads'].items():
        payload = (GOLD_PACKET/name).read_bytes()
        assert len(payload) == pin['bytes'] and sha(payload) == pin['sha256']
    gold_review_path = Path(args.gold_source_review).resolve()
    gold_review_raw = gold_review_path.read_bytes()
    assert sha(gold_review_raw) == GOLD_FINAL_REVIEW_SHA
    gold_path = Path(args.gold_receipt).resolve()
    gold_exit = Path(args.gold_exit).resolve()
    gold_runner = Path(args.gold_runner).resolve()
    gold_raw = gold_path.read_bytes()
    gold = json.loads(gold_raw)
    gold_runner_raw = gold_runner.read_bytes()
    assert gold_exit.read_bytes() == b'0\n'
    assert gold['kind'] == 'ROOT_ACTUAL_108_REAL_MAINWINDOW'
    assert gold['phase'] == 'gold' and gold['passed'] is gold['workflow_complete'] is True
    assert gold['runner_sha256'] == sha(gold_runner_raw) == GOLD_RUNNER_SHA
    assert assignment(gold_runner_raw,'FACT_SHA') == gold['fixture_facts_sha256'] == GOLD_FACT_SHA
    assert assignment(gold_runner_raw,'ORIGINAL_SHA') == gold['original_receipt_sha256'] == ORIGINAL_SHA
    assert assignment(gold_runner_raw,'ORIGINAL_GUARD_SHA') == gold['original_guard_sha256'] == OLD_GUARD_SHA
    assert assignment(gold_runner_raw,'TRANSPORT_SHA') == gold['transport_sha256'] == TRANSPORT_SHA
    assert gold['original_raw_exit_sha256'] == sha(original_exit.read_bytes())
    assert gold['source_guard_sha256'] == sha(guard_raw)
    assert gold['source_before'] == gold['source_after'] == guard['source_sha256']
    assert gold['source_additional_before'] == gold['source_additional_after'] == guard['source_additional_sha256']
    assert gold['source_drift'] == gold['Qt_errors'] == []
    assert gold['native_windows_verified'] is gold['game_chat_sampling_executed'] is gold['private_state_access'] is False
    assert len(gold['rows']) == 43 and len(gold['windows']) == 2 and gold['pngs'] == []
    assert gold['natural_OCR_producer_verified'] is gold['malformed_saved_cache_admission_claimed'] is False
    manifest_raw = (PACKET/'SOURCE_MANIFEST.json').read_bytes()
    assert sha(manifest_raw) == MANIFEST_SHA
    manifest = json.loads(manifest_raw)
    assert manifest['STOPWRITE'] is True and manifest['Runtime_executed'] is manifest['product_pass'] is False
    assert len(manifest['files']) == 7
    assert {p.name for p in PACKET.iterdir() if p.is_file()} == set(manifest['files'])|{'SOURCE_MANIFEST.json'}
    for name,pin in manifest['files'].items():
        raw = (PACKET/name).read_bytes()
        assert len(raw) == pin['bytes'] and sha(raw) == pin['sha256']
    review_path = BASE/'section108-active-zone-candidate-independent-source-v1/review.json'
    review_raw = review_path.read_bytes()
    assert sha(review_raw) == CONSUMER_REVIEW_SHA
    review = json.loads(review_raw)
    assert review['Source_only'] is True and review['runtime_pass'] is review['product_pass'] is False
    assert review['packet_manifest']['sha256'] == MANIFEST_SHA
    transport_raw = (PACKET/'exact-local-transports.json').read_bytes()
    assert sha(transport_raw) == TRANSPORT_SHA
    transport = json.loads(transport_raw)
    assert transport['STOPWRITE'] is True and transport['Runtime_executed'] is transport['product_pass'] is False
    assert len(transport['replacements']) == 2 and len(transport['add_files']) == 1
    assert {change['path'] for change in transport['replacements']} == {ENV_PATH,CLOUD_PATH}
    assert transport['add_files'] == [{'path':TEST_PATH,'packet_file':Path(TEST_PATH).name,'Root_must_require_absent':True}]
    assert not (ROOT/TEST_PATH).exists()
    outputs = {}
    originals = {}
    for change in transport['replacements']:
        name = change['path']
        current = (ROOT/name).read_bytes()
        assert len(current) == change['before_bytes'] and sha(current) == change['before_sha256']
        before,after = change['before'].encode(),change['after'].encode()
        assert change['exact_occurrences'] == current.count(before) == 1 and current.count(after) == 0
        composed = current.replace(before,after,1)
        assert composed.count(after) == 1 and composed.replace(after,before,1) == current
        assert len(composed) == change['after_bytes'] and sha(composed) == change['after_sha256']
        outputs[name] = composed
        originals[name] = current
    test_raw = (PACKET/Path(TEST_PATH).name).read_bytes()
    assert len(test_raw) == 12998 and sha(test_raw) == TEST_SHA
    methods = [n.name for n in ast.walk(ast.parse(test_raw)) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')]
    assert len(methods) == len(set(methods)) == 16
    outputs[TEST_PATH] = test_raw
    old_modules,new_modules = cloud_AST(originals[CLOUD_PATH],outputs[CLOUD_PATH])
    full_raw = (ROOT/FULL_PATH).read_bytes()
    assert sha(full_raw) == FULL_SHA == guard['source_sha256'][FULL_PATH]
    old_union,new_union = selector_union(full_raw,old_modules,core_raw),selector_union(full_raw,new_modules,core_raw)
    assert SELECTOR not in old_union and new_union.count(SELECTOR) == 1
    assert len(old_union) == 241 and len(new_union) == 242
    assert [item for item in new_union if item != SELECTOR] == old_union
    assert set(outputs) == {ENV_PATH,CLOUD_PATH,TEST_PATH} and FULL_PATH not in outputs
    for name,raw in outputs.items():
        compile(raw,name,'exec')
    compile(original_runner_raw,str(original_runner),'exec')
    compile(gold_runner_raw,str(gold_runner),'exec')
    assert source_map() == guard['source_sha256'] and guard_path.read_bytes() == guard_raw
    assert core_path.read_bytes() == core_raw and (ROOT/FULL_PATH).read_bytes() == full_raw
    assert (ROOT/'DEVELOPMENT_CHECKPOINT.json').read_bytes() == cp_raw
    # All actual publication/current original/Gold and Source gates precede writes.
    for name,raw in outputs.items():
        (ROOT/name).write_bytes(raw)
    after = source_map()
    assert len(after) == 751 and set(after)-set(guard['source_sha256']) == {TEST_PATH}
    assert not set(guard['source_sha256'])-set(after)
    assert {name for name in guard['source_sha256'] if after[name] != guard['source_sha256'][name]} == {ENV_PATH,CLOUD_PATH}
    assert all(after[name] == sha(raw) for name,raw in outputs.items())
    assert guard_path.read_bytes() == guard_raw and core_path.read_bytes() == core_raw
    assert (ROOT/FULL_PATH).read_bytes() == full_raw and (ROOT/'DEVELOPMENT_CHECKPOINT.json').read_bytes() == cp_raw
    receipt = {'section':108,'status':'ACTUALLY_APPLIED_RUNTIME_PENDING','baseline_HEAD':head,
        'actual_prior_publication':publication,'actual_prior_publication_sha256':sha(publication_raw),
        'applied_at_Beijing':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),
        'source_sha256':after,'source_additional_sha256':guard['source_additional_sha256'],'source_count':751,
        'changed_paths':sorted(outputs),'applier_source_sha256':sha(Path(__file__).read_bytes()),
        'prior_complete_source_guard_sha256':sha(guard_raw),'candidate_packet_manifest_sha256':sha(manifest_raw),
        'exact_local_transport_sha256':sha(transport_raw),'consumer_independent_source_review_sha256':sha(review_raw),
        'original_actual_zone_observations_path':str(original_dir/'observations.json'),
        'original_actual_zone_observations_sha256':sha(original_raw),'original_source_count':750,
        'original_actual_consumer_calls':original['actual_explicit_consumer_calls'],
        'original_actual_native_records':original['actual_native_records'],
        'original_actual_consumer_errors_preserved':original['consumer_error_count'],
        'original_actual_blocked_phases_preserved':original['blocked_phase_count'],
        'actual_healthy_Gold_receipt_path':str(gold_path),'actual_healthy_Gold_receipt_sha256':sha(gold_raw),
        'actual_healthy_Gold_windows':len(gold['windows']),'actual_healthy_Gold_snapshots':len(gold['rows']),
        'window_source_sha256':sha(gold_runner_raw),'window_facts_sha256':GOLD_FACT_SHA,
        'window_packet_manifest_sha256':sha(gold_manifest_raw),'window_independent_Source_review_sha256':sha(gold_review_raw),
        'test_source_sha256':sha(test_raw),'test_methods':16,'cloud_selectors_before':118,'cloud_selectors_after':119,
        'full_NEW_MODULES_unchanged':True,'full_helper_source_sha256_unchanged':sha(full_raw),
        'full_selector_union_before':241,'full_selector_union_after':242,
        'registry_choice':'Cloud-only prepend; unchanged full main already unions cloudMODULES with historical and NEW41.',
        'scope':['Active malformed zone container and unhashable ID fail explicitly; original falsey/inactive/known/portal precedence preserved',
                 'No cache schema relaxation, guessed main depth, new growth mechanism or caller normalization'],
        'runtime_checks_passed_claimed':False,'native_windows_verified':False}
    with target.open('x',encoding='utf-8') as stream:
        json.dump(receipt,stream,ensure_ascii=False,indent=2)
        stream.write('\n')
    print(json.dumps({'section':108,'applied':True,'source_files':len(after),'cloud_selectors':119,
                      'changed_paths':sorted(outputs),'runtime_checks_passed_claimed':False}))


if __name__ == '__main__':
    main()
