"""Build exact one-hop resting-corner references from pinned public originals."""
from copy import deepcopy
from hashlib import sha256
from html import unescape
from html.parser import HTMLParser
import argparse
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
EVENT='community_group_023'
PACKET='research/p3-resting-results-293'
DATA='rouge/data/resting-corner-results.json'
CATALOG='rouge/data/node-catalog.json'
CATALOG_SHA='7df1d94bb69650eb19fc811af661e54d44bf07d72b1c0793de511adc1b2e915d'
GAME='.cache/game-data/roguelike_topic_table.json'
GAME_SHA='f5867e55d09472253083486174aa47bd94dd48b07684b74b60a5b29ca00eda86'
GAME_COMMIT='a550f5e048bb94e7cdefc6eb97a4091f0c4c7add'
HTML={
    '427904':('research/p3-peace-guardian-results-291/prts-events-427904.html','faa088b0474e75806b357df8648c6a59b1be6dcbc9be749db7c934ca9e6307e9'),
    '440271':('research/p3-peace-guardian-results-291/prts-events-440271.html','e04971ad361436e5bb3721883423d98ad66636d5156794dd6221a977ffd6dac8')}
ORIGINS=((1,0,3),(6,0,2),(9,1,2),(11,0,2))
FUTURE={
    2:('抚摸小狗的脑袋','获得20希望',20,'hope',None,'choice_ro6_surprise_2'),
    3:('目送豹子们远去','获得1件珍贵的加工品',1,None,'珍贵的加工品','choice_ro6_surprise_8'),
    4:('闭眼感受','获得15护盾',15,'shield',None,'choice_ro6_surprise_3'),
    5:('拾起松鼠落下的橡实','获得1件珍贵的加工品',1,None,'珍贵的加工品','choice_ro6_surprise_4'),
    7:('帮忙采摘','获得15护盾',15,'shield',None,'choice_ro6_surprise_7'),
    10:('进入神秘空间','获得99源石锭',99,'gold',None,None)}


class _Node:
    def __init__(self,tag,attrs):self.tag=tag;self.attrs=dict(attrs);self.children=[]


class _Document(HTMLParser):
    VOID={'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
    def __init__(self,text):
        super().__init__(convert_charrefs=True);self.nodes=[];self.stack=[_Node('root',[])];self.feed(text)
    def handle_starttag(self,tag,attrs):
        node=_Node(tag,attrs);self.nodes.append(node);self.stack[-1].children.append(node)
        if tag not in self.VOID:self.stack.append(node)
    def handle_startendtag(self,tag,attrs):
        self.handle_starttag(tag,attrs)
        if tag not in self.VOID:self.handle_endtag(tag)
    def handle_endtag(self,tag):
        for i in range(len(self.stack)-1,0,-1):
            if self.stack[i].tag==tag:del self.stack[i:];break
    def handle_data(self,value):self.stack[-1].children.append(value)


def _text(node):
    if isinstance(node,str):return node
    return ''.join(_text(child)+('\n' if isinstance(child,_Node) and child.tag in ('br','p','li') else '') for child in node.children)


def _descendants(node):
    for child in node.children:
        if isinstance(child,_Node):yield child;yield from _descendants(child)


def _class(node,value):return value in node.attrs.get('class','').split()
def _children(node,value):return [child for child in node.children if isinstance(child,_Node) and _class(child,value)]
def _part(node,name):
    found=[child for child in _descendants(node) if _class(child,name)]
    if len(found)!=1:raise ValueError('Expected one DOM part: '+name)
    return _text(found[0]).strip()
def _plain(value):return re.sub(r'<[@$][^<>]*>|</>','',unescape(value)).strip()
def _normalized(value):return re.sub(r'\s+','',_plain(value).replace('\\n','\n'))
def _json(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
def _pin(raw):return {'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
def _require(value,message):
    if not value:raise ValueError(message)


def build(root=ROOT):
    """Return deterministic artifacts; no writes, network, application or state calls."""
    root=Path(root);catalog_raw=(root/CATALOG).read_bytes();game_raw=(root/GAME).read_bytes()
    _require(sha256(catalog_raw).hexdigest()==CATALOG_SHA,'Fixed catalog bytes differ.')
    _require(sha256(game_raw).hexdigest()==GAME_SHA,'Full original game bytes differ.')
    catalog=json.loads(catalog_raw);event=next(e for e in catalog['events'] if e['id']==EVENT)
    _require(event['title']=='安眠一隅' and len(event['scenes'])==12,'Complete event differs.')
    detail=json.loads(game_raw)['details']['rogue_6']
    originals={'choices':{k:v for k,v in detail['choices'].items() if k.startswith('choice_ro6_surprise_')},
        'choiceScenes':{k:v for k,v in detail['choiceScenes'].items() if k.startswith('scene_ro6_surprise_')}}
    _require(len(originals['choices'])==len(originals['choiceScenes'])==12,'Original 12/12 differs.')
    for scene in event['scenes']:
        for original_id in scene['game_scene_ids']:
            original=originals['choiceScenes'][original_id]
            _require(original['title']==event['title'] and _normalized(original['description'])==_normalized(scene['description']),
                'Complete original scene candidate differs: '+original_id)
    game_source={'url':f'https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/{GAME_COMMIT}/zh_CN/gamedata/excel/roguelike_topic_table.json',
        'commit':GAME_COMMIT,**_pin(game_raw)}
    outputs={};dom_versions={};sources={'original_game':game_source,'community_documents':[]}
    for revision,(relative,digest) in HTML.items():
        raw=(root/relative).read_bytes();_require(sha256(raw).hexdigest()==digest,'HTML byte pin differs: '+revision)
        text=raw.decode('utf-8');_require(re.search(r'"wgRevisionId"\s*:\s*(\d+)',text)[1]==revision,'HTML revision differs.')
        doc=_Document(text);groups=[node for node in doc.nodes if _class(node,'IS-event-data')
            and any(scene.attrs.get('data-name')=='安眠一隅' for scene in _children(node,'scene'))]
        _require(len(groups)==1,'Expected one event group.')
        scenes=_children(groups[0],'scene');_require(len(scenes)==12,'Expected all 12 community scenes.')
        records=[]
        for si,(node,expected) in enumerate(zip(scenes,event['scenes'])):
            _require(node.attrs==expected['attributes'],'Scene attributes differ: '+str(si))
            description=_part(node,'sceneText');_require(description==expected['description'],'Scene text differs: '+str(si))
            choices=_children(node,'choose');_require(len(choices)==len(expected['choices']),'Choice count differs.')
            choice_rows=[]
            for ci,(choice,fixed) in enumerate(zip(choices,expected['choices'])):
                desc=_part(choice,'desc1');notes=[n for n in _descendants(choice) if _class(n,'desc2')]
                _require(len(notes)<=1,'Multiple choice annotations.')
                note=_text(notes[0]).strip() if notes else None
                _require(choice.attrs==fixed['attributes'] and desc==fixed['description'] and note==fixed['conditional'],
                    f'Complete option differs: {si}/{ci}')
                choice_rows.append({'choice_key':fixed['key'],'attributes':choice.attrs,'description':desc,'conditional':note,
                    'subchoice_attribute_raw':choice.attrs.get('data-subchoose')})
            records.append({'scene_key':expected['key'],'attributes':node.attrs,'description':description,'choices':choice_rows})
        packet_path=f'{PACKET}/prts-events-{revision}.html';outputs[packet_path]=raw
        dom_versions[revision]={'source':packet_path,'rows':records}
        sources['community_documents'].append({'revision':revision,'path':packet_path,
            'url':f'https://m.prts.wiki/index.php?title=沉沦者的黑流树海/事件一览&oldid={revision}',**_pin(raw)})
    outputs[f'{PACKET}/original-records.json']=_json({'source':game_source,'records':originals})
    outputs[f'{PACKET}/community-readback.json']=_json({'event_id':EVENT,'versions':dom_versions})
    future={}
    for si,(title,desc,amount,resource,category,original_id) in FUTURE.items():
        scene=event['scenes'][si];_require(len(scene['choices'])==1,'Future scene button count differs.')
        choice=scene['choices'][0]
        _require(choice['key']==f'{EVENT}:scene:{si}:choice:0' and choice['title']==title and choice['description']==desc,'Future button differs.')
        if original_id:
            _require(choice['game_choice_ids']==[original_id],'Future original IDs differ.')
            original=originals['choices'][original_id]
            _require(original['title']==title and _plain(original['description'])==desc,'Full original future button differs.')
            expected_targets=[target['key'] for target in event['scenes'] if original['nextSceneId'] in target['game_scene_ids']]
            _require(bool(choice['destination_keys']) and set(choice['destination_keys'])<=set(expected_targets),
                'Explicit future destination is not compatible with its original candidate.')
        else:
            _require(choice['game_choice_ids']==[] and choice['game_match_basis']=='destination_mismatch','99 gold mismatch must remain.')
            original=originals['choices']['choice_ro6_surprise_12']
            _require(original['title']==title and _plain(original['description'])==desc
                and original['nextSceneId']=='scene_ro6_surprise_1' and choice['destination_keys']==[f'{EVENT}:scene:8'],
                '99 gold original/community mismatch differs.')
        future[scene['key']]={'choice_key':choice['key'],'title':title,'description':desc,'quantity_reference':amount,
            'resource':resource,'category_text':category,'item_pool':None,'game_choice_ids':deepcopy(choice['game_choice_ids']),
            'game_match_basis':choice['game_match_basis'],'actual_granted':None,'source_kind':'future_button_text_reference',
            'original_content_reference_ids':[original_id] if original_id else [],
            'original_entry_relation_verified':False,'original_relation_mismatch':original_id is None}
    cards=[];edges=[]
    by_key={scene['key']:scene for scene in event['scenes']}
    for si,ci,count in ORIGINS:
        scene=event['scenes'][si];choice=scene['choices'][ci]
        _require(choice['key']==f'{EVENT}:scene:{si}:choice:{ci}' and choice['conditional']==f'随机出现以下{count}种奖励中的1种','Random annotation differs.')
        _require(choice['title']==('四处看看' if si==1 else '触碰图案'),'Random choice differs.')
        raw_subchoices=choice['attributes']['data-subchoose'].split(';;')
        _require(len(raw_subchoices)==len(choice['subchoices']),'Source attribute branch count differs.')
        for raw,sub in zip(raw_subchoices,choice['subchoices']):
            parts=raw.split(';')
            _require(len(parts)==2 and parts[1].isdigit() and 0<=int(parts[1])<len(event['scenes']),
                'Source branch must name a valid group-local array index.')
            _require(sub['raw']==raw and sub['parts']==parts
                and sub['community_destination_scene_id']==event['scenes'][int(parts[1])]['key'],
                'Source attribute branch and catalog navigation differ.')
        for cid in choice['game_choice_ids']:
            original=originals['choices'][cid]
            _require(original['title']==choice['title'] and _plain(original['description'])==choice['description']
                and original['type']=='NEXT_PROB' and original['nextSceneId'] is None,'Original random choice differs.')
        branches=[]
        for index,sub in enumerate(choice['subchoices']):
            key=sub['community_destination_scene_id'];_require(key in future and key in by_key,'Subchoice escapes exact six target scenes.')
            branch_id=choice['key']+':sub:'+str(index);target=by_key[key]
            branches.append({'branch_id':branch_id,'label':sub['parts'][0],'target_scene_key':key,
                'target_scene_number':event['scenes'].index(target)+1,'target_scene_description':target['description'],
                'future_buttons':[deepcopy(future[key])],'actual_transition':None,'actual_reward':None})
            edges.append({'choice_key':choice['key'],'branch_id':branch_id,'subchoice':deepcopy(sub),'target_scene_key':key})
        listed=len(branches);matches=count==listed
        conflict='' if matches else f'资料数量对不上：原注写{count}种，这里只列出{listed}项。无法确认是漏项还是说明不准确；以下只列文档已经写出的后续。'
        cards.append({'reference_id':choice['key'],'event_id':EVENT,'scene_key':scene['key'],'scene_number':si+1,
            'choice_key':choice['key'],'choice_title':choice['title'],'source_annotation_text':choice['conditional'],
            'documented_count':count,'listed_branch_count':listed,'count_matches':matches,'conflict_notice':conflict,
            'branches':branches,'full_actual_pool_known':False,'actual_selected_branch':None,'actual_reward':None,
            'actual_selectable':None,'source_scene_link_verified':False,'annotation_role':'future_results_reference'})
    _require([len(card['branches']) for card in cards]==[3,2,1,3] and len(edges)==9,'Four card branch domains differ.')
    source_scenes={key:{'key':key,'scene_number':event['scenes'].index(by_key[key])+1,'description':by_key[key]['description'],
        'edesc_texts':deepcopy(by_key[key]['edesc_texts']),'choices':deepcopy(by_key[key]['choices']),
        'game_scene_ids':deepcopy(by_key[key]['game_scene_ids'])} for key in future}
    data={'schema_version':1,'event_id':EVENT,'expected_event':deepcopy(event),'cards':cards,'scenes':source_scenes,
        'sources':sources,'full_actual_pool_known':False,'current_server_verified':False,'actual_result':None,
        'notice':'这里只整理正在查阅的资料选择及一跳后续；后续按钮奖励不是本次已领取，不相加。完整池、本局触发、可选和领取仍未知。'}
    outputs[DATA]=_json(data)
    outputs[f'{PACKET}/extraction.json']=_json({'source':sources,'complete_original_choice_count':12,'complete_original_scene_count':12,
        'community_scenes_per_version':12,'community_choices_per_version':sum(len(scene['choices']) for scene in event['scenes']),
        'all_four_random_choices_and_nine_subedges':edges,'target_scene_keys':list(source_scenes),
        'scope':'Content and community navigation references only; original source entry and actual server execution unproved.'})
    builder_relative='scripts/build_resting_corner_results_293.py'
    builder_raw=Path(__file__).read_bytes()
    files={path:_pin(raw) for path,raw in outputs.items()}
    files[CATALOG]=_pin(catalog_raw);files[builder_relative]=_pin(builder_raw)
    outputs[f'{PACKET}/source-manifest.json']=_json({'schema_version':1,'files':files,
        'scope':'Four exact random-choice one-hop cards, conflict-aware future button references; no eligibility/state/pool inference.'})
    return outputs


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,default=ROOT);parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();artifacts=build(args.root)
    for relative,raw in artifacts.items():
        path=args.out/relative;path.parent.mkdir(parents=True,exist_ok=True)
        with path.open('xb') as stream:stream.write(raw)
    print(json.dumps({'artifacts':len(artifacts),'full_original_bytes_verified':True,'original_records':[12,12],
        'community_scenes_each_version':12,'random_choices':4,'subedges':9,
        'manifest_sha256':sha256(artifacts[f'{PACKET}/source-manifest.json']).hexdigest()},ensure_ascii=False))


if __name__=='__main__':main()
