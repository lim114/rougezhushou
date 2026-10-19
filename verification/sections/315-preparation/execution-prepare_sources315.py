from pathlib import Path
from hashlib import sha256
import json,shutil
ROOT=Path(__file__).resolve().parents[1];CACHE=ROOT/'.cache/p3-current-rewards-315';PACK=ROOT/'research/p3-current-rewards-315';PACK.mkdir()
def enc(v):return(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode()
collection=json.loads((CACHE/'collection.json').read_bytes());assert not collection['failures']
objects={}
for key,pin in collection['files'].items():
 raw=(CACHE/(key+'.json')).read_bytes();assert sha256(raw).hexdigest()==pin['sha256']and len(raw)==pin['bytes'];objects[key]=json.loads(raw)
ids=['trap_320_shtlbx','trap_321_shnbox','trap_322_shrbox','trap_323_shsbox','trap_327_shchst'];chars={key:objects['character_table'][key]for key in ids};skills={s['skillId']:objects['skill_table'][s['skillId']]for c in chars.values()for s in c['skills']}
assert len(skills)==5
(PACK/'selected-originals.json').write_bytes(enc({'characters':chars,'skills':skills}))
(PACK/'source-selection.json').write_bytes(enc({'commit':collection['commit'],'original_sources':collection['files'],'complete_character_objects':ids,'complete_skill_objects':list(skills),'actual_current_server_verified':False,'original_cache_source_equality_must_be_verified_separately':True}))
shutil.copyfile(CACHE/'collection.json',PACK/'collection.json');shutil.copyfile(CACHE/'documented-rewards.json',PACK/'new-document-download-failures.json')
lookup={'queried_this_section':True,'successful_new_HTML_downloads':0,'local_TLS_failures_preserved':'research/p3-current-rewards-315/new-document-download-failures.json','web_rendered_observations':[{'url':'https://prts.wiki/w/恶笼草','scope':'grade0 reward condition +10/-10 visible in actual web open; no full-page bytes archived','other_grade_reverification_claimed':False},{'url':'https://prts.wiki/w/鸭爵','scope':'grade1 reward1 relic visible in actual web open; no full-page bytes archived','other_grade_reverification_claimed':False},{'url':'https://prts.wiki/w/小八界','scope':'name and level sections visible; no reward quantity established'}],'runtime_quantity_documents_reused':['research/p3-rare-rewards/documented-outcomes.json','rouge/data/moving-reward-current-reference.json'],'reuse_scope':'Pinned prior per-grade community documentation, never silently promoted to current-server execution or refreshed revision. New current exact refs independently qualified.','original_game_device_rules_from_current_primary_tables':True,'source_publisher_distinction':'Kengxxiao extracted game mirror; PRTS community mechanics; neither is the live game server API.'}
(PACK/'documentation-scope.json').write_bytes(enc(lookup))
print(json.dumps({'primary_characters':len(chars),'primary_skills':len(skills),'reused_document_scope_explicit':True}))
