"""Preserve the whole six-fog document and all explicitly associated original records."""
from pathlib import Path
from hashlib import sha256
from copy import deepcopy
import argparse,json,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.build_documented_event_flows_321 import Document,Node,canonical,encoded
ROOT=Path(__file__).resolve().parents[1];PACK='research/p3-current-portal-341';DATA='rouge/data/current-portal.json'
CURRENT='research/p3-expansion-313/current-topic.json';BASELINE='research/p3-expansion-313/baseline-topic.json';LEGACY='rouge/data/node-catalog.json';TITLE='溯源'
FOGS=('红雾','蓝雾','绿雾','金雾','橙雾','紫雾')

def build(root=ROOT):
    root=Path(root);receipt=json.loads((root/PACK/'source-receipt.json').read_bytes());raw=(root/receipt['selected_file']).read_bytes()
    if receipt['revision']!=352356 or len(raw)!=receipt['selected_bytes']or sha256(raw).hexdigest()!=receipt['selected_sha256']:raise ValueError('Complete exact table required')
    d=json.loads((root/CURRENT).read_bytes())['details'];old=json.loads((root/BASELINE).read_bytes())['details'];doc=Document(raw.decode())
    tables=[n for n in doc.root.walk()if n.tag=='table']
    if len(tables)!=1:raise ValueError('One complete portal table required')
    trs=[n for n in tables[0].walk()if n.tag=='tr']
    if len(trs)!=15:raise ValueError('Keep all fifteen rows')
    def cells(i):return[n for n in trs[i].children if isinstance(n,Node)and n.tag in('th','td')]
    if cells(2)[0].attrs.get('rowspan')!='11'or canonical(cells(2)[0].text())!='零件箱内有【加工品】':raise ValueError('Do not omit has-part row span')
    if cells(13)[0].attrs.get('rowspan')!='2'or canonical(cells(13)[0].text())!='零件箱内没有【加工品】':raise ValueError('Do not omit no-part row span')
    os={k:deepcopy(v)for k,v in d['choiceScenes'].items()if v['title']==TITLE}
    oc={k:deepcopy(v)for k,v in d['choices'].items()if v.get('nextSceneId')in os or(v['title']=='成功了'and v['description']=='进入黑潭'and v['type']=='TELEPORT')}
    if (len(os),len(oc))!=(76,114):raise ValueError('Current complete original coverage changed')
    scenes={'overview':{'id':'overview','label':'先选择雾色资料','description':None,'choice_ids':[],'source_scene_ids':[]}};choices={}
    def scene(key,label,text):
        ids=[k for k,v in os.items()if canonical(v['description'])==canonical(text)]
        if not ids:raise ValueError('Full narrative missing from current original')
        scenes[key]={'id':key,'label':label,'description':text,'choice_ids':[],'source_scene_ids':ids};return key
    tabs=[n for n in cells(1)[0].walk()if n.tag=='div'and 'tabbertab'in n.attrs.get('class','').split()]
    if tuple(t.attrs['title']for t in tabs)!=FOGS:raise ValueError('Preserve all six named fog tabs')
    for tab in tabs:scene('fog:'+tab.attrs['title'],tab.attrs['title']+' · 起始对话',tab.text().strip())
    for i,row in enumerate((3,6,9),1):scene('after:'+str(i),'使用第'+str(i)+'条加工品选项后的对话',cells(row)[0].text().strip())
    leave_tabs=[n for n in cells(12)[0].walk()if n.tag=='div'and 'tabbertab'in n.attrs.get('class','').split()]
    if [t.attrs['title']for t in leave_tabs]!=['红/蓝/绿雾','绿/金/橙/紫雾']:raise ValueError('Keep overlapping green labels')
    for i,t in enumerate(leave_tabs):scene('leave:'+str(i),'离开对话'+str(i+1)+' · '+t.attrs['title'],t.text().strip())
    scene('no-engine','没有加工品后的对话',cells(14)[0].text().strip())
    def matched(text,title=None,next_text=None):
        ids=[k for k,v in oc.items()if(title is None or v['title']==title)and canonical(v['title']+(v.get('description')or''))==canonical(text)
             and(next_text is None or v['nextSceneId']in os and canonical(os[v['nextSceneId']]['description'])==canonical(next_text))]
        if not ids:raise ValueError('Full documented choice not in current originals')
        return ids
    def choice(key,ids,role,next_scene,inventory,source_row):
        v=oc[ids[0]]
        if len({(oc[i]['title'],oc[i]['description'],oc[i]['type'])for i in ids})!=1:raise ValueError('Do not merge different complete choices')
        choices[key]={'id':key,'title':v['title'],'description':v['description'],'role':role,'variant_ids':ids,'next_scene_id':next_scene,
                      'stage_ids':[],'inventory_rule':inventory,'actual_variant':None,'actual_eligible':None,'source_row':source_row}
    for i,row in enumerate((2,5,8),1):
        text=cells(row)[-1].text();ids=matched(text,next_text=scenes['after:'+str(i)]['description']);choice('pay:'+str(i),ids,'pay','after:'+str(i),'has',row)
        if len(ids)!=19 or any(oc[k]['type']!='SCRAP_PAY_SHOW'for k in ids):raise ValueError('All nineteen payment variants required')
        ids=matched(cells(row+2)[0].text());choice('confirm:'+str(i),ids,'teleport',None,None,row+2)
        if len(ids)!=19 or any(oc[k]['nextSceneId']is not None or oc[k]['type']!='TELEPORT'for k in ids):raise ValueError('No invented teleport destination')
        scenes['after:'+str(i)]['choice_ids']=['confirm:'+str(i)]
    leave_text=cells(11)[-1].text()
    for i,tab in enumerate(leave_tabs):
        ids=matched(leave_text,next_text=tab.text());choice('leave:'+str(i),ids,'leave','leave:'+str(i),'has',11)
    normal=matched('我们无法发动引擎没有可用的加工品');alt=matched('无法发动引擎没有可用的加工品')
    if len(normal)!=18 or len(alt)!=1:raise ValueError('Keep both no-engine captions')
    choice('no-engine:normal',normal,'no_engine','no-engine','none',13);choice('no-engine:alt',alt,'no_engine','no-engine','none',13)
    if '◈红雾情况下有概率为：'not in cells(13)[1].text():raise ValueError('Keep red alternative annotation')
    for fog in FOGS:
        ids=['pay:1','pay:2','pay:3']
        for i,t in enumerate(leave_tabs):
            if fog.replace('雾','')in t.attrs['title'].replace('雾','').split('/'):ids.append('leave:'+str(i))
        ids+=['no-engine:normal']+(['no-engine:alt']if fog=='红雾'else[]);scenes['fog:'+fog]['choice_ids']=ids
    for i in range(2):choices['leave:'+str(i)]['title']+=' · 资料对话'+str(i+1)
    choices['no-engine:alt']['title']+='（红雾资料变体）'
    if len(scenes)!=13 or len(choices)!=10:raise ValueError('Keep all document contexts and choices')
    covered_scenes={k for s in scenes.values()for k in s['source_scene_ids']};covered_choices={k for c in choices.values()for k in c['variant_ids']}
    if covered_scenes!=set(os)or covered_choices!=set(oc):raise ValueError('No dropped original records')
    legacy=next(e for e in json.loads((root/LEGACY).read_bytes())['events']if e['title']==TITLE);links=[]
    for s in legacy['scenes']:
        for sid in s['game_scene_ids']:
            if sid not in os or canonical(s['description'])!=canonical(os[sid]['description']):raise ValueError('Do not fuzz legacy narrative')
            links.append({'legacy_scene_key':s['key'],'current_original_scene_id':sid,'complete_description':s['description']})
    if len(links)!=44 or legacy['scenes'][0]['game_scene_ids']:raise ValueError('Keep old entry unbound and44 exact later scene references')
    result={'schema':'current_portal_341_v1','game_commit':'bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d','event':{'id':'portal','title':TITLE,'entry_scene_id':'overview','scene_ids':list(scenes),'choice_ids':list(choices)},
            'scenes':scenes,'choices':choices,'originals':{'scenes':os,'choices':oc,'items':{},'stages':{}},'original_choice_association':{k:('explicit_destination_scene'if v['nextSceneId']in os else'full_literal_teleport_candidate')for k,v in oc.items()},'source':receipt,'complete_document_table':True,'complete_game_option_pool':False,
            'actual_eligible':None,'run_updated':False,'green_leave_label_overlap_unresolved':True,'legacy_initial_scene_remains_unbound':True,
            'catalogue_binding':{'expected_legacy_event':legacy,'expected_summary':{k:deepcopy(legacy[k])for k in('id','title','node_types','floors','natural','natural_reason','entry')},'exact_scene_links':links,'current_event_id':'portal'},
            'complete_selected_record_comparison_to_baseline':{'scenes':{k:old['choiceScenes'].get(k)==v for k,v in os.items()},'choices':{k:old['choices'].get(k)==v for k,v in oc.items()}}}
    data=encoded(result);names=[CURRENT,BASELINE,LEGACY,PACK+'/source-receipt.json',PACK+'/source-notes.json',receipt['selected_file']];files={n:{'bytes':len((root/n).read_bytes()),'sha256':sha256((root/n).read_bytes()).hexdigest()}for n in names};files[DATA]={'bytes':len(data),'sha256':sha256(data).hexdigest()}
    return data,encoded({'schema':'current_portal_341_manifest_v1','game_commit':result['game_commit'],'files':files})
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args();d,m=build()
    if a.check:
        if(ROOT/DATA).read_bytes()!=d or(ROOT/PACK/'runtime-manifest.json').read_bytes()!=m:raise ValueError('Build differs')
    else:(ROOT/DATA).write_bytes(d);(ROOT/PACK/'runtime-manifest.json').write_bytes(m)
    print(json.dumps({'original_scenes':76,'original_choices':114,'fog_tabs':6,'document_contexts':13,'document_choices':10,'manifest_sha256':sha256(m).hexdigest()}))
