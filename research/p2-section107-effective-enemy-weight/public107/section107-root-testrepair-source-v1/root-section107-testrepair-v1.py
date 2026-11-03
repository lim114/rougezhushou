"""Root-only one-test-contract repair. Draft until frozen candidate/review pins.

Never execute this draft; Root must receive a sealed Source version with the
actual new candidate bytes and review SHA supplied. No timing/product rewrite.
"""
import argparse
import ast
from copy import deepcopy
import datetime
import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path('/workspace/rougezhushou')
BASE=Path('/workspace/.continuation')
TEST='tests/test_aglna_gravity_weight_107.py'
OLD_TEST_SHA='62766f1d8cae2b4ef4618ae4f90dddb0c1e9ce8d165f272f1d0fc9caa3b87e8c'
OLD_GUARD_SHA='9f06db822007088a569ab571abb1b950bdc9701ad3eaa366603b713c80f9d897'
FAILED_LINUX_SHA='6f407da19b0899d77331bd23a9eb3abab92edb8fd4413aab5fa7e8042147ae82'
DIAGNOSIS_SHA='a4748413342aab7a5ee896beabadafd74553c82fdcc045bd68c8f942b777172b'
NEW_TEST_SHA=None  # Must be filled from the actual frozen candidate, never guessed.
NEW_REVIEW_SHA=None  # Must be filled from its actual independent Source review.


def sha(raw):return hashlib.sha256(raw).hexdigest()


def sources():
    return {p.relative_to(ROOT).as_posix():sha(p.read_bytes())
            for directory in ('rouge','tests','scripts') for p in sorted((ROOT/directory).rglob('*'))
            if p.is_file() and p.suffix in ('.py','.json') and '__pycache__' not in p.parts}


def method_delta(old,new):
    a,b=ast.parse(old),ast.parse(new)
    def methods(tree):
        found=[n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')]
        assert len(found)==11 and len({n.name for n in found})==11
        return {n.name:n for n in found}
    am,bm=methods(a),methods(b)
    unchanged={name for name in am.keys()&bm.keys()
               if ast.dump(am[name],include_attributes=False)==ast.dump(bm[name],include_attributes=False)}
    assert len(unchanged)==10
    ac,bc=set(am)-unchanged,set(bm)-unchanged
    assert len(ac)==len(bc)==1
    for tree,changed in ((a,am[next(iter(ac))]),(b,bm[next(iter(bc))])):
        removed=0
        for node in ast.walk(tree):
            for field,value in ast.iter_fields(node):
                if isinstance(value,list) and any(item is changed for item in value):
                    setattr(node,field,[item for item in value if item is not changed]);removed+=1
        assert removed==1
    assert ast.dump(a,include_attributes=False)==ast.dump(b,include_attributes=False)
    return sorted(ac),sorted(bc)


def main():
    assert NEW_TEST_SHA is not None and NEW_REVIEW_SHA is not None, 'Unsealed Source draft cannot apply'
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--new-test-source',required=True)
    parser.add_argument('--new-independent-review',required=True)
    args=parser.parse_args()
    target=BASE/'resume107-applied-source-v2.json';assert not target.exists()
    assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()=='codex/p2-development'
    guard_path=BASE/'resume107-applied-source-v1.json';guard_raw=guard_path.read_bytes()
    assert sha(guard_raw)==OLD_GUARD_SHA
    old=json.loads(guard_raw);assert old['section']==107 and old['source_count']==750
    assert len(old['source_sha256'])==750 and sources()==old['source_sha256']
    assert old['source_sha256'][TEST]==OLD_TEST_SHA
    assert set(old['source_additional_sha256'])=={'CORE_0.70_VERIFICATION.json'}
    core_path=ROOT/'CORE_0.70_VERIFICATION.json';core_raw=core_path.read_bytes()
    assert sha(core_raw)==old['source_additional_sha256']['CORE_0.70_VERIFICATION.json']
    checkpoint=json.loads((ROOT/'DEVELOPMENT_CHECKPOINT.json').read_bytes())
    assert checkpoint['completed_sections']==106 and checkpoint['next_section']==107
    assert checkpoint['full_validation_due'] is False and checkpoint['next_full_validation_after']==110
    publication=json.loads((BASE/'section106-publication-v1.json').read_bytes())
    assert publication['local_HEAD']==publication['remote_HEAD']==old['baseline_HEAD']
    assert publication['clean'] is True and publication['push_primary_exit']==0
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==publication['local_HEAD']
    failed_path=BASE/'resume107-related-linux-v1.json';failed_raw=failed_path.read_bytes()
    assert sha(failed_raw)==FAILED_LINUX_SHA
    assert (BASE/'resume107-related-linux-v1.exit-code').read_bytes()==b'1\n'
    failed=json.loads(failed_raw)
    assert failed['available_checks_passed'] is False and failed['tests_run']==222 and failed['tests_passed']==219
    assert failed['failures']==1 and failed['errors']==0 and failed['skipped']==1 and failed['unavailable_parent_count']==1
    assert failed['source_sha256']==failed['source_after']==old['source_sha256'] and failed['source_drift']==[]
    diag_path=BASE/'root-section107-empty-diagnostic-v1.json';diag_raw=diag_path.read_bytes()
    assert sha(diag_raw)==DIAGNOSIS_SHA and (BASE/'root-section107-empty-diagnostic-v1.exit-code').read_bytes()==b'0\n'
    diagnosis=json.loads(diag_raw)
    assert diagnosis['kind']=='ROOT_ACTUAL_107_EMPTY_BOUNDARY_DIAGNOSIS' and len(diagnosis['rows'])==12
    assert diagnosis['Source_750_CORE_unchanged'] is diagnosis['new_test_failure_preserved'] is True
    assert diagnosis['product_modified'] is False
    new_path=Path(args.new_test_source).resolve();review_path=Path(args.new_independent_review).resolve()
    assert ROOT not in new_path.parents and ROOT not in review_path.parents
    new_raw=new_path.read_bytes();review_raw=review_path.read_bytes()
    assert sha(new_raw)==NEW_TEST_SHA and sha(review_raw)==NEW_REVIEW_SHA
    current=(ROOT/TEST).read_bytes();assert sha(current)==OLD_TEST_SHA
    old_methods,new_methods=method_delta(current,new_raw)
    compile(new_raw,TEST,'exec')
    assert sources()==old['source_sha256'] and guard_path.read_bytes()==guard_raw and core_path.read_bytes()==core_raw
    # Exactly one root-owned write, after every actual evidence/Source gate.
    (ROOT/TEST).write_bytes(new_raw)
    after=sources()
    assert set(after)==set(old['source_sha256']) and len(after)==750
    assert {name for name in after if after[name]!=old['source_sha256'][name]}=={TEST}
    assert after[TEST]==NEW_TEST_SHA and guard_path.read_bytes()==guard_raw and core_path.read_bytes()==core_raw
    final=deepcopy(old)
    final.update(status='ACTUALLY_REPAIRED_TEST_CONTRACT_RUNTIME_PENDING',source_sha256=after,
        test_source_sha256=NEW_TEST_SHA,runtime_checks_passed_claimed=False,
        test_repaired_at_Beijing=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),
        test_repair_prior_guard_sha256=sha(guard_raw),test_repair_original_test_sha256=OLD_TEST_SHA,
        test_repair_candidate_source_sha256=sha(new_raw),test_repair_independent_source_review_sha256=sha(review_raw),
        test_repair_applier_source_sha256=sha(Path(__file__).read_bytes()),
        preserved_failed_Linux_receipt_sha256=sha(failed_raw),preserved_actual_empty_diagnosis_sha256=sha(diag_raw),
        test_repair_old_methods=old_methods,test_repair_new_methods=new_methods,
        only_test_changed_from_prior_applied_guard=True,
        test_repair_scope='Correct one new regression-test expectation using actual original continuous/frames boundary evidence; no timing or product modification.')
    with target.open('x',encoding='utf-8') as handle:json.dump(final,handle,ensure_ascii=False,indent=2);handle.write('\n')
    print(json.dumps({'guard':str(target),'source_count':750,'only_changed_path':TEST,'runtime_pass_claimed':False}))


if __name__=='__main__':main()
