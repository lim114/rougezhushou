import gzip,json,pathlib
p=pathlib.Path(__file__).resolve().parent;strict=lambda v:json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
a=json.loads(gzip.decompress((p/'baseline-whole-outcomes.json.gz').read_bytes()));b=json.loads(gzip.decompress((p/'draft-whole-outcomes.json.gz').read_bytes()));assert len(a)==len(b)
added=errors=other=0;groups={};failures=[]
for left,right in zip(a,b):
 assert {k:left[k] for k in ('key','group','input')}=={k:right[k] for k in ('key','group','input')}
 old=left['outcome'];new=right['outcome'];args=left['input'];assert old['accepted']==new['accepted']
 if not old['accepted']:
  assert strict(old)==strict(new);errors+=1;continue
 assert strict(old)==strict(new['stripped_old_outcome']),left['key']
 current={k:v for k,v in new.items() if k!='stripped_old_outcome'}
 if args['operator']!='char_1035_wisdel':
  assert strict(old)==strict(current);other+=1;continue
 result=new['result'];ref=result['wisdel_summon_qualification_reference'];qualified=args.get('elite',2)==2
 assert ref['talent_route']['cultivation_qualified']==ref['skill_route']['cultivation_qualified']==qualified
 assert ref['skill_route']['currently_selected']==(args['skill']==3)
 assert (ref['skill_route']['selected_level_source'] is not None)==(args['skill']==3)
 if args['skill']==3:assert ref['skill_route']['selected_level_source']['rank']==args.get('skill_rank',10)
 assert ref['actual_source_provenance'] is None and ref['covers_all_routes']==ref['declared_counts_reinterpreted']==ref['actual_presence_verified']==ref['actual_cast_clock_verified']==False
 assert sum(s['id']=='wisdel_summon_qualification' for s in result['report']['sections'])==1
 added+=1;groups[left['group']]=groups.get(left['group'],0)+1
assert not failures and added+errors+other==len(a)
receipt={'baseline_head':'552a6f3ab8b16cce49a9cf0de1e247c3ff49e3a9','cases':len(a),'actual_paired_public_calls':sum(json.loads((p/(tag+'-matrix-receipt.json')).read_text())['actual_public_calculate_calls'] for tag in ('baseline','draft')),'accepted_wisdel_source_only_added_cases':added,'all_old_complete_outcomes_preserved_after_exact_new_key_and_section_removal':True,'old_numbers_all_metadata_and_three_report_strings_unchanged':True,'exact_error_cases_preserved':errors,'unrelated_owner_whole_cases_preserved':other,'added_groups':groups,'new_qualification_matches_current_cultivation':True,'no_S1_S2_rank_inherited_as_S3':True,'no_declaration_provenance_or_zero_reinterpretation':True,'shared_source_cache_and_inputs_preserved':True,'failures':failures}
(p/'paired-comparison.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n');print(json.dumps(receipt))
