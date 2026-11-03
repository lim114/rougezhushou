"""Apply only the frozen thirteen connections after actual section93 acceptance."""
from pathlib import Path
import ast
import hashlib
import json
import subprocess
import sys

ROOT = Path('/workspace/rougezhushou')
LOCAL = Path('/workspace/.continuation')
CANDIDATE = LOCAL / 'p2-offline-input-refresh-candidate094-v1'
BASE_HEAD = 'f509d186e501bfcfd042e45b46e398ec756840ec'
GUARD_SHA = '0fbfe28e2528ae9987f9f260bfed0068b1e16edf02274ea3349cd6d988aa2180'
MANIFEST_SHA = '31d2ea82865edcaf21bac24f81174b991a8bd92dd208223ac47f8dfee275659c'
REVIEW_SHA = '3fa43a592d90ff70670f3aa682c4ff17cda595afbb979ec78c11007a68dd3d35'
APP_BEFORE = '3dd6810e3398471ddb6dbe9545824c7b92ba4d141fc23f889287a8044670a48f'
APP_AFTER = '589b9ac2b846206581c394d037baec0d9e43a165a7bdd5becc0982ab0e09c0fd'
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def save_new(path, data):
    with path.open('x') as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
def maintained():
    return {p.relative_to(ROOT).as_posix(): digest(p) for base in ('rouge', 'tests', 'scripts')
        for p in sorted((ROOT/base).rglob('*')) if p.is_file() and p.suffix in ('.py', '.json') and '__pycache__' not in p.parts}
def base_gate():
    assert subprocess.check_output(['git', 'branch', '--show-current'], cwd=ROOT, text=True).strip() == 'codex/p2-development'
    assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip() == BASE_HEAD
    guard_path = LOCAL / 'root-source-093.json'
    assert digest(guard_path) == GUARD_SHA
    guard = json.loads(guard_path.read_bytes())
    assert guard['passed'] is True and guard['current_maintained'] == 732
    assert maintained() == guard['source_sha256_after']
    assert digest(ROOT/'rouge/app.py') == APP_BEFORE
    return guard
def candidate_gate():
    mf = CANDIDATE/'public-manifest094.json'
    assert digest(mf) == MANIFEST_SHA
    for rel, item in json.loads(mf.read_bytes())['artifacts'].items():
        path = CANDIDATE/rel
        assert path.resolve().is_relative_to(CANDIDATE.resolve())
        assert path.stat().st_size == item['bytes'] and digest(path) == item['sha256']
    review = CANDIDATE/'review-independent094.json'
    assert digest(review) == REVIEW_SHA
    proof = json.loads(review.read_bytes())
    assert proof['static_review_passed'] is True and all(proof['checks'].values())
    base = (CANDIDATE/'base/rouge/app.py').read_bytes()
    new = (CANDIDATE/'candidate/rouge/app.py').read_bytes()
    inverse = json.loads((CANDIDATE/'inverse094.json').read_bytes())
    inserted = inverse['insertion_utf8_LF'].replace('\n', '\r\n').encode()
    assert len(inserted.splitlines()) == 13 and len(inserted) == 945
    assert hashlib.sha256(inserted).hexdigest() == inverse['insertion_bytes_CRLF_sha256']
    assert new.count(inserted) == 1 and new.replace(inserted, b'', 1) == base
    assert hashlib.sha256(base).hexdigest() == APP_BEFORE and hashlib.sha256(new).hexdigest() == APP_AFTER
    assert ast.dump(ast.parse(new.replace(inserted, b'', 1).decode()), include_attributes=False) == ast.dump(ast.parse(base.decode()), include_attributes=False)
    return new
def completed93_gate(path, sha, closure_path, closure_sha):
    assert digest(path) == sha and digest(closure_path) == closure_sha
    receipt = json.loads(path.read_bytes())
    closure = json.loads(closure_path.read_bytes())
    assert receipt['section'] == closure['section'] == 93
    assert receipt['actual_window_verified_by_root'] is True
    assert receipt['actual_states'] == 132 and receipt['actual_fresh_MainWindows'] == 31
    assert closure['status'] == 'VERIFIED_ARCHIVED_NOT_COMMITTED_OR_PUSHED'
    assert closure['all_archive_index_blobs_exact'] is True
    assert closure['actual_HEAD_unchanged'] == BASE_HEAD and closure['source_snapshot_sha256'] == GUARD_SHA
    archive = ROOT/receipt['research_archive']
    mf = archive/'archive-manifest.json'
    assert digest(mf) == closure['archive_manifest_sha256']
    for rel, item in json.loads(mf.read_bytes()).items():
        p = archive/rel
        assert p.stat().st_size == item['bytes'] and digest(p) == item['sha256']
    cp = json.loads((ROOT/'DEVELOPMENT_CHECKPOINT.json').read_bytes())
    assert cp['completed_sections'] == 93 and cp['policy']['commit_after_each_section'] is False
    assert cp['policy']['commit_interval'] == 5 and cp['policy']['push_after_batch_commit'] is True
    return {'receipt_path':str(path), 'receipt_sha256':sha, 'closure_path':str(closure_path), 'closure_sha256':closure_sha}

phase = sys.argv[1]
if phase == 'prepare':
    guard = base_gate()
    candidate_gate()
    actual93 = completed93_gate(Path(sys.argv[2]), sys.argv[3], Path(sys.argv[4]), sys.argv[5])
    save_new(LOCAL/'root-integration-plan094.json', {'format_version':1,'passed':True,
        'actual_HEAD_unchanged92':BASE_HEAD,'actual93_completed_working_tree_binding':actual93,
        'source093_guard_sha256':GUARD_SHA,'before_source_sha256':guard['source_sha256_after'],
        'candidate_manifest_sha256':MANIFEST_SHA,'candidate_app_sha256':APP_AFTER,
        'changed_paths':['rouge/app.py'],'project_calls':0,'no_per_section_commit_or_tag':True})
    print(json.dumps({'source_gate_PASS':True,'actual93_completion_verified':True,'candidate_not_applied':True,'project_calls':0}))
elif phase == 'apply':
    plan = json.loads((LOCAL/'root-integration-plan094.json').read_bytes())
    bound = plan['actual93_completed_working_tree_binding']
    completed93_gate(Path(bound['receipt_path']),bound['receipt_sha256'],Path(bound['closure_path']),bound['closure_sha256'])
    guard = base_gate()
    new = candidate_gate()
    (ROOT/'rouge/app.py').write_bytes(new)
    after = maintained()
    expected = dict(guard['source_sha256_after']);expected['rouge/app.py'] = APP_AFTER
    assert after == expected
    save_new(LOCAL/'root-integration-applied094.json', {'format_version':1,'passed':True,
        'root_only_apply':True,'changed_paths':['rouge/app.py'],'candidate_bytes_exact':True,'project_calls':0})
    save_new(LOCAL/'root-source-094.json', {'format_version':1,'passed':True,
        'actual_HEAD_unchanged92':BASE_HEAD,'actual_base_section':93,'base_source_guard_sha256':GUARD_SHA,
        'actual93_completed_working_tree_binding':bound,'old_maintained':732,'current_maintained':732,
        'unchanged_maintained':731,'changed_maintained':['rouge/app.py'],'new_maintained':[],
        'source_sha256_after':after,'candidate_bytes_exact':True,'project_calls':0})
    print(json.dumps({'applied':True,'current_maintained':732,'unchanged_maintained':731,'changed':['rouge/app.py'],'project_calls':0}))
else:
    raise ValueError(phase)
