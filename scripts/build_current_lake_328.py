"""Lake event: explicit repeated-note mapping and separate documented outcomes."""
from pathlib import Path
from hashlib import sha256
from copy import deepcopy
import argparse,json,re,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.build_documented_event_flows_321 import Document,Node,canonical,encoded
ROOT=Path(__file__).resolve().parents[1];PACK='research/p3-current-lake-328';DATA='rouge/data/current-lake.json';CURRENT='research/p3-expansion-313/current-topic.json';BASELINE='research/p3-expansion-313/baseline-topic.json'

def build(root=ROOT):
    root=Path(root);receipt=json.loads((root/PACK/'source-receipt.json').read_bytes());raw=(root/receipt['selected_file']).read_bytes()
    if receipt['revision']!=352356 or len(raw)!=receipt['selected_bytes']or sha256(raw).hexdigest()!=receipt['selected_sha256']:raise ValueError('Whole exact lake event table required.')
    current=json.loads((root/CURRENT).read_bytes())['details'];old=json.loads((root/BASELINE).read_bytes())['details'];table=next(n for n in Document(raw.decode()).root.walk()if n.tag=='table');cells=[];scene_cells={};captions=[];repeat=None;originals={g:{}for g in('scenes','choices','items','stages')}
    def exact_scene(text):
        ids=[k for k,v in current['choiceScenes'].items()if v['title']=='湖中仙女'and canonical(v['description'])==text]
        if len(ids)!=1:raise ValueError('Narrative must identify one exact current scene.')
        return ids[0]
    for ri,tr in enumerate(n for n in table.walk()if n.tag=='tr'):
        for ci,cell in enumerate(n for n in tr.children if isinstance(n,Node)and n.tag in('td','th')):
            text=canonical(cell.text());loc={'file':receipt['selected_file'],'row':ri,'cell':ci,'attributes':cell.attrs,'text':cell.text(),'text_sha256':sha256(cell.text().encode()).hexdigest()};cells.append((cell,text,loc))
            if not text:continue
            if cell.tag=='th':
                sid=exact_scene(text);scene_cells.setdefault(sid,[]).append(loc);originals['scenes'][sid]=deepcopy(current['choiceScenes'][sid]);continue
            if '若在第一轮环节选择该选项'in text:
                if repeat is not None or'若在第二轮环节再次选择该选项'not in text:raise ValueError('Keep the complete explicit repetition note.')
                hits=[k for k,v in current['choiceScenes'].items()if v['title']=='湖中仙女'and canonical(v['description'])in text]
                if len(hits)!=1:raise ValueError('Quoted repeat narrative must be unique.')
                sid=hits[0];scene_cells.setdefault(sid,[]).append(loc);originals['scenes'][sid]=deepcopy(current['choiceScenes'][sid]);repeat={'scene_id':sid,'source':loc};continue
            if text in('主选项','选项一分支','分支1后续')or re.fullmatch(r'选项[一二]|分支[123](?:\.[123])?(?:（随机）)?|情况[12]',text):continue
            matches={k:v for k,v in current['choices'].items()if v.get('title')and v.get('description')and text.startswith(canonical(v['title'])+canonical(v['description']))}
            if not matches:raise ValueError('Do not skip any complete documented option caption.')
            # A second pass below identifies the immediately following narrative.
            captions.append({'matches':matches,'text':text,'source':loc,'cell':cell})
    if repeat is None:raise ValueError('Missing explicit repeated-phase note.')
    selected={};locations={};random_outcomes=[]
    for row in captions:
        index=next(i for i,(cell,_,_)in enumerate(cells)if cell is row['cell']);next_th=next((text for cell,text,_ in cells[index+1:]if cell.tag=='th'),None);next_sid=exact_scene(next_th)if next_th else None;matches=row['matches']
        if len(matches)>1:
            explicit={k:v for k,v in matches.items()if v['nextSceneId']is not None and v['nextSceneId']==next_sid}
            if explicit:matches=explicit
        if len(matches)>1:
            matches={k:v for k,v in matches.items()if v['type']=='NEXT_PROB'and v['nextSceneId']is None}
            if len(matches)!=1 or'分支1.1（随机）'not in canonical(table.text())or next_sid is None:raise ValueError('Do not turn ambiguous continuation into a chosen outcome.')
            random_outcomes.append({'scene_id':next_sid,'source':row['source'],'actual_result':None,'probability':None})
        if len(matches)!=1:raise ValueError('One exact original choice per caption context required.')
        cid,v=next(iter(matches.items()));selected[cid]=v;locations.setdefault(cid,[]).append(row['source'])
        if v['nextSceneId']is not None and v['nextSceneId']!=next_sid:raise ValueError('Original nextSceneId contradicts the documented following narrative.')
    repeat_ids=[k for k,v in current['choices'].items()if v['nextSceneId']==repeat['scene_id']and v['title']=='继续拿出诚意'and canonical(v['description'])=='失去1源石锭']
    if len(repeat_ids)!=1:raise ValueError('Unique current repeated choice must explicitly target the quoted watch narrative.')
    rid=repeat_ids[0];selected[rid]=current['choices'][rid];locations[rid]=[repeat['source']];originals['choices']={k:deepcopy(v)for k,v in selected.items()}
    def unique_title(title):
        ids=[k for k,v in selected.items()if v['title']==title]
        if len(ids)!=1:raise ValueError('Unique named source action required: '+title)
        return ids[0]
    entry=next(iter(scene_cells));approach=unique_title('上前看看');ignore=unique_title('不理会她');pay=unique_title('拿出诚意');reject=unique_title('休想骗我');leave=unique_title('离开');normal=unique_title('到此为止了！');urgent=unique_title('我不要困在这里！');claim=unique_title('获得了奖励');prob_ids=[k for k,v in selected.items()if v['type']=='NEXT_PROB']
    if len(prob_ids)!=1 or len(random_outcomes)!=2 or len({x['scene_id']for x in random_outcomes})!=2:raise ValueError('Exactly two documented outcomes, no probability inference.')
    random_id=prob_ids[0];request=selected[approach]['nextSceneId'];magnet=selected[pay]['nextSceneId'];watch=repeat['scene_id'];expose=selected[reject]['nextSceneId'];decline=selected[leave]['nextSceneId'];gift=next(x['scene_id']for x in random_outcomes if x['scene_id']==next(s for s,v in originals['scenes'].items()if'捞出一件礼物'in v['description']));danger=next(x['scene_id']for x in random_outcomes if x['scene_id']!=gift)
    labels={entry:'最初对话 · 湖中仙女',request:'她询问你的虔诚',magnet:'已经捞出磁石',watch:'已经捞出破损手表',selected[ignore]['nextSceneId']:'没有理会她',expose:'识破倒影',decline:'离开湖边',danger:'随机结果：陷入险境',gift:'随机结果：捞出礼物',selected[claim]['nextSceneId']:'拿走宝物后的对话'}
    parents={entry:[approach,ignore],request:[pay,reject,leave],magnet:[rid,reject,leave],watch:[random_id,reject,leave],expose:[normal],danger:[urgent],gift:[claim]};scenes={sid:{'id':sid,'event_id':'lake','label':labels[sid],'choice_ids':parents.get(sid,[]),'source_cells':sources}for sid,sources in scene_cells.items()}
    choices={}
    for cid,v in selected.items():
        battle=cid in(normal,urgent);cost=1 if canonical(v['description'])=='失去1源石锭'else None
        choices[cid]={'id':cid,'title':v['title'],'description':v['description'],'event_id':'lake','scene_ids':[s for s,cs in parents.items()if cid in cs],'next_scene_id':v['nextSceneId'],'stage_ids':[],'has_documented_battle_link':battle,'source_cells':locations[cid],'mapping_basis':'explicit_repeat_note_plus_unique_current_nextSceneId'if cid==rid else'documented_caption_and_current_record','gold_cost_reference':cost,'reward_reference':{'quantity':1,'quality':'珍贵','kind':'收藏品','pool':None}if cid==claim else None,'documented_outcomes':deepcopy(random_outcomes)if cid==random_id else[],'actual_outcome':None,'actual_eligible':None,'actual_consumed':None,'actual_received':None,'actual_parent_scene_id':None}
    if any(not c['scene_ids']for c in choices.values()):raise ValueError('Every original action needs a declared document context.')
    counts={'scenes':len(scenes),'original_choices':len(choices),'caption_cells':len(captions),'scene_choice_references':sum(len(s['choice_ids'])for s in scenes.values()),'random_outcomes':len(random_outcomes),'pay_actions':sum(c['gold_cost_reference']is not None for c in choices.values()),'named_battle_choices':sum(c['has_documented_battle_link']for c in choices.values())}
    if counts!={'scenes':10,'original_choices':10,'caption_cells':13,'scene_choice_references':14,'random_outcomes':2,'pay_actions':3,'named_battle_choices':2}:raise ValueError('Whole lake scope mismatch: '+str(counts))
    comparison={g:{k:old['choiceScenes'if g=='scenes'else g].get(k)==v for k,v in records.items()}for g,records in originals.items()};data={'schema':'current_lake_328_v1','game_commit':'bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d','event':{'id':'lake','title':'湖中仙女','entry_scene_id':entry,'scene_ids':list(scenes),'choice_ids':list(choices)},'scenes':scenes,'choices':choices,'originals':originals,'counts':counts,'repeat_note':repeat,'source':receipt,'complete_selected_record_comparison_to_baseline':comparison,'actual_probability':None,'actual_outcome':None,'complete_game_option_pool':False,'game_parent_script_restored':False,'run_updated':False}
    blob=encoded(data);names=[CURRENT,BASELINE,PACK+'/source-receipt.json',receipt['selected_file']];files={n:{'bytes':len((root/n).read_bytes()),'sha256':sha256((root/n).read_bytes()).hexdigest()}for n in names};files[DATA]={'bytes':len(blob),'sha256':sha256(blob).hexdigest()};return blob,encoded({'schema':'current_lake_328_manifest_v1','game_commit':data['game_commit'],'files':files})

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output-dir',type=Path);p.add_argument('--check',action='store_true');args=p.parse_args();d,m=build()
    if args.output_dir:args.output_dir.mkdir(parents=True,exist_ok=False);(args.output_dir/'current-lake.json').write_bytes(d);(args.output_dir/'runtime-manifest.json').write_bytes(m)
    if args.check:assert(ROOT/DATA).read_bytes()==d and(ROOT/PACK/'runtime-manifest.json').read_bytes()==m
    print(json.dumps({'counts':json.loads(d)['counts'],'manifest_sha256':sha256(m).hexdigest()}))
