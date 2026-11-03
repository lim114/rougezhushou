"""Keep resting outcomes scoped to their documentary case and retain conflicts."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import argparse,json,re,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.build_documented_event_flows_321 import Document,Node,canonical,encoded
ROOT=Path(__file__).resolve().parents[1];PACK='research/p3-current-resting-345';DATA='rouge/data/current-resting.json'
CURRENT='research/p3-expansion-313/current-topic.json';BASELINE='research/p3-expansion-313/baseline-topic.json';LEGACY='rouge/data/node-catalog.json';ICONS='rouge/data/relic-icon-receipt.json';OLD='rouge/data/resting-corner-results.json'
OLD_FILES=[OLD,'research/p3-resting-results-293/prts-events-427904.html','research/p3-resting-results-293/prts-events-440271.html']
LABELS={1:'最初对话',3:'进入后的病床',6:'初次结果 · 小狗',8:'小狗后的小猫图案',10:'初次结果 · 捕梦网',12:'捕梦网后的小猫图案',14:'初次结果 · 松鼠',16:'松鼠后的小猫图案',18:'小狗后 · 果园',20:'小狗果园后的离开',22:'小狗后 · 豹子竞速',24:'小狗竞速后的离开',26:'捕梦网后安静观察的离开',28:'捕梦网后 · 动物泥偶',30:'99源石锭后的文献离开（存在冲突）',32:'松鼠后 · 果园',34:'松鼠果园后的离开',36:'松鼠后 · 豹子竞速',38:'松鼠竞速后的离开'}

def build(root=ROOT):
    root=Path(root);receipt=json.loads((root/PACK/'source-receipt.json').read_bytes());raw=(root/receipt['selected_file']).read_bytes()
    if receipt['revision']!=352356 or len(raw)!=receipt['selected_bytes']or sha256(raw).hexdigest()!=receipt['selected_sha256']:raise ValueError('Exact full section required')
    current=json.loads((root/CURRENT).read_bytes())['details'];old=json.loads((root/BASELINE).read_bytes())['details'];originals={'scenes':{k:deepcopy(v)for k,v in current['choiceScenes'].items()if v['title']=='安眠一隅'},'choices':{},'items':{},'stages':{}}
    tables=[n for n in Document(raw.decode()).root.walk()if n.tag=='table']
    if len(tables)!=1:raise ValueError('One full resting table required')
    cells={};scenes={};choices={}
    for ri,tr in enumerate(n for n in tables[0].walk()if n.tag=='tr'):
        for ci,cell in enumerate(n for n in tr.children if isinstance(n,Node)and n.tag in('th','td')):
            full=canonical(cell.text());loc={'file':receipt['selected_file'],'row':ri,'cell':ci,'cell_text_sha256':sha256(cell.text().encode()).hexdigest()}
            if not full:continue
            if cell.tag=='th':
                ids=[k for k,v in originals['scenes'].items()if canonical(v['description'])==full]
                if not ids or ri not in LABELS:raise ValueError('All full narratives must match originals')
                sid='doc:'+str(ri);scenes[sid]={'id':sid,'label':LABELS[ri],'description':cell.text().strip(),'source_scene_ids':ids,'choice_ids':[],'scope':'bwiki','source':loc};continue
            text=full.split('◈')[0]
            hits={k:deepcopy(v)for k,v in current['choices'].items()if canonical(v['title']+(v['description']or''))==text and(v['nextSceneId']in originals['scenes']or(v['nextSceneId']is None and v['type']=='NEXT_PROB'))}
            if hits:
                if ri in cells:raise ValueError('One complete option cell per row')
                signature={(v['title'],v['description'],v['type'])for v in hits.values()}
                if len(signature)!=1:raise ValueError('Distinct full text/type cannot merge')
                cells[ri]={'variants':hits,'source':loc};originals['choices'].update(hits)
    required={2,4,5,7,9,11,13,15,17,19,21,23,25,27,29,31,33,35,37}
    if set(cells)!=required or len(scenes)!=19:raise ValueError('Every full documented option and19 narrative occurrences required')
    if(len(originals['scenes']),len(originals['choices']))!=(12,12):raise ValueError('Preserve12 narratives and12 original choices')
    if set(originals['scenes'])!={k for s in scenes.values()for k in s['source_scene_ids']}:raise ValueError('Account for every original narrative')
    def add(cid,parent,next_id,row,role,*,label=None,outcome=False,scope='bwiki'):
        cell=cells[row];v=next(iter(cell['variants'].values()));ids=list(cell['variants']);explicit=[k for k in ids if cell['variants'][k]['nextSceneId']]
        conflict=bool(explicit and next_id in scenes and any(canonical(originals['scenes'][cell['variants'][k]['nextSceneId']]['description'])!=canonical(scenes[next_id]['description'])for k in explicit))
        c={'id':cid,'scene_id':parent,'next_scene_id':next_id,'title':label or v['title'],'original_title':v['title'],'description':v['description'],'role':role,'presentation':'outcome_reference'if outcome else'option_reference','actual_game_button':False if outcome else None,'scope':scope,'variant_ids':ids,'source_only':False,'stage_ids':[],'explicit_next_conflict':conflict,'conflicting_original_id':explicit[0]if conflict and len(explicit)==1 else None,'actual_result':None,'actual_received':None,'source':deepcopy(cell['source'])}
        choices[cid]=c;scenes[parent]['choice_ids'].append(cid)
    def menu(key,label):scenes[key]={'id':key,'label':label,'description':None,'source_scene_ids':[],'choice_ids':[],'scope':'bwiki','source':{'file':receipt['selected_file'],'kind':'documented_results_not_actual_menu'}}
    menu('outcomes:first','四处看看 · 文献列出的结果')
    menu('outcomes:dog','小狗后触碰图案 · 文献结果')
    menu('outcomes:net','捕梦网后触碰图案 · 数量注释待核对')
    menu('outcomes:squirrel','松鼠后触碰图案 · 来源差异待核对')
    add('option:enter','doc:1','doc:3',2,'named_item')
    add('option:look','doc:3','outcomes:first',4,'look')
    for name,row,dest in [('dog',5,6),('net',9,10),('squirrel',13,14)]:add('result:first-'+name,'outcomes:first','doc:'+str(dest),row,'outcome',label='查阅'+{'dog':'小狗','net':'捕梦网','squirrel':'松鼠'}[name]+'结果',outcome=True)
    for key,row,parent,dest in [('dog',7,6,8),('net',11,10,12),('squirrel',15,14,16)]:add('reward:'+key,'doc:'+str(parent),'doc:'+str(dest),row,'resource')
    for name,row,parent in [('dog',17,8),('net',27,12),('squirrel',31,16)]:add('option:touch-'+name,'doc:'+str(parent),'outcomes:'+name,row,'touch')
    for key,parent,row,dest,label in [('dog-orchard','dog',17,18,'果园'),('dog-race','dog',21,22,'豹子竞速'),('net-mud','net',27,28,'动物泥偶'),('squirrel-orchard','squirrel',31,32,'果园'),('squirrel-race','squirrel',35,36,'豹子竞速')]:add('result:'+key,'outcomes:'+parent,'doc:'+str(dest),row,'outcome',label='查阅'+label+'结果',outcome=True)
    for key,row,parent,dest in [('dog-orchard',19,18,20),('dog-race',23,22,24),('observe',25,12,26),('gold99',29,28,30),('squirrel-orchard',33,32,34),('squirrel-race',37,36,38)]:add('reward:'+key,'doc:'+str(parent),'doc:'+str(dest),row,'gold99'if key=='gold99'else'resource')
    historical=json.loads((root/OLD).read_bytes());cards=deepcopy(historical['cards'])
    if [(c['documented_count'],c['listed_branch_count'],c['count_matches'])for c in cards]!=[(3,3,True),(2,2,True),(2,1,False),(2,3,False)]:raise ValueError('Keep both historical count conflicts exactly')
    extra=cards[3]['branches'][2]
    if extra['label']!='动物泥偶'or not extra['future_buttons'][0]['original_relation_mismatch']:raise ValueError('Keep unresolved legacy mud branch')
    if canonical(extra['target_scene_description'])!=canonical(scenes['doc:28']['description']):raise ValueError('Legacy mud narrative must fully match, not name only')
    scenes['legacy:mud']={**deepcopy(scenes['doc:28']),'id':'legacy:mud','label':'旧PRTS另列：松鼠后动物泥偶（归属未证）','choice_ids':[],'scope':'legacy_unresolved'}
    scenes['legacy:end']={**deepcopy(scenes['doc:30']),'id':'legacy:end','label':'旧资料记载的离开（原项后续不符）','choice_ids':[],'scope':'legacy_unresolved'}
    add('result:legacy-squirrel-mud','outcomes:squirrel','legacy:mud',27,'outcome',label='旧PRTS另列：动物泥偶（当前归属未证）',outcome=True,scope='legacy_unresolved')
    add('reward:legacy-gold99','legacy:mud','legacy:end',29,'gold99',scope='legacy_unresolved')
    for c in choices.values():
        if c['explicit_next_conflict']and c['role']!='gold99':raise ValueError('Unexpected new document/original next conflict')
        if c['scope']=='legacy_unresolved':c['source']['additional_legacy_branch']=deepcopy(extra)
    named=[v for v in originals['choices'].values()if v['description']=='获得收藏品<@ro6.get>源私钥</>']
    matches={k:v for k,v in current['items'].items()if v['name']=='源私钥'and v['type']=='RELIC'}
    if len(named)!=1 or named[0]['displayData']['itemId']is not None or len(matches)!=1:raise ValueError('Unique literal named-item reference with missing original pointer required')
    item_id,item=next(iter(matches.items()));originals['items'][item_id]=deepcopy(item)
    icon=next(v for v in json.loads((root/ICONS).read_bytes())['icons']if v['id']==item_id);picture=(root/'rouge/data'/icon['file']).read_bytes()
    if sha256(picture).hexdigest()!=icon['sha256']:raise ValueError('Exact current item picture required at build')
    legacy=next(v for v in json.loads((root/LEGACY).read_bytes())['events']if v['title']=='安眠一隅');links=[]
    for s in legacy['scenes']:
        for sid in s['game_scene_ids']:
            if sid not in originals['scenes']:continue
            a=canonical(s['description']);b=canonical(originals['scenes'][sid]['description'])
            if a!=b and a.replace('……','......')!=b:raise ValueError('No fuzzy legacy link')
            links.append({'legacy_scene_key':s['key'],'current_original_scene_id':sid,'legacy_complete_description':s['description'],'current_complete_description':originals['scenes'][sid]['description']})
    if len(links)!=18:raise ValueError('Keep18 links with repeated legacy contexts, not18 unique originals')
    association={k:'explicit_destination_scene'if v['nextSceneId']else'full_literal_random_candidate'for k,v in originals['choices'].items()}
    if sum(v=='explicit_destination_scene'for v in association.values())!=8:raise ValueError('Exactly8 explicit and4 no-next candidates')
    rewards={}
    for key,v in originals['choices'].items():
        match=re.fullmatch(r'获得(\d+)(希望|护盾|源石锭|件珍贵的加工品)',canonical(v['description']))
        rewards[key]={'quantity':int(match[1]),'kind':{'希望':'hope','护盾':'shield','源石锭':'gold','件珍贵的加工品':'precious_processed_part'}[match[2]]}if match else None
    for c in choices.values():
        c['reward_reference']=deepcopy(rewards[c['variant_ids'][0]])if c['role']in('resource','gold99')else None
    result={'schema':'current_resting_345_v1','game_commit':'bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d','event':{'id':'resting','title':'安眠一隅','entry_scene_id':'doc:1','scene_ids':list(scenes),'choice_ids':list(choices)},'scenes':scenes,'choices':choices,'originals':originals,'original_choice_association':association,'historical_result_cards':cards,'complete_document_table':True,'complete_game_option_pool':False,'actual_result':None,'run_updated':False,'source':receipt,'icon_reference':{**deepcopy(icon),'file':'rouge/data/'+icon['file'],'bytes':len(picture)},'catalogue_binding':{'expected_legacy_event':legacy,'expected_summary':{k:deepcopy(legacy[k])for k in('id','title','node_types','floors','natural','natural_reason','entry')},'exact_scene_links':links,'current_event_id':'resting'},'complete_selected_record_comparison_to_baseline':{g:{k:old['choiceScenes'if g=='scenes'else g].get(k)==v for k,v in rows.items()}for g,rows in originals.items()}}
    result['named_item_binding']={'basis':'full_literal_unique_current_RELIC_name','original_item_pointer':None,'actual_received':None}
    result['original_reward_references']=rewards
    data=encoded(result);names=[CURRENT,BASELINE,LEGACY,ICONS,PACK+'/source-receipt.json',PACK+'/source-notes.json',receipt['selected_file'],*OLD_FILES]
    files={n:{'bytes':len((root/n).read_bytes()),'sha256':sha256((root/n).read_bytes()).hexdigest()}for n in names};files[DATA]={'bytes':len(data),'sha256':sha256(data).hexdigest()}
    return data,encoded({'schema':'current_resting_345_manifest_v1','game_commit':result['game_commit'],'files':files})

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args();d,m=build()
    if a.check:
        if(ROOT/DATA).read_bytes()!=d or(ROOT/PACK/'runtime-manifest.json').read_bytes()!=m:raise ValueError('Build differs')
    else:(ROOT/DATA).write_bytes(d);(ROOT/PACK/'runtime-manifest.json').write_bytes(m)
    v=json.loads(d);print(json.dumps({'original_scenes':12,'original_choices':12,'document_contexts':len(v['scenes']),'document_options_and_results':len(v['choices']),'manifest_sha256':sha256(m).hexdigest()}))
