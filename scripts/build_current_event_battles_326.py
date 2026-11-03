"""Complete fixed-document named battle links, explicit exclusions, no parent guesses."""
from pathlib import Path
from hashlib import sha256
from copy import deepcopy
from urllib.parse import unquote
import argparse,json,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.build_documented_event_flows_321 import Document,Node,canonical,encoded
ROOT=Path(__file__).resolve().parents[1];PACK='research/p3-current-event-battles-326';DATA='rouge/data/current-event-battles.json';CURRENT='research/p3-expansion-313/current-topic.json';BASELINE='research/p3-expansion-313/baseline-topic.json'

def build(root=ROOT):
    root=Path(root);receipt=json.loads((root/PACK/'source-receipt.json').read_bytes());raw=(root/receipt['selected_file']).read_bytes()
    if receipt['revision']!=352356 or len(raw)!=receipt['selected_bytes']or sha256(raw).hexdigest()!=receipt['selected_sha256']:raise ValueError('Exact complete selected named-link tables required.')
    current=json.loads((root/CURRENT).read_bytes())['details'];baseline=json.loads((root/BASELINE).read_bytes())['details'];nodes=list(Document(raw.decode()).root.walk());events={};choices={};originals={k:{}for k in('choices','scenes','stages')};cells=0
    for head in(n for n in nodes if n.tag=='h3'):
        title=head.attrs['id'];table=next(n for n in nodes[nodes.index(head)+1:]if n.tag in('table','h3'))
        if table.tag!='table'or title in events:raise ValueError('One whole table per event required.')
        event={'id':title,'title':title,'choice_ids':[],'related_scene_ids':[]};events[title]=event
        for ri,tr in enumerate(n for n in table.walk()if n.tag=='tr'):
            for ci,cell in enumerate(n for n in tr.children if isinstance(n,Node)and n.tag in('td','th')):
                anchors=[a for a in cell.walk()if a.tag=='a'and'ISW-'in a.text()]
                if not anchors:continue
                cells+=1;text=canonical(cell.text());matches={k:v for k,v in current['choices'].items()if v.get('title')and v.get('description')and text.startswith(canonical(v['title'])+canonical(v['description']))}
                if len(matches)!=1:raise ValueError('Full current caption must identify one choice, not ID or title guessing.')
                cid,original=next(iter(matches.items()));pages=[];admitted=[];excluded=[];unbound=[]
                emergency='（紧急作战）'in text
                for a in anchors:
                    page=a.attrs.get('title','');href=unquote(a.attrs.get('href',''));label=canonical(a.text()).replace('_','')
                    if not page.startswith('ISW-')or not href.startswith('/arknights/ISW-'):raise ValueError('Exact named game stage page required.')
                    code,name=page.split(' ',1)
                    if canonical(code+name)!=label:raise ValueError('Do not repair or guess an anchor target.')
                    hits={k:v for k,v in current['stages'].items()if v['name']==name and v['code']==code}
                    if not hits:raise ValueError('A named stage is absent from the complete current table.')
                    for k,v in hits.items():
                        if type(v['isElite'])is not int or v['isElite']not in(0,1)or(v['isElite']==1)!=(v['difficulty']=='FOUR_STAR'):raise ValueError('Inconsistent emergency stage fields.')
                        originals['stages'][k]=deepcopy(v)
                    incompatible=[k for k,v in hits.items()if emergency and not v['isElite']];remaining={k:v for k,v in hits.items()if k not in incompatible}
                    if not remaining:raise ValueError('Explicit emergency target has no matching current configuration.')
                    ambiguous=len({v['levelId']for v in remaining.values()})!=1
                    target={'page_title':page,'href':'https://wiki.biligame.com'+a.attrs['href'],'anchor_text':a.text(),'code':code,'name':name,'candidate_stage_ids':list(hits),'admitted_stage_ids':[]if ambiguous else list(remaining),'excluded_stage_ids':incompatible,'unbound_stage_ids':list(remaining)if ambiguous else[],'explicit_emergency':emergency,'actual_stage_id':None,'single_level_family':not ambiguous}
                    pages.append(target);admitted+=target['admitted_stage_ids'];excluded+=incompatible;unbound+=target['unbound_stage_ids']
                loc={'file':receipt['selected_file'],'heading':title,'row':ri,'cell':ci,'full_text':cell.text(),'attributes':cell.attrs,'text_sha256':sha256(cell.text().encode()).hexdigest()}
                row={'id':cid,'event_id':title,'title':original['title'],'description':original['description'],'pages':pages,'stage_ids':admitted,'excluded_stage_ids':excluded,'unbound_stage_ids':unbound,'explicit_emergency':emergency,'actual_stage_id':None,'actual_eligible':None,'parent_scene_id':None,'document_cells':[loc]}
                if cid in choices:
                    previous=choices[cid];old=deepcopy(previous);old['document_cells']=[loc]
                    if old!=row:raise ValueError('Same-caption repeated cells disagree on exact stage scope.')
                    previous['document_cells'].append(loc)
                else:choices[cid]=row;event['choice_ids'].append(cid);originals['choices'][cid]=deepcopy(original)
        for sid,scene in current['choiceScenes'].items():
            if scene['title']==title:event['related_scene_ids'].append(sid);originals['scenes'][sid]=deepcopy(scene)
    counts={'events':len(events),'document_cells':cells,'choices':len(choices),'admitted_choice_stage_refs':sum(len(c['stage_ids'])for c in choices.values()),'excluded_refs':sum(len(c['excluded_stage_ids'])for c in choices.values()),'unbound_refs':sum(len(c['unbound_stage_ids'])for c in choices.values()),'admitted_stage_ids':len({s for c in choices.values()for s in c['stage_ids']})}
    if counts!={'events':9,'document_cells':13,'choices':12,'admitted_choice_stage_refs':20,'excluded_refs':3,'unbound_refs':0,'admitted_stage_ids':17}:raise ValueError('Preserve every selected link, repeated cell, exclusion and unresolved same-name family: '+str(counts))
    comparison={g:{k:baseline['choiceScenes'if g=='scenes'else g].get(k)==v for k,v in records.items()}for g,records in originals.items()}
    data={'schema':'current_event_battles_326_v1','game_commit':'bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d','events':events,'choices':choices,'originals':originals,'counts':counts,'complete_selected_record_comparison_to_baseline':comparison,'source':receipt,'actual_event_eligible':None,'actual_entered':None,'parent_script_restored':False,'complete_event_option_pool':False,'current_server_verified':False,'run_updated':False}
    blob=encoded(data);names=[CURRENT,BASELINE,PACK+'/source-receipt.json',receipt['selected_file']];files={n:{'bytes':len((root/n).read_bytes()),'sha256':sha256((root/n).read_bytes()).hexdigest()}for n in names};files[DATA]={'bytes':len(blob),'sha256':sha256(blob).hexdigest()}
    return blob,encoded({'schema':'current_event_battles_326_manifest_v1','game_commit':data['game_commit'],'files':files})

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output-dir',type=Path);p.add_argument('--check',action='store_true');args=p.parse_args();d,m=build()
    if args.output_dir:args.output_dir.mkdir(parents=True,exist_ok=False);(args.output_dir/'current-event-battles.json').write_bytes(d);(args.output_dir/'runtime-manifest.json').write_bytes(m)
    if args.check:assert(ROOT/DATA).read_bytes()==d and(ROOT/PACK/'runtime-manifest.json').read_bytes()==m
    print(json.dumps({'counts':json.loads(d)['counts'],'manifest_sha256':sha256(m).hexdigest()}))
