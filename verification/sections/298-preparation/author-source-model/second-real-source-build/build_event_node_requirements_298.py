"""Bind five explicit node main-floor restrictions to six fixed event groups.

Only negative floor wording is a constraint. Two technology records are
documented enabling paths, never inverse/negative account-unlock gates.
"""
from copy import deepcopy
from hashlib import sha256
from html.parser import HTMLParser
import argparse
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PACKET='research/p3-event-node-requirements-298'
DATA='rouge/data/event-node-requirements.json'
CATALOG='rouge/data/node-catalog.json'
CATALOG_SHA='7df1d94bb69650eb19fc811af661e54d44bf07d72b1c0793de511adc1b2e915d'
GAME_SHA='f5867e55d09472253083486174aa47bd94dd48b07684b74b60a5b29ca00eda86'
COMMIT='a550f5e048bb94e7cdefc6eb97a4091f0c4c7add'
SOURCES={
    'main-433770.html':('research/p3-stage-context/community-main.html','366e0bf14b526816b20750f1d83b6c7b132d556dfc0b09a0ab3c302fd00610e9'),
    'events-427904.html':('research/p3-choice-recruitment-290/prts-events-427904.html','faa088b0474e75806b357df8648c6a59b1be6dcbc9be749db7c934ca9e6307e9'),
    'events-440271.html':('research/p3-choice-recruitment-290/prts-events-440271.html','e04971ad361436e5bb3721883423d98ad66636d5156794dd6221a977ffd6dac8')}
RULES=(
    ('安全的角落',(1,),('community_group_037',),'※该节点不会在第I层出现'),
    ('狭路相逢',(1,2,6),('community_group_028','community_group_029'),'※该节点不会在第I，II，VI层出现。'),
    ('失与得',(1,6),('community_group_025',),'※该节点不会在第I，VI层出现。'),
    ('误入奇境',(1,2,6),('community_group_027',),'※该节点不会在第I，II，VI层出现。'),
    ('先行一步',(1,5,6),('community_group_024',),'※该节点不会在第I，V，VI层出现。'))
TECH_IDS={'误入奇境':'rogue_6_outbuff_7','先行一步':'rogue_6_outbuff_9'}


class _Node:
    def __init__(self,tag,attrs,order):self.tag,self.attrs,self.order,self.children=tag,dict(attrs),order,[]


class _Document(HTMLParser):
    VOID={'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
    def __init__(self,text):
        super().__init__(convert_charrefs=True);self.nodes=[];self.stack=[_Node('root',[],-1)];self.feed(text)
    def handle_starttag(self,tag,attrs):
        node=_Node(tag,attrs,len(self.nodes));self.nodes.append(node);self.stack[-1].children.append(node)
        if tag not in self.VOID:self.stack.append(node)
    def handle_startendtag(self,tag,attrs):
        self.handle_starttag(tag,attrs)
        if tag not in self.VOID:self.handle_endtag(tag)
    def handle_endtag(self,tag):
        for index in range(len(self.stack)-1,0,-1):
            if self.stack[index].tag==tag:del self.stack[index:];break
    def handle_data(self,value):self.stack[-1].children.append(value)


def _text(node):
    if isinstance(node,str):return node
    return ''.join(_text(child)+('\n' if isinstance(child,_Node) and child.tag in ('br','p','li') else '') for child in node.children)
def _children(node):
    for child in node.children:
        if isinstance(child,_Node):yield child;yield from _children(child)
def _class(node,cls):return cls in node.attrs.get('class','').split()
def _tree(node):
    if isinstance(node,str):return node
    return {'tag':node.tag,'attributes':node.attrs,'children':[_tree(child) for child in node.children]}
def _json(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf8')
def _pin(raw):return {'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
def _read(root,path,digest):
    raw=(root/path).read_bytes()
    if sha256(raw).hexdigest()!=digest:raise ValueError('Source changed: '+path)
    return raw


def build(root=ROOT,*,original_topic):
    root=Path(root);raw_game=Path(original_topic).read_bytes()
    if sha256(raw_game).hexdigest()!=GAME_SHA:raise ValueError('Complete original topic table changed.')
    primary=json.loads(raw_game);detail=primary['details']['rogue_6']
    development=primary['customizeData']['rogue_6']['commonDevelopment']['developments']
    raw_catalog=_read(root,CATALOG,CATALOG_SHA);catalog=json.loads(raw_catalog)
    ids={identity for _,_,event_ids,_ in RULES for identity in event_ids}
    expected={e['id']:e for e in catalog['events'] if e['id'] in ids}
    if expected.keys()!=ids:raise ValueError('Incomplete exact event set.')
    files={};docs={}
    for name,(relative,digest) in SOURCES.items():
        raw=_read(root,relative,digest);files[PACKET+'/'+name]=raw;docs[name]=_Document(raw.decode('utf8'))
    groups=[];rows={};node_records={}
    for node_type,excluded,event_ids,wording in RULES:
        headers=[n for n in docs['main-433770.html'].nodes if n.tag=='ul' and _text(n).strip()=='事件 '+node_type]
        if len(headers)!=1:raise ValueError('Ambiguous exact node heading: '+node_type)
        header=headers[0]
        block=next(n for n in docs['main-433770.html'].nodes if n.order>header.order and n.tag=='dl')
        paragraphs=[_text(n).strip() for n in _children(block) if n.tag=='dd']
        if wording not in paragraphs:raise ValueError('Explicit negative floor wording changed.')
        type_records={key:value for key,value in detail['nodeTypeData'].items() if value['name']==node_type}
        if len(type_records)!=1:raise ValueError('Primary node identity is not unique.')
        node_records.update(type_records)
        binding={'node_type':node_type,'header_order':header.order,'header':_tree(header),
            'description_list_order':block.order,'complete_description_list':_tree(block),'paragraphs':paragraphs,
            'restriction_wording':wording,'documented_excluded_main_floors':list(excluded)}
        groups.append(binding)
        for identity in event_ids:
            event=expected[identity]
            if event['node_types']!=[node_type]:raise ValueError('Event node type identity changed.')
            event_dom=[]
            for revision in ('427904','440271'):
                doc=docs['events-'+revision+'.html'];matches=[]
                for group in (n for n in doc.nodes if _class(n,'IS-event-data')):
                    scenes=[n for n in _children(group) if _class(n,'scene')]
                    if scenes and scenes[0].attrs.get('data-index')==event['scenes'][0]['attributes']['data-index']:
                        matches.append((group,scenes))
                if len(matches)!=1:raise ValueError('Full event DOM identity is ambiguous.')
                group,scenes=matches[0]
                if (len(scenes)!=len(event['scenes']) or scenes[0].attrs.get('data-name')!=event['title']
                        or any(scene.attrs!=expected_scene['attributes'] for scene,expected_scene in zip(scenes,event['scenes']))):
                    raise ValueError('Complete event DOM attributes changed.')
                declared=scenes[0]
                if not declared.attrs.get('data-etype'):
                    earlier=[n for n in doc.nodes if n.order<scenes[0].order and _class(n,'scene') and n.attrs.get('data-etype')]
                    if not earlier:raise ValueError('No preceding declared node type.')
                    declared=earlier[-1]
                if declared.attrs['data-etype']!=node_type:raise ValueError('Declared or inherited DOM node type changed.')
                event_dom.append({'revision':revision,'group_order':group.order,'complete_group':_tree(group),
                    'scene_count':len(scenes),'node_type_binding':{
                        'kind':'direct_declared_type' if declared is scenes[0] else 'inherited_previous_declared_type',
                        'declaring_scene_order':declared.order,'declaring_scene_complete_attributes':declared.attrs,
                        'source_scene_entry_script_proven':False}})
            tech_id=TECH_IDS.get(node_type);tech=None
            if tech_id:
                original=development[tech_id]
                if original['rawDesc']!=['探险中会出现“'+node_type+'”节点']:raise ValueError('Technology identity changed.')
                tech={'development_id':tech_id,'name':original['buffName'],'rawDesc':original['rawDesc'],
                    'source_selector':'$.customizeData.rogue_6.commonDevelopment.developments.'+tech_id,
                    'role':'known_enabling_path_only','necessary_negative_gate_proven':False,
                    'inactive_hard_exclusion_supported':False,'actual_account_active':None}
            rows[identity]={'event_id':identity,'event_name':event['title'],'node_type':node_type,
                'node_type_original_id':next(iter(type_records)),
                'documented_excluded_main_floors':list(excluded),'source_text':wording,
                'main_document_group_reference':node_type,'technology_enabling_reference':tech,
                'event_dom_bindings':event_dom,
                'scope_notice':'仅文献记载的自然主层禁区；完整生成条件与实际服务器资格未知。'}
    original={'source':{'commit':COMMIT,'sha256':GAME_SHA,'bytes':len(raw_game),
        'url':'https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/'+COMMIT+'/zh_CN/gamedata/excel/roguelike_topic_table.json'},
        'nodeTypeData':node_records,'developments':{key:development[key] for key in TECH_IDS.values()}}
    packet={'schema':'event_node_requirements_v1','reference_kind':'documented_natural_main_floor_requirements',
        'expected_events':expected,'events':rows,'main_node_groups':groups,
        'source':{'original':original['source'],'main':{'revision':'433770','file':PACKET+'/main-433770.html',
            'url':'https://prts.wiki/index.php?title=沉沦者的黑流树海&oldid=433770'},
            'event_document_revisions':['427904','440271']},
        'current_server_verified':False,'actual_server_eligible':None,'inventory_updated':False,
        'original_entry_restored':False,'probability':None,
        'notice':'这里只核对文献明确列出的自然主层限制；允许层数不表示必然出现。观察内容、历史或特殊区域另行保留。',
        'limits':['科技条目是已知开启途径；不从未点亮反推事件绝不出现。',
                  '不把自然主层禁区应用于特殊区域、历史或已读具体内容。',
                  '不恢复服务器执行脚本、原来源场景、实际节点、概率或路线。']}
    files[PACKET+'/original-records.json']=_json(original)
    files[PACKET+'/node-dom-bindings.json']=_json({'groups':groups})
    files[DATA]=_json(packet)
    manifest={'schema':'event_node_requirements_source_manifest_v1','data_file':DATA,'data_sha256':sha256(files[DATA]).hexdigest(),
        'files':{path:_pin(raw) for path,raw in {**files,CATALOG:raw_catalog}.items()},
        'primary_complete_table_build_check':original['source'],'runtime_reads_primary_table':False}
    files[PACKET+'/source-manifest.json']=_json(manifest)
    return files


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--root',type=Path,default=ROOT)
    parser.add_argument('--original-topic',type=Path,required=True);parser.add_argument('--output-root',type=Path)
    args=parser.parse_args();files=build(args.root,original_topic=args.original_topic);dest=args.output_root or args.root
    for name,raw in files.items():
        path=dest/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
    print(json.dumps({'kind':'source-build-not-feature-acceptance','files':{path:_pin(raw) for path,raw in files.items()},
        'new_data_sha256':sha256(files[DATA]).hexdigest(),
        'new_manifest_sha256':sha256(files[PACKET+'/source-manifest.json']).hexdigest(),
        'full_primary_table_verified':True,'Qt_game_chat_private_Git_mutation':False},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
