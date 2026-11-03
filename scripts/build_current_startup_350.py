from pathlib import Path
from copy import deepcopy
from hashlib import sha256
import argparse,json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from rouge import current_startup as m
def enc(v):return(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf8')
def build():
    cur=json.loads((ROOT/'research/p3-expansion-313/current-topic.json').read_bytes())['details'];old=json.loads((ROOT/'rouge/data/original-entry-reference.json').read_bytes())['startup'];choices={};originals={k:{}for k in('choices','scenes','items','relics')}
    if cur['choiceScenes'][m.SCENE]!=old['scene']:raise ValueError('Current original scene differs')
    originals['scenes'][m.SCENE]=cur['choiceScenes'][m.SCENE]
    for raw in old['regular_choices']:
        cid=raw['id']
        if cur['choices'][cid]!=raw or raw['isHiddenChoice']is not False:raise ValueError('Exact complete regular record required')
        choices[cid]={'id':cid,'title':raw['title'],'scene_id':m.SCENE,'kind':'regular','original':deepcopy(raw),'next_scene_id':None,'stage_ids':[],'item_id':None,'source_scene_pointer_verified':False}
    for inherited in old['legacy_choices']:
        raw=inherited['choice'];cid=raw['id'];lid=inherited['legacy_id'];buff=inherited['force_add_choice_buff'];iid=raw['displayData']['itemId']
        if cur['choices'][cid]!=raw or buff not in cur['relics'][lid]['buffs']or not raw['isHiddenChoice']:raise ValueError('Exact current inheritance binding required')
        choices[cid]={'id':cid,'title':raw['title'],'scene_id':m.SCENE,'kind':'inherited','original':deepcopy(raw),'next_scene_id':None,'stage_ids':[],'item_id':iid,'legacy_id':lid,'force_add_choice_buff':deepcopy(buff),'source_scene_pointer_verified':True}
        originals['items'][iid]=cur['items'][iid];originals['items'][lid]=cur['items'][lid];originals['relics'][lid]=cur['relics'][lid]
    originals['choices']={cid:cur['choices'][cid]for cid in choices}
    if len(choices)!=12:raise ValueError('Twelve exact options required')
    ids=list(choices);data={'schema':'current_startup_350_v1','game_commit':m.version.NEW_COMMIT,'event':{'id':'startup','title':'行动奖励','entry_scene_id':m.SCENE,'scene_ids':[m.SCENE],'choice_ids':ids},'scenes':{m.SCENE:{'id':m.SCENE,'event_id':'startup','choice_ids':ids}},'choices':choices,'originals':originals,'regular_ids':ids[:6],'inherited_ids':ids[6:],'actual_displayed_choices':None}
    notes={'section':350,'sources':['research/p3-expansion-313/current-topic.json','rouge/data/original-entry-reference.json'],'rule_scope':'Current complete scene and12 choice records exactly equal pinned prior startup evidence. Six direct force_add_choice records still explicitly point to scene/choice; regular six retain lack of original parent pointer. No automatic menu or actual eligibility.','fresh_web':'https://prts.wiki/w/沉沦者的黑流树海/事件一览','fresh_web_limit':'Current web text search did not expose action reward section; no new rule inferred from that absence. Existing pinned evidence remains scope.','new_mechanics_or_game_observation':False,'unknown':['actual menu','actual rewards and complete pools','current server eligibility','capacity/hp floors','legacy trigger execution and active effects']}
    out={m.DATA:enc(data),m.PACK+'/source-notes.json':enc(notes)}
    names=set(out)|{'research/p3-expansion-313/current-topic.json','rouge/data/original-entry-reference.json',*['rouge/data/relic-icons/rogue_6_start_'+str(i)+'.png'for i in range(1,7)]}
    files={}
    for name in sorted(names):
        raw=out.get(name)or(ROOT/name).read_bytes();files[name]={'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
    out[m.MANIFEST]=enc({'schema':'current_startup_350_manifest_v1','game_commit':m.version.NEW_COMMIT,'files':files});return out
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args();out=build()
    for n,raw in out.items():
        path=ROOT/n
        if a.check:
            if path.read_bytes()!=raw:raise ValueError('Build differs:'+n)
        else:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
    h=sha256(out[m.MANIFEST]).hexdigest()
    if a.check and h!=m.MANIFEST_SHA256:raise ValueError('Manifest differs')
    print(json.dumps({'choices':12,'regular_candidates':6,'independent_inherited_sources':6,'manifest_sha256':h}))
