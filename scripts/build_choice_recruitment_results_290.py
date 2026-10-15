"""Bind one fixed choice annotation to four complete documented result variants."""
import argparse
from copy import deepcopy
import hashlib
from html import unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PACKET = 'research/p3-choice-recruitment-290'
EVENT = 'community_group_018'
SCENE = EVENT+':scene:0'
CHOICE = SCENE+':choice:1'
PAIRS = [('先锋','近卫'),('重装','辅助'),('医疗','狙击'),('术师','特种')]
ORIGINAL_IDS = ['choice_ro6_hire1_1','choice_ro6_hire1_4','choice_ro6_hire1_5','choice_ro6_hire1_6']
PINNED = {
    PACKET+'/bwiki-investigation.html':'26b7768bf3556cf73c24529659c2c92f4095059476f782130bf3fa768422b908',
    PACKET+'/prts-events-427904.html':'faa088b0474e75806b357df8648c6a59b1be6dcbc9be749db7c934ca9e6307e9',
    PACKET+'/prts-events-440271.html':'e04971ad361436e5bb3721883423d98ad66636d5156794dd6221a977ffd6dac8',
    PACKET+'/original-records.json':'89db8c766c68daf7f1aa14e9755b5d46cb873f70f6f5637833962dd71b65502f',
    'rouge/data/node-catalog.json':'7df1d94bb69650eb19fc811af661e54d44bf07d72b1c0793de511adc1b2e915d',
}


class _Node:
    def __init__(self, tag, attrs, order):
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

    def handle_data(self,data):
        self.stack[-1].children.append(data)


def _text(node):
    if isinstance(node,str):return node
    return ''.join(_text(c)+('\n' if isinstance(c,_Node) and c.tag in ('br','p','li') else '') for c in node.children)


def _descendants(node,tag):
    for child in node.children:
        if isinstance(child,_Node):
            if child.tag==tag:yield child
            yield from _descendants(child,tag)


def _class(node,name):
    return name in node.attrs.get('class','').split()


def _single_descendant_text(node,name):
    found=[n for n in _descendants(node,'div') if _class(n,name)]
    if len(found)!=1:raise ValueError('Expected one exact DOM part: '+name)
    return _text(found[0]).strip()


def _json(value):
    return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')


def _plain_game(value):
    return re.sub(r'<[@$][^<>]*>|</>','',unescape(value)).strip()


def build(root=ROOT):
    """Return reproducible bytes, without writing files or using network/state."""
    root=Path(root)
    blobs={}
    for relative,sha in PINNED.items():
        raw=(root/relative).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=sha:raise ValueError('Pinned source differs: '+relative)
        blobs[relative]=raw
    catalog=json.loads(blobs['rouge/data/node-catalog.json'])
    event=next(e for e in catalog['events'] if e['id']==EVENT)
    scene=next(s for s in event['scenes'] if s['key']==SCENE)
    choice=next(c for c in scene['choices'] if c['key']==CHOICE)
    expected_annotation='可出现的职业搭配固定为：'+' / '.join('或'.join(pair) for pair in PAIRS)
    if (event['title']!='临时中介所' or choice['title']!='可靠的中介值得信任'
            or choice['description']!='获得2希望，招募1名直升的5星及以下??或??干员'
            or choice['conditional']!=expected_annotation or choice['game_choice_ids']!=[]
            or choice['presentation_role']!='display_option_reference'):
        raise ValueError('Complete target catalog annotation differs.')
    dom_bindings={}
    for revision in ('427904','440271'):
        html=blobs[PACKET+'/prts-events-'+revision+'.html'].decode('utf-8')
        if re.findall(r'"wgRevisionId"\s*:\s*(\d+)',html)!=[revision]:
            raise ValueError('Original PRTS revision differs.')
        document=_Document(html)
        scenes=[n for n in document.nodes if n.tag=='div' and n.attrs==scene['attributes']]
        if len(scenes)!=1:raise ValueError('Full scene DOM attributes must identify one scene.')
        current=scenes[0]
        if _single_descendant_text(current,'sceneText')!=scene['description']:
            raise ValueError('Full community scene prose differs.')
        choices=[n for n in _descendants(current,'div') if _class(n,'choose')]
        matches=[n for n in choices if n.attrs==choice['attributes']]
        if len(matches)!=1 or choices.index(matches[0])!=1:
            raise ValueError('Target DOM choice is not its exact scene-local position and attributes.')
        desc1=_single_descendant_text(matches[0],'desc1')
        desc2=_single_descendant_text(matches[0],'desc2')
        if desc1!=choice['description'] or desc2!=choice['conditional']:
            raise ValueError('Full target result or annotation differs.')
        dom_bindings[revision]={'scene_attributes':deepcopy(current.attrs),
            'scene_description':scene['description'],'choice_attributes':deepcopy(matches[0].attrs),
            'scene_local_choice_index':1,'desc1':desc1,'desc2':desc2,
            'source_sha256':PINNED[PACKET+'/prts-events-'+revision+'.html']}
    bw=blobs[PACKET+'/bwiki-investigation.html'].decode('utf-8')
    for key in ('wgRevisionId','wgCurRevisionId'):
        if re.findall(r'"'+key+r'"\s*:\s*(\d+)',bw)!=['349818']:
            raise ValueError('BWiki revision differs.')
    document=_Document(bw)
    headings=[n for n in document.nodes if n.tag in ('h2','h3')]
    positions=[i for i,n in enumerate(headings) if _text(n).replace('[编辑]','').strip()=='临时中介所']
    if len(positions)!=1:raise ValueError('BWiki event section must be unique.')
    i=positions[0]
    end=headings[i+1].order if i+1<len(headings) else len(document.nodes)
    tables=[n for n in document.nodes if n.tag=='table' and headings[i].order<n.order<end]
    rows=[[_text(c).strip() for c in tr.children if isinstance(c,_Node) and c.tag in ('td','th')]
          for table in tables for tr in _descendants(table,'tr')]
    primary=json.loads(blobs[PACKET+'/original-records.json'])
    variants=[]
    for original_id,pair in zip(ORIGINAL_IDS,PAIRS):
        original=primary['choices'][original_id]
        clean=_plain_game(original['description'])
        expected='获得2希望，招募1名直升的5星及以下'+'或'.join(pair)+'干员'
        if (original['id']!=original_id or original['title']!=choice['title'] or clean!=expected
                or original['type']!='TRADE' or original['isHiddenChoice'] is not False
                or original['displayData']['funcIconId']!='recruit'):
            raise ValueError('Complete original recruitment variant differs.')
        matches=[{'row_index':r,'cell_index':c,'cell_text':text}
            for r,cells in enumerate(rows) for c,text in enumerate(cells)
            if ' '.join(text.split())==original['title']+' '+clean]
        if len(matches)!=1:raise ValueError('Full BWiki title/result must uniquely match each original choice.')
        variants.append({'original_choice_id':original_id,'profession_pair':list(pair),
            'hope_gain_reference':2,'recruit_count_reference':1,'rarity_ceiling_reference':5,
            'upgrade_reference_text':'直升','description':clean,'original_record':deepcopy(original),
            'source_reference':{'bwiki_revision':'349818','bwiki_section':'临时中介所',
                'bwiki_full_text_match':matches[0],
                'original_field_path':'$.details.rogue_6.choices.'+original_id,
                'original_sha256':primary['source']['sha256'],
                'source_scene_inferred_from_destination':False},
            'recruitment_cost':None,'actual_granted':None,'actual_operator':None,'actual_cultivation':None,
            'original_entry_scene_verified':False})
    source={'original_game':deepcopy(primary['source']),
        'bwiki':{'url':'https://wiki.biligame.com/arknights/沉沦者的黑流树海/调查记录','revision':'349818',
                 'sha256':PINNED[PACKET+'/bwiki-investigation.html'],'visible_content_date':'2026-07-27'},
        'prts_versions':{revision:{'revision':revision,'sha256':PINNED[PACKET+'/prts-events-'+revision+'.html'],
             'url':'https://m.prts.wiki/index.php?title=沉沦者的黑流树海/事件一览&oldid='+revision}
             for revision in ('427904','440271')},
        'fixed_catalog':deepcopy(catalog['sources']['cached_community_catalog'])}
    source_reference={'event_id':EVENT,'scene_key':SCENE,'choice_key':CHOICE,
        'prts_dom_bindings':dom_bindings,'comparison':'Complete strings; BWiki cell line-break/whitespace only is normalized, original game rich-text tags only are removed.',
        'entry_prose_difference_retained':{'original':primary['choiceScenes']['scene_ro6_hire1_enter']['description'],
                                         'community':scene['description'],
                                         'source_scene_edge_proven':False}}
    data={'schema_version':1,'event_id':EVENT,'scene_key':SCENE,'choice_key':CHOICE,
        'expected_event':deepcopy(event),'expected_scene':deepcopy(scene),'expected_choice':deepcopy(choice),
        'annotation_text':choice['conditional'],'variants':variants,'source':source,
        'source_reference':source_reference,'original_entry_scene_verified':False,
        'full_recruitment_pool_known':False,'actual_result_variant':None}
    extraction={'schema_version':1,'event_id':EVENT,'scene_key':SCENE,'choice_key':CHOICE,
        'prts_dom_bindings':dom_bindings,'bwiki_variant_matches':[v['source_reference'] for v in variants],
        'original_choices':[v['original_choice_id'] for v in variants],
        'original_entry_gap_reduction_claimed':False,'actual_recruitment_or_cost_proven':False,
        'entry_prose_difference_retained':source_reference['entry_prose_difference_retained']}
    outputs={'rouge/data/choice-recruitment-results.json':_json(data),PACKET+'/extraction.json':_json(extraction)}
    files={}
    for relative in [*PINNED,PACKET+'/README.md',PACKET+'/extract_original_records.py',
                     'scripts/build_choice_recruitment_results_290.py',*outputs]:
        raw=outputs.get(relative)
        if raw is None:raw=(root/relative).read_bytes()
        files[relative]={'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
    outputs[PACKET+'/source-manifest.json']=_json({'schema_version':1,'files':files,
        'scope':'One fixed choice result annotation, not an appearance condition, source-scene edge or actual recruitment.'})
    return outputs


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    outputs=build()
    for relative,raw in outputs.items():
        path=ROOT/relative
        if args.check:
            if path.read_bytes()!=raw:raise ValueError('Stored output does not reproduce: '+relative)
        else:
            path.parent.mkdir(parents=True,exist_ok=True)
            with path.open('xb') as stream:stream.write(raw)
    print(json.dumps({'checked_existing':args.check,'result_variants':4,
        'manifest_sha256':hashlib.sha256(outputs[PACKET+'/source-manifest.json']).hexdigest(),
        'original_entry_scene_verified':False}))


if __name__=='__main__':main()
