"""Close popup-control evidence using the executed, source-sealed CORE suite.

Does not repeat its image tests or infer a pass from static preparation.
"""
import ast
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import time

ROOT=Path(__file__).resolve().parents[1]


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))


def main():
    core_path=ROOT/'CORE_0.59_VERIFICATION.json';core=read(core_path)
    assert core['passed'] and not core['failures'] and not core['errors']
    assert core['maintained_test_files_sealed'] and not core['source_drift_during_tests']
    for name,value in core['source_sha256'].items():assert sha(ROOT/name)==value,name
    log=ROOT/core['test_log'];assert sha(log)==core['test_log_sha256']
    lines=log.read_text(encoding='utf-8').splitlines()
    successful=[line for line in lines if '(tests.test_page_features_059.' in line and line.endswith(' ... ok')]
    assert len(successful)==9,successful
    semantic=[line for line in lines if '(tests.test_recognition_059.' in line and line.endswith(' ... ok')]
    assert len(semantic)==15,semantic
    assert any('test_each_missing_control_falls_back (tests.test_page_features_056.' in line
               and line.endswith(' ... ok') for line in lines)
    before=read(ROOT/'.cache/batch-059-before/manifest.json')
    original={n:v for n,v in before['source_hashes'].items()
              if n.startswith('rouge/data/page-features/') and Path(n).suffix in ('.npz','.png')}
    assert len(original)==20
    for name,value in original.items():assert sha(ROOT/name)==value,name
    old_path=ROOT/'.cache/batch-059-before/tests/test_page_features_056.py'
    current_path=ROOT/'tests/test_page_features_056.py'
    assert sha(old_path)==before['source_hashes']['tests/test_page_features_056.py']
    old=ast.parse(old_path.read_text(encoding='utf-8-sig'))
    current=deepcopy(ast.parse(current_path.read_text(encoding='utf-8-sig')))
    target=next(node for node in ast.walk(current) if isinstance(node,ast.FunctionDef)
                and node.name=='test_each_missing_control_falls_back')
    loop=target.body[0];guard=loop.body[1]
    expected=ast.parse("if page.get('source_client_rect'):\n"
                       "    left, top, right, bottom = page['source_client_rect']\n"
                       "    image = image[top:bottom, left:right]\n").body[0]
    assert ast.dump(guard,include_attributes=False)==ast.dump(expected,include_attributes=False)
    del loop.body[1]
    assert ast.dump(old,include_attributes=False)==ast.dump(current,include_attributes=False)
    experiment_path=ROOT/'.cache/page-features-059/feature-experiment-evidence.json'
    experiment=read(experiment_path)
    assert experiment['closure_verified'] is True
    for name,value in experiment['evidence_sha256'].items():assert sha(ROOT/name)==value,name
    files=[ROOT/'rouge/page_features.py',ROOT/'scripts/build_page_features_059.py',Path(__file__),
           current_path,ROOT/'tests/test_page_features_058.py',ROOT/'tests/test_page_features_059.py',
           ROOT/'.cache/research/page-routing-056/epoch-1791136902879484600/inventory.json',
           ROOT/'.cache/batch-059-before/manifest.json',old_path,
           *[p for p in (ROOT/'rouge/data/page-features').iterdir() if p.is_file()]]
    values={p.relative_to(ROOT).as_posix():sha(p) for p in files}
    values.update(experiment['evidence_sha256'])
    values[experiment_path.relative_to(ROOT).as_posix()]=sha(experiment_path)
    receipt={'version':'0.59.0','passed':True,'new_test_methods_executed':9,
        'new_semantic_footer_test_methods_executed':15,
        'experiment_evidence':{'path':experiment_path.relative_to(ROOT).as_posix(),'sha256':sha(experiment_path)},
        'core_receipt':{'path':core_path.relative_to(ROOT).as_posix(),'sha256':sha(core_path)},
        'test_log':{'path':log.relative_to(ROOT).as_posix(),'sha256':sha(log)},
        'source_sha256':values,'original_twenty_binary_assets_sha256':original,
        'legacy_test_change':'Recorded client crop only; remaining old module AST identical.',
        'original_legacy_test':{'path':old_path.relative_to(ROOT).as_posix(),'sha256':sha(old_path)},
        'training_sources':1,'untrained_operator_identities_in_development_corpus':3,
        'limits':['Existing captures from one user; no independent accuracy rate.',
                  'Derived scale/count/body/occlusion tests do not establish new real layouts.',
                  'Page features provide no owner, count or buff facts.'],
        'game_actions':0,'chat_requests':0,'private_state_read':False,'verified_at':time.time()}
    folder=ROOT/'.cache/page-features-059';folder.mkdir(exist_ok=True)
    path=folder/f'freeze-{time.time_ns()}.json'
    with path.open('x',encoding='utf-8') as handle:json.dump(receipt,handle,ensure_ascii=False,indent=2)
    print(json.dumps({'passed':True,'receipt':path.relative_to(ROOT).as_posix()},ensure_ascii=False))


if __name__=='__main__':main()
