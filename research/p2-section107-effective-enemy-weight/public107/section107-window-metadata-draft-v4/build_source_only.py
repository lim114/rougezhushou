from pathlib import Path
import ast
import difflib
import hashlib
import json

# Author's stdlib Source builder only. It never imports/executes the generated
# Window, project modules, evidence helper or codec.
OLD_SOURCE=Path('/workspace/.continuation/section107-window-source-v3/window107.py')
OUT=Path('/workspace/.continuation/section107-window-metadata-draft-v4b')
NEW_TEST='0'*64
sha=lambda b:hashlib.sha256(b).hexdigest()
old=OLD_SOURCE.read_bytes()
assert sha(old)=='9762693bc8088837122758f4c3893ac17b47414ced0c484942cb0754e31472e8'
assert not OUT.exists();OUT.mkdir()
blocks=[]

def block(tag,body,indent=''):
    text=indent+'# BEGIN107_META_'+tag+'\n'+body+indent+'# END107_META_'+tag+'\n'
    blocks.append((tag,indent,text))
    return text

metadata=block('01', '''GOLD_RUNNER_SHA='9762693bc8088837122758f4c3893ac17b47414ced0c484942cb0754e31472e8'
GOLD_RECEIPT_SHA='f543d873cbc9ab3c629e8d0815df3438a82c15fe459e463870f757bef9396634'
GOLD_GUARD_SHA='0eea8377cec0b48efa72b9885e5668b6e518e1802c49f8d57de12b962ad0a442'
OLD_TEST_SHA='62766f1d8cae2b4ef4618ae4f90dddb0c1e9ce8d165f272f1d0fc9caa3b87e8c'


def admit_legacy_gold(artifact,gold_raw,gold_exit_raw,current_source):
    """Read-only bootstrap: original Gold evidence is never rewritten."""
    assert TEST_SHA!='0'*64
    assert gold_exit_raw==b'0\\n' and len(gold_raw)==571058 and sha(gold_raw)==GOLD_RECEIPT_SHA
    legacy_path=artifact/'legacy-gold-window107.py'
    guard_path=artifact/'legacy-gold-guard.json'
    assert not legacy_path.is_symlink() and not guard_path.is_symlink()
    legacy_source=legacy_path.read_bytes();legacy_guard_raw=guard_path.read_bytes()
    assert len(legacy_source)==39470 and sha(legacy_source)==GOLD_RUNNER_SHA
    assert len(legacy_guard_raw)==82361 and sha(legacy_guard_raw)==GOLD_GUARD_SHA
    legacy_guard=json.loads(legacy_guard_raw);legacy_gold=json.loads(gold_raw)
    assert legacy_gold['source_guard_sha256']==GOLD_GUARD_SHA
    assert legacy_gold['source_before']==legacy_gold['source_after']==legacy_guard['source_sha256']
    assert len(legacy_guard['source_sha256'])==749 and len(current_source)==750
    assert 'tests/test_aglna_gravity_weight_107.py' not in legacy_guard['source_sha256']
    assert current_source['tests/test_aglna_gravity_weight_107.py']==TEST_SHA
    # Removing only declared metadata blocks and two exact replacements must
    # recover all actual old runner bytes, including every fixture and loop.
    recovered=Path(__file__).read_bytes()
    candidate_runner_sha=sha(recovered)
    for tag,indent in (('01',''),('02','    '),('03','        '),('04','    ')):
        begin=(indent+'# BEGIN107_META_'+tag+'\\n').encode()
        end=(indent+'# END107_META_'+tag+'\\n').encode()
        assert recovered.count(begin)==recovered.count(end)==1
        first=recovered.index(begin);last=recovered.index(end,first)+len(end)
        recovered=recovered[:first]+recovered[last:]
    newer=("TEST_SHA='"+TEST_SHA+"'\\n").encode()
    older=("TEST_SHA='"+OLD_TEST_SHA+"'\\n").encode()
    assert recovered.count(newer)==1;recovered=recovered.replace(newer,older)
    newer=b"gold['runner_sha256']==GOLD_RUNNER_SHA and gold['original_receipt_sha256']==ORIGINAL_SHA"
    older=b"gold['runner_sha256']==sha(Path(__file__).read_bytes()) and gold['original_receipt_sha256']==ORIGINAL_SHA"
    assert recovered.count(newer)==1;recovered=recovered.replace(newer,older)
    assert recovered==legacy_source and sha(recovered)==GOLD_RUNNER_SHA
    return {'kind':'ROOT107_METADATA_ONLY_GOLD_ADMISSION_V1',
            'Gold_runner_sha256':GOLD_RUNNER_SHA,'candidate_runner_sha256':candidate_runner_sha,
            'legacy_Gold_receipt_sha256':GOLD_RECEIPT_SHA,
            'legacy_Gold_source_guard_sha256':GOLD_GUARD_SHA,
            'legacy_Gold_primary_sha256':sha(gold_exit_raw),
            'functional_source_inverse_sha256':sha(recovered),'candidate_test_sha256':TEST_SHA,
            'legacy_Gold_source_count':749,'candidate_source_count':750,
            'legacy_Gold_contains_107_test':False,'Window_imports_107_test':False,
            'old_and_new_runners_are_identical':False,'legacy_Gold_values_rewritten':False}


''')
text=old.decode()
old_test="TEST_SHA='62766f1d8cae2b4ef4618ae4f90dddb0c1e9ce8d165f272f1d0fc9caa3b87e8c'\n"
new_test_line="TEST_SHA='"+NEW_TEST+"'\n"
assert text.count(old_test)==1;text=text.replace(old_test,new_test_line+metadata)
anchor='    gold=None;gold_dir=None\n'
preflight=block('02',"    assert args.phase=='candidate' and TEST_SHA!='0'*64\n",'    ')
assert text.count(anchor)==1;text=text.replace(anchor,preflight+anchor)
anchor="        gold_dir=Path(args.gold);gold_raw=(gold_dir/'receipt.json').read_bytes();gold=json.loads(gold_raw)\n"
admission=block('03',"        compatibility=admit_legacy_gold(artifact,gold_raw,Path(args.gold_exit).read_bytes(),expected)\n",'        ')
assert text.count(anchor)==1;text=text.replace(anchor,anchor+admission)
before="        assert gold['runner_sha256']==sha(Path(__file__).read_bytes()) and gold['original_receipt_sha256']==ORIGINAL_SHA\n"
after="        assert gold['runner_sha256']==GOLD_RUNNER_SHA and gold['original_receipt_sha256']==ORIGINAL_SHA\n"
assert text.count(before)==1;text=text.replace(before,after)
anchor='    def save(kind,value):\n'
receipt=block('04',"    receipt['Gold_runner_compatibility']=compatibility\n",'    ')
assert text.count(anchor)==1;text=text.replace(anchor,receipt+anchor)
new=text.encode();(OUT/'window107.py').write_bytes(new)
for name in ('native_evidence.py','fixture-facts.json','exact-local-transports.json'):
    (OUT/name).write_bytes((OLD_SOURCE.parent/name).read_bytes())
(OUT/'legacy-gold-window107.py').write_bytes(old)
(OUT/'legacy-gold-guard.json').write_bytes(Path('/workspace/.continuation/resume106-applied-source-v1.json').read_bytes())
recovered=text
for tag,indent,snippet in blocks:
    assert recovered.count(snippet)==1;recovered=recovered.replace(snippet,'')
assert recovered.count(new_test_line)==1;recovered=recovered.replace(new_test_line,old_test)
assert recovered.count(after)==1;recovered=recovered.replace(after,before)
assert recovered.encode()==old
left=ast.parse(old.decode());right=ast.parse(new.decode());compile(right,str(OUT/'window107.py'),'exec')
left_asserts=[ast.dump(n,include_attributes=False) for n in ast.walk(left) if isinstance(n,ast.Assert)]
right_no_metadata=ast.parse(recovered.replace(before,after))
right_asserts=[ast.dump(n,include_attributes=False) for n in ast.walk(right_no_metadata) if isinstance(n,ast.Assert)]
assert len(left_asserts)==len(right_asserts)==91
assert sum(a!=b for a,b in zip(left_asserts,right_asserts))==1
changes={'kind':'INACTIVE107_V4_METADATA_ONLY_DRAFT','Source_only':True,'runtime_executed':False,'frozen':False,
         'candidate_new_test_ready':False,'placeholder_test_sha256':NEW_TEST,
         'actual_legacy_Gold':{'receipt_bytes':571058,'receipt_sha256':'f543d873cbc9ab3c629e8d0815df3438a82c15fe459e463870f757bef9396634',
                              'Source_runner_sha256':sha(old),'guard_sha256':'0eea8377cec0b48efa72b9885e5668b6e518e1802c49f8d57de12b962ad0a442','raw_exit':'0\\n'},
         'original_assert_count':91,'original_assert_AST_changed_count':1,'all_other_original_assert_AST_order_same':True,
         'original_complete_source_inverse_exact':True,'draft_sha256':sha(new),'draft_bytes':len(new),
         'added_metadata_blocks':[{'tag':tag,'indent':indent,'Source':snippet} for tag,indent,snippet in blocks],
         'unique_old_new_replacements':[{'before':old_test,'after':new_test_line},{'before':before,'after':after}]}
(OUT/'DRAFT_PLAN.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2)+'\n')
(OUT/'metadata-only.diff').write_text(''.join(difflib.unified_diff(old.decode().splitlines(True),text.splitlines(True),fromfile='sealed-v3/window107.py',tofile='inactive-v4/window107.py')))
print(json.dumps({'draft':str(OUT),'bytes':len(new),'sha256':sha(new),'Source_only':True,'frozen':False,'inverse_exact':True,
                  'baseline_asserts':91,'metadata_assert_exceptions':1,'added_asserts':sum(isinstance(n,ast.Assert) for n in ast.walk(right))-91}))
