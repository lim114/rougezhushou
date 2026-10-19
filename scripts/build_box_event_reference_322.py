"""Bind one investigation table to current records; retain ambiguous variants."""
from pathlib import Path
from hashlib import sha256
from copy import deepcopy
import argparse,json,re,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.build_documented_event_flows_321 import Document,Node,canonical,encoded

ROOT=Path(__file__).resolve().parents[1]
PACK='research/p3-box-event-322';DATA='rouge/data/box-event-reference.json'
CURRENT='research/p3-expansion-313/current-topic.json'
GROUPS={
    'protect':['choice_ro6_end2_1','choice_ro6_end2_4','choice_ro6_end2_7'],
    'normal_battle':['choice_ro6_end2_3'],'leave':['choice_ro6_end2_2'],
    'covenant':['choice_ro6_end2_5'],'print':['choice_ro6_end2_6'],
}


def build(root=ROOT):
    root=Path(root);receipt=json.loads((root/PACK/'source-receipt.json').read_bytes());raw=(root/receipt['selected_file']).read_bytes()
    if receipt['revision']!=352356 or sha256(raw).hexdigest()!=receipt['selected_sha256']or len(raw)!=receipt['selected_bytes']:
        raise ValueError('Exact investigation document required.')
    nodes=list(Document(raw.decode('utf8')).root.walk());tables=[n for n in nodes if n.tag=='table']
    if len(tables)!=2 or canonical(tables[0].text())!='调查中':raise ValueError('Keep the actual investigation banner.')
    current=json.loads((root/CURRENT).read_bytes())['details'];originals={g:{}for g in('scenes','choices','stages','items')}
    scenes={};choices={};entry=None;active=None;pending=None;document_option=None;used=set()
    for ri,tr in enumerate(n for n in tables[1].walk()if n.tag=='tr'):
        for ci,cell in enumerate(n for n in tr.children if isinstance(n,Node)and n.tag in('td','th')):
            text=canonical(cell.text());loc={'file':receipt['selected_file'],'table':1,'row':ri,'cell':ci,'text_sha256':sha256(cell.text().encode()).hexdigest(),'attributes':cell.attrs}
            if not text or text=='主选项':continue
            if re.fullmatch('选项[一二三四]',text):document_option=text;active=entry;pending=None;continue
            if cell.tag=='th':
                ids=[k for k,v in current['choiceScenes'].items()if v['title']=='窥视箱中'and canonical(v['description'])==text]
                if len(ids)!=1 or ids[0]in scenes:raise ValueError('Unique unrepeated current scene required.')
                sid=ids[0]
                if pending is not None and choices[pending]['next_scene_id']!=sid:raise ValueError('Declared nextSceneId disagrees with narrative.')
                active=sid;pending=None
                if entry is None:entry=sid
                scenes[sid]={'id':sid,'choice_ids':[],'source':loc};originals['scenes'][sid]=deepcopy(current['choiceScenes'][sid]);continue
            ids=[k for k,v in current['choices'].items()if text.startswith(canonical(v['title'])+canonical(v.get('description')))]
            matches=[k for k,v in GROUPS.items()if set(v)==set(ids)]
            if len(matches)!=1 or active is None:raise ValueError('Preserve all matching variants, not a guessed representative.')
            key=matches[0]
            if key in used:raise ValueError('Repeated document choice.')
            used.add(key);records=[current['choices'][i]for i in ids]
            # The document supports only common wording and common next scene, never variant selection.
            common={(r['title'],r['description'],r['nextSceneId'])for r in records}
            if len(common)!=1:raise ValueError('Variants disagree on displayed wording or destination.')
            title,description,target=next(iter(common));stages=[]
            for name in ('混沌源阶理论','失恒常量'):
                if '前往ISW-DF'+name in text.replace('_',''):
                    stage_ids=[k for k,v in current['stages'].items()if v['name']==name and v['code']=='ISW-DF']
                    if len(stage_ids)!=1:raise ValueError('Unique explicitly named current stage required.')
                    stages.extend(stage_ids)
            if stages and key not in('normal_battle','covenant'):raise ValueError('Do not move document links to neighboring choices.')
            choices[key]={'id':key,'scene_id':active,'title':title,'description':description,'variant_ids':list(GROUPS[key]),'next_scene_id':target,'stage_ids':stages,'item_id':None,'source':loc,'document_option_label':document_option,'requires_covenant':key=='covenant','actual_variant_id':None,'game_parent_scene_verified':False,'battle_destination_unbound':key=='print'}
            scenes[active]['choice_ids'].append(key)
            for cid in GROUPS[key]:
                originals['choices'][cid]=deepcopy(current['choices'][cid]);iid=(current['choices'][cid].get('displayData')or{}).get('itemId')
                if iid:originals['items'][iid]=deepcopy(current['items'][iid])
            for sid in stages:originals['stages'][sid]=deepcopy(current['stages'][sid])
            pending=key if target else None
    if entry!='scene_ro6_end2_enter'or len(scenes)!=4 or used!=set(GROUPS)or pending is not None:raise ValueError('Keep the whole four-scene/five-option table.')
    if choices['covenant']['stage_ids']!=['ro6_b_5_b']or choices['normal_battle']['stage_ids']!=['ro6_b_5']or choices['print']['stage_ids']:raise ValueError('Keep named maps and unbound confirmation separate.')
    if scenes[entry]['choice_ids']!=['protect','leave','covenant','print']or scenes['scene_ro6_end2_2']['choice_ids']!=['normal_battle']:raise ValueError('Respect the source table grouping, not a supposed game script.')
    covenant=[k for k,v in current['items'].items()if v['name']=='祭日之契'and v['type']=='RELIC']
    if covenant!=['rogue_6_relic_final_8']:raise ValueError('Exact current covenant identity required.')
    originals['items'][covenant[0]]=deepcopy(current['items'][covenant[0]])
    result={'schema':'box_event_322_v1','game_commit':'bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d','event':{'id':'box','title':'窥视箱中','entry_scene_id':entry,'scene_ids':list(scenes),'choice_ids':list(choices)},'scenes':scenes,'choices':choices,'originals':originals,'source':receipt,'covenant_item_id':covenant[0],'document_under_investigation':True,'all_game_options_verified':False,'game_parent_script_restored':False,'actual_server_eligible':None,'actual_variant_selected':None,'actual_battle_entered':None,'run_updated':False}
    data=encoded(result);names=[CURRENT,PACK+'/source-receipt.json',receipt['selected_file']]
    files={n:{'bytes':len((root/n).read_bytes()),'sha256':sha256((root/n).read_bytes()).hexdigest()}for n in names};files[DATA]={'bytes':len(data),'sha256':sha256(data).hexdigest()}
    manifest=encoded({'schema':'box_event_322_manifest_v1','game_commit':result['game_commit'],'files':files});return data,manifest


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output-dir',type=Path);parser.add_argument('--check',action='store_true');args=parser.parse_args();data,manifest=build()
    if args.output_dir:
        args.output_dir.mkdir(parents=True,exist_ok=False);(args.output_dir/'box-event-reference.json').write_bytes(data);(args.output_dir/'runtime-manifest.json').write_bytes(manifest)
    if args.check:assert(ROOT/DATA).read_bytes()==data and(ROOT/PACK/'runtime-manifest.json').read_bytes()==manifest
    print(json.dumps({'scenes':4,'documented_options':5,'primary_variants':7,'stage_references':2,'manifest_sha256':sha256(manifest).hexdigest()}))
