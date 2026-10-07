from pathlib import Path
import json,hashlib,gzip,collections,datetime,sys
B=Path('/workspace/.continuation/p2-cooperative-text-input-069');R=Path('/workspace/rougezhushou');OUT=Path(__file__).parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();source=json.loads((B/'source-receipt.json').read_bytes());freeze=json.loads((B/'baseline-freeze.json').read_bytes())
assert freeze['head']==source['baseline_head']=='f4ca1c97278c5354f32940f56db2de60bbd21423'
for name,record in freeze['files'].items():assert sha(B/'baseline64'/name)==record['sha256'],name
raws={}
for name,record in source['raw_sources'].items():
    path=R/'.cache/p2-s1-binding'/name;assert sha(path)==record['sha256'];raws[name]=json.loads(path.read_bytes())
for name,record in source['source_files'].items():assert sha(B/'baseline64'/name)==record['sha256'],name
for name,record in source['reused_receipts'].items():assert sha(Path(name))==record['sha256'],name
for name,digest in source['artifact_hashes'].items():assert sha(B/name)==digest,name
char=raws['character_table.json'];skill=raws['skill_table.json'];native=char['char_1045_svash2'];token=char['token_10057_svash2_eagle3']
assert native['skills'][2]==source['actual_skill_binding_record'];assert token['skills'][2]==source['actual_token_binding_record']
assert native['skills'][2]['skillId']=='skchr_svash2_3' and native['skills'][2]['overrideTokenKey']=='token_10057_svash2_eagle3'
assert token['skills'][2]['skillId']=='sktok_svash2_3'
sys.path.insert(0,str(B/'baseline64'))
from rouge.catalog import catalog
from rouge.operator_engine import selected_talents
p=catalog()['operators']['silverash'];assert p['id']=='char_1045_svash2'
for i,row in enumerate(source['all_ten_selected_own_and_token_skill_records']):
    assert row['own_record']==skill['skchr_svash2_3']['levels'][i]
    assert row['token_record']==skill['sktok_svash2_3']['levels'][i]
    assert p['skills'][2]['levels'][i]['values']=={item['key']:item['value'] for item in row['own_record']['blackboard']}
for row in source['selected_named_talent_cases']:
    talents,parts=selected_talents(p,row['scenario'])
    assert talents==row['selected_talents']
app=(B/'baseline64/rouge/app.py').read_text()
assert 'self.cooperative.isChecked()' in app and '协同攻击持续覆盖同一目标' in app
old=(B/'baseline64/rouge/damage.py').read_bytes();new=(B/'draft69/rouge/damage.py').read_bytes()
guard=("    if scenario['operator']=='silverash' and skill==3 and isinstance(scenario.get('cooperative'),str):\r\n"+"        raise ValueError('cooperative不接受字符串，请提供明确的布尔条件。')\r\n").encode()
assert new.replace(guard,b'',1)==old
assert sha(B/'section69.patch')=='03c0dcc0b446c074669311861254820f702b8b9d27661dd9d78ea92cf02a785f'
with gzip.open(B/'baseline64-public-full-outcomes.json.gz','rt') as f:before=json.load(f)
with gzip.open(B/'draft69-public-full-outcomes.json.gz','rt') as f:after=json.load(f)
with gzip.open(B/'paired-full-outcomes.json.gz','rt') as f:paired=json.load(f)
assert len(before['cases'])==len(after['cases'])==len(paired['cases'])==1956
counts=collections.Counter()
for name,row in paired['cases'].items():
    a=before['cases'][name];c=after['cases'][name];assert row['scenario']==a['scenario']==c['scenario']
    assert row['before']==a['outcome'] and row['after']==c['outcome']
    if row['before']==row['after']:
        counts['old_errors_unchanged' if row['after']['error'] is not None else 'success_outputs_unchanged']+=1
    else:
        args=row['scenario'];assert args['operator']=='silverash' and args['skill']==3 and isinstance(args.get('cooperative'),str)
        assert row['before']['error'] is None
        assert row['after']=={'result':None,'error':{'type':'ValueError','message':'cooperative不接受字符串，请提供明确的布尔条件。'}}
        counts['qualified_strings_rejected']+=1
assert counts=={'qualified_strings_rejected':102,'success_outputs_unchanged':1794,'old_errors_unchanged':60}
out={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'baseline_commit':source['baseline_head'],
     'frozen_files_verified':len(freeze['files']),'fresh_raw_sources_verified':True,'exact_owner_and_token_skill_bindings_verified':True,
     'own_and_token_rank_pairs_verified':10,'original_named_talent_selection_cases_verified':len(source['selected_named_talent_cases']),
     'reused_receipt_hashes_verified':len(source['reused_receipts']),'gui_checkbox_producer_static_verified':True,
     'source_and_formula_bytes_unchanged_except_two_guard_lines':True,'source_borrow_or_native_clock_rule_added':False,
     'author_saved_complete_pairs_strictly_recompared':1956,'author_counts':counts,'author_calls_not_reexecuted':3912,
     'current_source_hashes':source['artifact_hashes'],'native_or_wine_or_gui_validation':False}
(OUT/'source-and-saved-comparison.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out,ensure_ascii=False))
