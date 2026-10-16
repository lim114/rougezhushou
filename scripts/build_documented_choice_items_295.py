"""Reconstruct one documented item reference; never an original grant binding."""
import argparse
from copy import deepcopy
import hashlib
from html import unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
EVENT='community_group_021'
SCENE=EVENT+':scene:0'
CHOICE=SCENE+':choice:0'
ITEM='rogue_6_relic_final_1'
PACKET='research/p3-documented-choice-items-295'
DATA='rouge/data/documented-choice-items.json'
CATALOG='rouge/data/node-catalog.json'
CATALOG_SHA='7df1d94bb69650eb19fc811af661e54d44bf07d72b1c0793de511adc1b2e915d'
GAME='.cache/p3-287-event-research/fixed-game-topic.json'
GAME_SHA='f5867e55d09472253083486174aa47bd94dd48b07684b74b60a5b29ca00eda86'
GAME_COMMIT='a550f5e048bb94e7cdefc6eb97a4091f0c4c7add'
ICON='rouge/data/relic-icons/'+ITEM+'.png'
ICON_SHA='1d07a123253172ede9a4585abdcd1b301350e096b245bc046539c48f6c6fb825'
ICON_BLOB='874eb15d491afc7cd4c292816bff9e334eb2dab6'
HTMLS={
 '427904':('research/p3-choice-recruitment-290/prts-events-427904.html','faa088b0474e75806b357df8648c6a59b1be6dcbc9be749db7c934ca9e6307e9'),
 '440271':('research/p3-choice-recruitment-290/prts-events-440271.html','e04971ad361436e5bb3721883423d98ad66636d5156794dd6221a977ffd6dac8'),
 'bw349818':('research/p3-choice-recruitment-290/bwiki-investigation.html','26b7768bf3556cf73c24529659c2c92f4095059476f782130bf3fa768422b908')}


class _Node:
    def __init__(self,tag,attrs,start):self.tag=tag;self.attrs=dict(attrs);self.start=start;self.end=None;self.children=[]


class _Document(HTMLParser):
    VOID={'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
    def __init__(self,source):
        super().__init__(convert_charrefs=True);self.source=source;self.nodes=[];self.offsets=[];offset=0
        for line in source.splitlines(keepends=True):self.offsets.append(offset);offset+=len(line)
        self.stack=[_Node('root',[],0)];self.feed(source);self.close()
    def _position(self):
        line,col=self.getpos();return self.offsets[line-1]+col
    def handle_starttag(self,tag,attrs):
        node=_Node(tag,attrs,self._position());self.nodes.append(node);self.stack[-1].children.append(node)
        if tag in self.VOID:node.end=node.start+len(self.get_starttag_text())
        else:self.stack.append(node)
    def handle_startendtag(self,tag,attrs):
        self.handle_starttag(tag,attrs)
        if tag not in self.VOID:self.handle_endtag(tag)
    def handle_endtag(self,tag):
        end=self.source.find('>',self._position())+1
        for i in range(len(self.stack)-1,0,-1):
            if self.stack[i].tag==tag:
                for node in self.stack[i:]:node.end=end
                del self.stack[i:];break
    def handle_data(self,value):self.stack[-1].children.append(value)


def _text(node):
    if isinstance(node,str):return node
    return ''.join(_text(c)+('\n' if isinstance(c,_Node) and c.tag in ('br','p','li') else '') for c in node.children).strip()
def _descendants(node):
    for child in node.children:
        if isinstance(child,_Node):yield child;yield from _descendants(child)
def _class(node,name):return isinstance(node,_Node) and name in node.attrs.get('class','').split()
def _part(node,name):
    rows=[n for n in _descendants(node) if _class(n,name)]
    if len(rows)>1:raise ValueError('Ambiguous exact DOM part: '+name)
    return _text(rows[0]) if rows else None
def _plain(value):return re.sub(r'<[@$][^<>]*>|</>','',unescape(value or '')).strip()
def _json(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
def _sha(raw):return hashlib.sha256(raw).hexdigest()
def _pin(raw):return {'sha256':_sha(raw),'bytes':len(raw)}
def _require(value,message):
    if not value:raise ValueError(message)


def build(source_root=ROOT):
    """Return new public artifact bytes; do not modify or import the application."""
    root=Path(source_root);catalog_raw=(root/CATALOG).read_bytes();game_raw=(root/GAME).read_bytes()
    _require(_sha(catalog_raw)==CATALOG_SHA,'Fixed current catalog changed.')
    _require(_sha(game_raw)==GAME_SHA,'Complete pinned original game table changed.')
    catalog=json.loads(catalog_raw);event=next(e for e in catalog['events'] if e['id']==EVENT)
    _require(event['title']=='线人' and len(event['scenes'])==4,'Exact event identity changed.')
    scene=event['scenes'][0];choice=scene['choices'][0]
    _require(scene['key']==SCENE and choice['key']==CHOICE and choice['game_choice_ids']==[],
             'Exact community choice or original-entry gap changed.')
    detail=json.loads(game_raw)['details']['rogue_6'];original=detail['choices']['choice_ro6_bomb1_1'];item=detail['items'][ITEM]
    _require([key for key,value in detail['items'].items() if value['name']=='沙盘α']==[ITEM],
             'The exact item name is not unique.')
    _require(item['type']=='RELIC' and item['iconId']==ITEM and original['displayData']['itemId'] is None,
             'Pinned item classification/icon or missing original pointer changed.')
    selected={'source':{'url':f'https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/{GAME_COMMIT}/zh_CN/gamedata/excel/roguelike_topic_table.json',
        **_pin(game_raw),'commit':GAME_COMMIT},'field_root':'$.details.rogue_6',
        'choice':deepcopy(original),'item':deepcopy(item),'relic':deepcopy(detail['relics'][ITEM]),
        'relic_parameters':deepcopy(detail['relicParams'][ITEM]),
        'choiceScenes':{key:deepcopy(value) for key,value in detail['choiceScenes'].items() if key.startswith('scene_ro6_bomb1_')},
        'scope':'Full selected source objects only; no native entry, quantity or current execution recovered.'}
    outputs={PACKET+'/original-records.json':_json(selected)};documents=[];bindings=[]
    for version,(relative,expected) in HTMLS.items():
        raw=(root/relative).read_bytes();_require(_sha(raw)==expected,'Pinned full HTML changed: '+relative)
        source=raw.decode('utf-8');document=_Document(source)
        if version.startswith('bw'):
            _require(re.findall(r'"wgRevisionId"\s*:\s*(\d+)',source)==['349818'],'BWiki revision changed.')
            headings=[n for n in document.nodes if n.tag in ('h2','h3')]
            matches=[i for i,n in enumerate(headings) if _text(n).replace('[编辑]','').strip()=='线人']
            _require(len(matches)==1,'BWiki event heading must be unique.');index=matches[0]
            start=headings[index].start;end=headings[index+1].start if index+1<len(headings) else len(source)
            tables=[n for n in document.nodes if n.tag=='table' and start<n.start<end];rows=[]
            for table in tables:
                for tr in _descendants(table):
                    if tr.tag=='tr':rows.append([_text(c) for c in tr.children if isinstance(c,_Node) and c.tag in ('td','th')])
            _require(rows[1][0]==scene['description']==selected['choiceScenes']['scene_ro6_bomb1_enter']['description'],
                     'Full entry prose differs.')
            _require(rows[2][-1]==original['title']+'\n'+_plain(original['description']),
                     'BWiki complete title/result does not corroborate the original full prose.')
            evidence={'full_table_rows':rows,'full_original_title_and_result_match':True}
            url='https://wiki.biligame.com/arknights/沉沦者的黑流树海/调查记录';revision='349818'
            packaged='bwiki-investigation.html'
        else:
            groups=[n for n in document.nodes if _class(n,'IS-event-data')]
            matches=[g for g in groups if any(_class(c,'scene') and c.attrs.get('data-name')=='线人' for c in g.children)]
            _require(len(matches)==1,'PRTS full event group must be unique.');group=matches[0]
            start,end=group.start,group.end
            scenes=[n for n in group.children if _class(n,'scene')]
            choices=[n for n in _descendants(group) if _class(n,'choose')]
            _require(len(scenes)==4 and len(choices)==3,'Full PRTS scene/choice scope changed.')
            _require(_part(scenes[0],'sceneText')==scene['description'],'Complete PRTS event prose differs.')
            notes=[_text(n) for n in _descendants(group) if _class(n,'edesc')]
            _require(notes==scene['edesc_texts'],'Event notes were changed or omitted.')
            first=choices[0];description=_part(first,'desc1');condition=_part(first,'desc2')
            _require(first.attrs==choice['attributes'] and first.attrs['data-iconid']==ITEM
                and description==choice['description'] and condition is None,'Full PRTS choice contents or explicit item identity differ.')
            _require(item['usage'] in description,'The item usage is not wholly corroborated by this choice.')
            evidence={'scene_attributes':scenes[0].attrs,'entry_prose':_part(scenes[0],'sceneText'),
                'event_notes':notes,'choice_attributes':first.attrs,'choice_description':description,'choice_condition':condition,
                'full_game_and_prts_descriptions_identical':False}
            url='https://m.prts.wiki/index.php?title=沉沦者的黑流树海/事件一览&oldid='+version
            revision=version;packaged='prts-events-'+version+'.html'
        excerpt=source[start:end].encode('utf-8');byte_start=len(source[:start].encode('utf-8'))
        _require(raw[byte_start:byte_start+len(excerpt)]==excerpt,'Selected HTML span differs from original bytes.')
        outputs[PACKET+'/'+packaged]=raw
        documents.append({'revision':revision,'url':url,'file':PACKET+'/'+packaged,**_pin(raw)})
        bindings.append({'revision':revision,'full_source_sha256':_sha(raw),'original_byte_start':byte_start,
            'original_byte_end':byte_start+len(excerpt),'span_sha256':_sha(excerpt),'evidence':evidence,
            'source_scene_link_verified':False})
    icon_raw=(root/ICON).read_bytes();blob=hashlib.sha1(b'blob '+str(len(icon_raw)).encode()+b'\0'+icon_raw).hexdigest()
    _require(_sha(icon_raw)==ICON_SHA and blob==ICON_BLOB,'Actual original icon bytes or Git blob changed.')
    icon={'file':ICON,'item_id':ITEM,'icon_id':ITEM,**_pin(icon_raw),'git_blob_sha1':blob,
        'url':'https://raw.githubusercontent.com/fexli/ArknightsResource/d0b5af0b004b044d322397ce5ae79632b6d9fcdd/rogueitem/'+ITEM+'.png',
        'resource_commit':'d0b5af0b004b044d322397ce5ae79632b6d9fcdd'}
    reference={'reference_id':CHOICE+':documented-item:'+ITEM,'event_id':EVENT,'scene_key':SCENE,
        'choice_key':CHOICE,'choice_title':choice['title'],'choice_description':choice['description'],
        'name':item['name'],'item_id':ITEM,'item_type':'RELIC','item_kind_name':'收藏品',
        'icon_reference':icon,'reference_kind':'documented_named_item',
        'quantity_reference':None,'actual_reward':None,'actual_selectable':None,'source_scene_link_verified':False,
        'original_choice_content_reference':'choice_ro6_bomb1_1','original_item_pointer_present':False,
        'original_choice_entry_bound':False,
        'scope_notice':'资料写明可获得该收藏品；数量、本局实际领取与可选状态未确认。'}
    data={'schema_version':1,'event_id':EVENT,'scope':'documented_named_item_not_grant',
        'expected_event':deepcopy(event),'reference':reference,'item':deepcopy(item),
        'sources':{'original_game':selected['source'],'documents':documents,'icon':icon},
        'source_reference':{'community_scene_key':SCENE,'community_choice_key':CHOICE,'dom_bindings':bindings,
            'primary_item_field':'$.details.rogue_6.items.'+ITEM,
            'original_choice_field':'$.details.rogue_6.choices.choice_ro6_bomb1_1',
            'content_corroboration_only':True,'source_scene_link_verified':False},
        'current_server_verified':False,'actual_reward':None,'actual_quantity':None,'actual_selectable':None,
        'source_scene_link_verified':False,'inventory_updated':False,
        'notice':'这是资料写明的物品，不是本局领取记录；数量、实际领取、可选状态与原入口仍未确认。',
        'unlock_notice':'物品条目的解锁说明不等于本事件的完整出现条件；本账号是否解锁仍未确认。'}
    outputs[DATA]=_json(data)
    outputs[PACKET+'/extraction.json']=_json({'source_bindings':bindings,'icon':icon,
        'native_source_scene_link_recovered':False,'quantity_inferred':False,
        'existing_typed_grant_channel_modified':False,'original_full_table_sha256':GAME_SHA})
    files={name:_pin(value) for name,value in outputs.items()}
    files[CATALOG]=_pin(catalog_raw);files[ICON]=_pin(icon_raw)
    manifest={'schema_version':1,'section':295,'files':files,
        'scope':'Fresh byte-bound documented item reading; no actual reward or source-scene script.'}
    outputs[PACKET+'/source-manifest.json']=_json(manifest)
    receipt={'status':'SOURCE_RECONSTRUCTION_ONLY','event_id':EVENT,'choice_key':CHOICE,
        'documented_item_count':1,'item_id':ITEM,'item_type':'RELIC','quantity_reference':None,
        'actual_reward':None,'source_scene_link_verified':False,'current_server_verified':False,
        'source_manifest_sha256':_sha(outputs[PACKET+'/source-manifest.json']),
        'output_files':{name:_pin(value) for name,value in outputs.items()},'network_requests':0,
        'game_chat_private_operations':0,'qt_or_tests_executed':False}
    return outputs,receipt


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--source-root',type=Path,default=ROOT)
    parser.add_argument('--output-dir',type=Path);args=parser.parse_args();outputs,receipt=build(args.source_root)
    if args.output_dir:
        destination=args.output_dir.resolve()
        _require(not destination.is_relative_to((args.source_root/'rouge/data').resolve()),'Output cannot enter runtime data.')
        destination.mkdir(parents=True,exist_ok=False)
        for name,raw in outputs.items():
            target=destination/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
        (destination/'source-build-receipt.json').write_bytes(_json(receipt))
    print(json.dumps(receipt,ensure_ascii=False))
