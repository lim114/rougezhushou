"""Complete pinned stage directory, not an eligible generation pool."""
from pathlib import Path,PurePosixPath
from hashlib import sha256
from copy import deepcopy
import json
from . import expansion_reference as version
ROOT=Path(__file__).resolve().parents[1];PACK='research/p3-current-stage-directory-317';DATA='rouge/data/current-stage-directory.json';MANIFEST=PACK+'/runtime-manifest.json';MANIFEST_SHA256='bc1203a00ba98a270c2df42c125c57609357e5d8a65b00b36b469a904866f2a6'
FLOORS=[(None,'全部层数')]+[('floor'+str(n),'第'+str(n)+'层')for n in range(1,7)]+[('unknown','层数未确认')]
KINDS=[(None,'全部作战来源'),('normal','普通作战'),('emergency','紧急作战'),('boss','险路恶敌'),('pursuit','追猎'),('duck','鸭爵与雇员'),('duel','狭路相逢'),('challenge','特殊挑战'),('resident','流窜居民与据点'),('shop','坎诺特的挑战'),('unknown','来源分类未确认')]
NOTICE='按固定资料中的层数和来源查找作战。目录保留所有同名配置，不表示这些配置都会在本局出现；未知层数不会被强行归类。'

def packet():
    try:
        raw=(ROOT/MANIFEST).read_bytes()
        if sha256(raw).hexdigest()!=MANIFEST_SHA256:return None
        manifest=json.loads(raw);values={}
        if manifest['schema']!='current_stage_directory_317_manifest_v1'or manifest['game_commit']!=version.NEW_COMMIT:return None
        for name,pin in manifest['files'].items():
            relative=PurePosixPath(name)
            if relative.is_absolute()or'..'in relative.parts or'\\'in name or':'in name:return None
            p=ROOT.joinpath(*relative.parts)
            if p.is_symlink()or not p.resolve().is_relative_to(ROOT.resolve()):return None
            raw=p.read_bytes()
            if len(raw)!=pin['bytes']or sha256(raw).hexdigest()!=pin['sha256']:return None
            values[name]=raw
        data=json.loads(values[DATA]);current=version.packet()
        if current is None:return None
        stages=current['current']['details']['stages']
        if set(stages)!=set(data['rows']):return None
        for sid,r in data['rows'].items():
            if r['original_stage']!=stages[sid]:return None
        return {'data':data,'source_identity':MANIFEST_SHA256,'actual_generation_pool':None,'actual_server_verified':False}
    except(OSError,ValueError,KeyError,TypeError,UnicodeError):return None

def rows(floor=None,kind=None,*,reference=None):
    if floor not in dict(FLOORS)or kind not in dict(KINDS):raise ValueError('分类尚未支持。')
    ref=packet()if reference is None else reference
    if ref is None:return None
    return [deepcopy(r)for r in ref['data']['rows'].values()if(floor is None or r['floor']==floor)and(kind is None or r['play_kind']==kind)]

def detail(stage_id,*,reference=None):
    ref=packet()if reference is None else reference
    if ref is None:return None
    row=ref['data']['rows'].get(stage_id)
    if row is None:return None
    variants=[r['id']for r in ref['data']['rows'].values()if r['name']==row['name']and r['code']==row['code']and r['play_kind']==row['play_kind']]
    return {'row':deepcopy(row),'source_identity':ref['source_identity'],'variant_index':variants.index(stage_id)+1,'variant_count':len(variants),'actual_eligible':None,'actual_floor_verified':False}

def label(info):
    row=info['row'];return row['name']+' · '+dict(KINDS)[row['play_kind']]+' · 资料'+str(info['variant_index'])

def player_text(info):
    row=info['row'];lines=['【层数与来源】',dict(FLOORS)[row['floor']]+' · '+row['region'],dict(KINDS)[row['play_kind']],f"同名同类资料{info['variant_index']} / {info['variant_count']}；每份配置单独保留。",NOTICE]
    if row['floor']=='unknown':lines+=['来源只说明特殊入口类别，没有明确层数；不能因为属于特殊挑战就推定任意层都能遇到。']
    if row['kind']=='pursuit':lines+=['追猎属于节点外事件，不能据此当作地图上的普通作战节点。']
    if row['floor']=='floor6':lines+=['两个第六层区域分别标明，不按区域编号或关卡编号猜层数。']
    lines+=['目录分组只用于查资料，不证明自然生成范围、强化版本选择、事件前置或本局可进入。','']
    return '\n'.join(lines)
