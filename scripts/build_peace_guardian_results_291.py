"""CACHE CANDIDATE: source-bind the single documented MOVE completion exception."""
import argparse
from copy import deepcopy
import hashlib
from html import unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
PACKET='research/p3-peace-guardian-results-291'
EVENT='community_group_019'
SCENE=EVENT+':scene:1'
CHOICE=SCENE+':choice:0'
PINNED={
    PACKET+'/prts-events-427904.html':'faa088b0474e75806b357df8648c6a59b1be6dcbc9be749db7c934ca9e6307e9',
    PACKET+'/prts-events-440271.html':'e04971ad361436e5bb3721883423d98ad66636d5156794dd6221a977ffd6dac8',
    PACKET+'/bwiki-investigation.html':'26b7768bf3556cf73c24529659c2c92f4095059476f782130bf3fa768422b908',
    PACKET+'/original-records.json':'c7baa3810b029676bb3e37cd60e5b810a62c35fa21c21edc18d5ee402e54441a',
    'rouge/data/node-catalog.json':'7df1d94bb69650eb19fc811af661e54d44bf07d72b1c0793de511adc1b2e915d'}


class _Node:
    def __init__(self,tag,attrs,order):
        self.tag,self.attrs,self.order,self.children=tag,dict(attrs),order,[]


class _Document(HTMLParser):
    VOID={'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
    def __init__(self,text):
        super().__init__(convert_charrefs=True)
        self.nodes=[]
        self.stack=[_Node('root',[],-1)]
        self.feed(text)
    def handle_starttag(self,tag,attrs):
        node=_Node(tag,attrs,len(self.nodes))
        self.nodes.append(node)
        self.stack[-1].children.append(node)
        if tag not in self.VOID:self.stack.append(node)
    def handle_startendtag(self,tag,attrs):
        self.handle_starttag(tag,attrs)
        if tag not in self.VOID:self.handle_endtag(tag)
    def handle_endtag(self,tag):
        for i in range(len(self.stack)-1,0,-1):
            if self.stack[i].tag==tag:
                del self.stack[i:]
                break
    def handle_data(self,data):self.stack[-1].children.append(data)


def _text(node):
    if isinstance(node,str):return node
    return ''.join(_text(c)+('\n' if isinstance(c,_Node) and c.tag in ('br','p','li') else '') for c in node.children)


def _descendants(node,tag):
    for child in node.children:
        if isinstance(child,_Node):
            if child.tag==tag:yield child
            yield from _descendants(child,tag)


def _has_class(node,name):return name in node.attrs.get('class','').split()


def _part(node,name,optional=False):
    found=[n for n in _descendants(node,'div') if _has_class(n,name)]
    if optional and not found:return None
    if len(found)!=1:raise ValueError('Exact DOM part missing or duplicated: '+name)
    return _text(found[0]).strip()


def _json(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')


def build(root=ROOT):
    """Only return bytes; sources and outputs stay under the candidate root."""
    root=Path(root)
    blobs={}
    for relative,digest in PINNED.items():
        raw=(root/relative).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=digest:raise ValueError('Pinned source changed: '+relative)
        blobs[relative]=raw
    catalog=json.loads(blobs['rouge/data/node-catalog.json'])
    event=next(e for e in catalog['events'] if e['id']==EVENT)
    scene=next(s for s in event['scenes'] if s['key']==SCENE)
    move,mark=scene['choices']
    exception='若已完成当前层的【“居民”据点】作战则不会移动'
    if (event['title']!='和平守卫者' or move['key']!=CHOICE or move['title']!='守卫和平！'
            or move['description']!='立即前往最近的“居民”据点' or move['conditional']!=exception
            or move['game_choice_ids']!=['choice_ro6_task1_3'] or mark['key']!=SCENE+':choice:1'
            or mark['title']!='从长计议' or mark['description']!='仅标记地图上最近的“居民”据点，暂不前往'
            or mark['conditional'] is not None or mark['game_choice_ids']!=['choice_ro6_task1_4']):
        raise ValueError('Complete target catalog MOVE/VISION content differs.')
    primary=json.loads(blobs[PACKET+'/original-records.json'])
    if primary['choiceScenes']['scene_ro6_task1_1']['description']!=scene['description']:
        raise ValueError('Original selected scene full prose differs.')
    original_move=primary['choices']['choice_ro6_task1_3']
    original_mark=primary['choices']['choice_ro6_task1_4']
    for expected,original,kind in ((move,original_move,'MOVE'),(mark,original_mark,'VISION')):
        description=re.sub(r'<[@$][^<>]*>|</>','',unescape(original['description'])).strip()
        if (original['title']!=expected['title'] or description!=expected['description']
                or original['type']!=kind or original['nextSceneId'] is not None):
            raise ValueError('Complete original choice base result differs.')
    if exception in json.dumps(primary['choices'],ensure_ascii=False):
        raise ValueError('Exception source scope changed; it was not in original choices.')
    dom={}
    for revision in ('427904','440271'):
        text=blobs[PACKET+'/prts-events-'+revision+'.html'].decode('utf-8')
        if re.findall(r'"wgRevisionId"\s*:\s*(\d+)',text)!=[revision]:
            raise ValueError('Archived PRTS revision differs.')
        document=_Document(text)
        scenes=[n for n in document.nodes if n.tag=='div' and n.attrs==scene['attributes']]
        if len(scenes)!=1 or _part(scenes[0],'sceneText')!=scene['description']:
            raise ValueError('Exact PRTS scene attributes/full prose differ.')
        choices=[n for n in _descendants(scenes[0],'div') if _has_class(n,'choose')]
        if len(choices)!=2:raise ValueError('Scene-local option count differs.')
        rows=[]
        for index,expected in enumerate((move,mark)):
            node=choices[index]
            if (node.attrs!=expected['attributes'] or _part(node,'desc1')!=expected['description']
                    or _part(node,'desc2',optional=True)!=expected['conditional']):
                raise ValueError('Exact PRTS scene-local option attributes or texts differ.')
            rows.append({'choice_key':expected['key'],'attributes':deepcopy(node.attrs),
                'desc1':_part(node,'desc1'),'desc2':_part(node,'desc2',optional=True)})
        dom[revision]={'scene_attributes':deepcopy(scenes[0].attrs),'scene_description':scene['description'],
                       'choices':rows,'source_sha256':PINNED[PACKET+'/prts-events-'+revision+'.html']}
    bw=blobs[PACKET+'/bwiki-investigation.html'].decode('utf-8')
    for key in ('wgRevisionId','wgCurRevisionId'):
        if re.findall(r'"'+key+r'"\s*:\s*(\d+)',bw)!=['349818']:raise ValueError('BWiki revision differs.')
    document=_Document(bw)
    headings=[n for n in document.nodes if n.tag in ('h2','h3')]
    indices=[i for i,n in enumerate(headings) if _text(n).replace('[编辑]','').strip()=='和平守卫者']
    if len(indices)!=1:raise ValueError('BWiki exact event section is not unique.')
    i=indices[0]
    end=headings[i+1].order if i+1<len(headings) else len(document.nodes)
    tables=[n for n in document.nodes if n.tag=='table' and headings[i].order<n.order<end]
    table_rows=[[_text(c).strip() for c in tr.children if isinstance(c,_Node) and c.tag in ('td','th')]
                for table in tables for tr in _descendants(table,'tr')]
    bw_bindings=[]
    for cid,original in (('choice_ro6_task1_3',original_move),('choice_ro6_task1_4',original_mark)):
        full=original['title']+' '+original['description']
        matches=[{'row_index':r,'cell_index':c,'cell_text':text} for r,cells in enumerate(table_rows)
                 for c,text in enumerate(cells) if ' '.join(text.split())==full]
        if len(matches)!=1:raise ValueError('Full BWiki base result is missing or not unique.')
        bw_bindings.append({'original_choice_id':cid,'match':matches[0]})
    if any(exception in cell for row in table_rows for cell in row):
        raise ValueError('BWiki exception scope changed; do not silently upgrade its evidence.')
    sources={'original_game':deepcopy(primary['source']),
        'bwiki':{'url':'https://wiki.biligame.com/arknights/沉沦者的黑流树海/调查记录','revision':'349818',
                 'sha256':PINNED[PACKET+'/bwiki-investigation.html'],'role':'two_base_results_only'},
        'prts_versions':{revision:{'revision':revision,'sha256':PINNED[PACKET+'/prts-events-'+revision+'.html'],
            'url':'https://m.prts.wiki/index.php?title=沉沦者的黑流树海/事件一览&oldid='+revision,
            'role':'same_community_family_documented_completion_exception'} for revision in ('427904','440271')}}
    data={'schema_version':1,'event_id':EVENT,'scene_key':SCENE,'choice_key':CHOICE,
        'expected_event':deepcopy(event),'expected_scene':deepcopy(scene),'expected_choice':deepcopy(move),
        'base_action_reference':{'action_kind':'move_to_nearest_resident_post','description':move['description'],
                                 'nearest_selection_algorithm_known':False},
        'completion_exception_reference':{'condition_text':exception,
            'predicate':'current_floor_resident_post_battle_completed','condition_matches':None,
            'documented_movement_if_condition_matches':False,'one_way_implication':True,
            'converse_verified':False,'negation_implies_successful_movement_verified':False,
            'documentation_revisions':['427904','440271'],
            'evidence_scope':'same-family community documentation; no original server-script verification'},
        'related_option_reference':{'choice_key':mark['key'],'original_choice_id':'choice_ro6_task1_4',
            'action_kind':'mark_nearest_resident_post','description':mark['description'],
            'original_record':deepcopy(original_mark),'move_exception_inherited':False},
        'original_record':deepcopy(original_move),'source':sources,
        'source_reference':{'prts_dom_bindings':dom,'bwiki_base_result_bindings':bw_bindings,
            'exception_in_bwiki':False,'exception_in_original_choices':False,
            'original_field_path':'$.details.rogue_6.choices.choice_ro6_task1_3',
            'source_scene_inferred_from_destination':False},
        'source_scene_link_verified':False,'complete_movement_result_known':False,
        'actual_current_floor_completion':None,'actual_target_node_id':None,'actual_moved':None}
    extraction={'schema_version':1,'event_id':EVENT,'scene_key':SCENE,'choice_key':CHOICE,
        'prts_dom_bindings':dom,'bwiki_base_result_bindings':bw_bindings,
        'completion_exception_source_family':'PRTS community only, two preserved revisions',
        'exception_in_bwiki':False,'exception_in_original_choices':False,
        'actual_or_inverse_implication_proven':False,'nearest_algorithm_proven':False,
        'original_source_scene_recovered':False}
    outputs={'rouge/data/peace-guardian-results.json':_json(data),PACKET+'/extraction.json':_json(extraction)}
    files={}
    for relative in [*PINNED,PACKET+'/README.md',PACKET+'/extract_original_records.py',
                     'scripts/build_peace_guardian_results_291.py',*outputs]:
        raw=outputs.get(relative)
        if raw is None:raw=(root/relative).read_bytes()
        files[relative]={'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
    outputs[PACKET+'/source-manifest.json']=_json({'schema_version':1,'files':files,
        'scope':'Cache candidate of a one-way documented exception, not actual state or route prediction.'})
    return outputs


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    outputs=build()
    for relative,raw in outputs.items():
        path=ROOT/relative
        if not path.resolve().is_relative_to(ROOT.resolve()):raise ValueError('Candidate output escaped root.')
        if args.check:
            if path.read_bytes()!=raw:raise ValueError('Stored candidate does not reproduce: '+relative)
        else:
            path.parent.mkdir(parents=True,exist_ok=True)
            with path.open('xb') as stream:stream.write(raw)
    print(json.dumps({'scope':'cache-only preparation, not product acceptance','checked_existing':args.check,
        'documented_move_exception_count':1,
        'manifest_sha256':hashlib.sha256(outputs[PACKET+'/source-manifest.json']).hexdigest()}))


if __name__=='__main__':main()
