"""Licensed public aggregate/reference data. Fixed GETs; never accepts private uploads."""
from pathlib import Path
from datetime import datetime,timezone
from hashlib import sha256
from copy import deepcopy
import json,urllib.request,math
from .expansion_reference import _plain
SITE='https://www.lubiao.wiki'
URLS={'archive':SITE+'/data/archives/blackstream.json','events':SITE+'/data/foundation-floors-rogue_6.json'}
DEFAULT=Path(__file__).resolve().parents[1]/'research/public-reference-391/snapshot.json'

def normalize(archive,events,provenance):
    if archive.get('schemaVersion')!=2 or archive.get('archive',{}).get('topicId')!='rogue_6':raise ValueError('藏品资料包与主题不符。')
    if events.get('schemaVersion')!=1 or events.get('topicId')!='rogue_6':raise ValueError('事件资料包与主题不符。')
    items={}
    for row in archive['classifier']['items']:
        identity=row.get('itemId')
        if identity and identity not in items:items[identity]={'id':identity,'name':row['name'],'effect':row.get('rawEffect')or'','icon':(row.get('topicItem')or{}).get('iconId')}
    versions={'base':archive['pools']['pools'],**archive['pools'].get('dataVersions',{})};pools={}
    for version,rows in versions.items():
        pools[version]=[]
        for row in rows:
            for item in row.get('memberItems',[]):
                items.setdefault(item['itemId'],{'id':item['itemId'],'name':item['name'],'effect':item.get('usage')or'','icon':None})
            pools[version].append({key:deepcopy(row[key])for key in ('id','name','collectibles','description','poolKind','nodeBindings','usageChannels','sourceReferences','observedDistribution','frequencyColumns')if key in row})
    result={'schema':'rouge-public-archive-v1','provider':'路标档案馆','provenance':provenance,'retrieved_at':datetime.now(timezone.utc).isoformat(),'default_version':archive['pools'].get('defaultVersionId'),'versions':pools,'items':items,'events':deepcopy(events),'version_applicability':'来源未声明DLC2覆盖；不能视为当前版本完整资料。'}
    validate(result);return result

def validate(data):
    if data.get('schema')!='rouge-public-archive-v1':raise ValueError('不支持的公开资料格式。')
    if not isinstance(data.get('items'),dict)or not isinstance(data.get('versions'),dict):raise ValueError('资料目录缺失。')
    if len(data['items'])>5000:raise ValueError('物品数量异常。')
    for version,rows in data['versions'].items():
        if not isinstance(version,str)or not isinstance(rows,list)or len(rows)>1000:raise ValueError('资料范围异常。')
        seen=set()
        for row in rows:
            if not isinstance(row.get('id'),str)or row['id']in seen or not isinstance(row.get('name'),str):raise ValueError('藏品池标识无效或重复。')
            seen.add(row['id'])
            if not isinstance(row.get('collectibles'),list)or any(not isinstance(i,str)for i in row['collectibles']):raise ValueError('藏品池成员异常。')
    events=data.get('events',{})
    if events.get('topicId')!='rogue_6'or not isinstance(events.get('floors'),list)or not isinstance(events.get('specialLayers'),list):raise ValueError('事件层数资料缺失。')
    return data

def fetch():
    values={};proof={}
    for kind,url in URLS.items():
        request=urllib.request.Request(url,headers={'User-Agent':'rougezhushou-public-reader/1.0','Accept':'application/json'})
        with urllib.request.urlopen(request,timeout=20)as response:
            if response.geturl()!=url:raise ValueError('公开资料地址发生跳转，请重新核对。')
            raw=response.read(6000001)
        if len(raw)>6000000:raise ValueError('公开资料包过大。')
        values[kind]=json.loads(raw);proof[kind]={'url':url,'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
    return normalize(values['archive'],values['events'],proof)

def load(path=DEFAULT):return validate(json.loads(Path(path).read_text('utf8')))

def pool_rows(data,version,query=''):
    q=query.strip().casefold()
    return [r for r in data['versions'].get(version,[])if not q or q in(r['name']+' '+(r.get('description')or'')+' '+' '.join(data['items'].get(k,{}).get('name',k)+' '+data['items'].get(k,{}).get('effect','')for k in r['collectibles'])).casefold()]

def distributions(pool):
    # Separate overlapping observations; do not add counts or mix denominators.
    rows=[]
    if pool.get('observedDistribution'):rows.append(('summary','来源汇总',pool['observedDistribution']))
    for key,row in pool.get('frequencyColumns',{}).items():
        if row.get('status')=='observed'and row.get('observedDistribution'):rows.append((key,{'autobattle':'自动战斗样本','blackflow-archive-cumulative':'归档累计样本'}.get(key,key if any('\u4e00'<=c<='\u9fff'for c in key)else'其他来源样本 '+str(len(rows)+1)),row['observedDistribution']))
    return rows

def members(data,pool,distribution=None):
    observed={r.get('itemId'):r for r in(distribution or{}).get('members',[])}
    result=[]
    for identity in pool['collectibles']:
        item=data['items'].get(identity,{'name':'未命名物品','effect':''});row=observed.get(identity,{})
        n=row.get('occurrenceCount');total=row.get('totalOccurrenceCount',(distribution or{}).get('totalOccurrenceCount'));rate=None
        if (distribution or{}).get('interpretation')=='observedFrequencyOnly'and type(n)is int and type(total)is int and 0<=n<=total and total>0:
            reported=row.get('occurrenceRate',n/total)
            if isinstance(reported,(int,float))and math.isfinite(reported)and math.isclose(reported,n/total,rel_tol=1e-6,abs_tol=1e-6):rate=n/total
        result.append({'id':identity,'name':item['name'],'effect':_plain(item['effect']),'icon':item.get('icon'),'count':n,'total':total,'rate':rate})
    return result

def event_rows(data,floor,treehole=False,query='',node_type=None):
    if type(floor)is not int or not 1<=floor<=6:raise ValueError('层数超出公开资料范围。')
    packet=data['events'];result=[]
    if treehole:
        layer=next((r for r in packet['specialLayers']if r.get('id')=='rogue_6:treehole'),None)
        if not layer or floor not in layer.get('entranceFloors',[]):return []
        groups=layer.get('eventsByEntranceFloor',{}).get(str(floor),{});rows=[(r,'树洞：按进入层数查询；仍需满足具体事件条件')for rs in groups.values()for r in rs]
    else:
        layer=next((r for r in packet['floors']if r.get('floor')==floor),None)
        if not layer:return []
        rows=[(r,'本层资料候选，仍需满足具体出现条件')for rs in layer['eventsByNodeType'].values()for r in rs]
        rows += [(r,'仅在生成对应节点且满足事件条件时可能出现'if r.get('floorRule')=='nodeTypeAvailable'else'探索开始奖励，不是普通节点候选')for r in layer.get('conditionalEvents',[])]
    for row,condition in rows:
        if node_type and row.get('classification')!=node_type:continue
        if query.strip().casefold()not in(row['name']+' '+row['classification']).casefold():continue
        scenes=row.get('sceneIds',[]);identity=next((i for i in scenes if i.endswith('_enter')),scenes[0]if scenes else row['name'])
        result.append({**deepcopy(row),'id':identity,'condition':condition,'prerequisites':row.get('prerequisiteEventIds',[]),'actual_eligible':None})
    return result
