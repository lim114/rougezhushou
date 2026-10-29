"""Version-scoped public descriptions, joined only by exact name AND icon."""
from pathlib import Path
from hashlib import sha256
from copy import deepcopy
import json
from . import expansion_reference as reference

SUPPLEMENT = Path(__file__).resolve().parents[1]/'research/public-compendium-413/dlc1.json'
# The archived source is licensed for local reading, caching and redistribution.
ARCHIVE_SHA = 'ba789272b3d7368ba1ede2ba9d4e77eb3d9ea0955a72cd4a136289ff0def489b'
SUPPLEMENT_SHA = '7b2a1409a9854931e02245145c0165882f79c9a54cdc2c83c3ee2a08687a5c1e'  # Pinned when the extracted public source is installed.


def validate(catalogs):
    if not isinstance(catalogs,dict) or len(catalogs)>20:raise ValueError('图鉴范围异常。')
    for version,pack in catalogs.items():
        if not isinstance(version,str) or not isinstance(pack,dict):raise ValueError('图鉴范围无效。')
        rows=pack.get('items');seen=set()
        if not isinstance(rows,list) or len(rows)>1000 or type(pack.get('count'))is not int or pack['count']!=len(rows):raise ValueError('图鉴条目数量不符。')
        for row in rows:
            if not isinstance(row,dict) or any(not isinstance(row.get(k),str) or not row[k] for k in ('name','iconId')):raise ValueError('图鉴身份不完整。')
            key=(row['name'],row['iconId'])
            if key in seen:raise ValueError('图鉴身份重复。')
            seen.add(key)
            for key in ('effect','description','category','unlockConditionText','obtainMethod'):
                if key in row and not isinstance(row[key],str):raise ValueError('图鉴文字无效。')
    return catalogs


def complete(data):
    """Read-only upgrade of the EXACT historic raw source; never borrow across caches."""
    if 'versioned_collectibles' in data:
        validate(data['versioned_collectibles']);return data
    if data.get('provenance',{}).get('archive',{}).get('sha256')!=ARCHIVE_SHA:return data
    try:
        raw=SUPPLEMENT.read_bytes()
        if sha256(raw).hexdigest()!=SUPPLEMENT_SHA:return data
        pack=json.loads(raw)
        if pack['archive']['sha256']!=ARCHIVE_SHA:return data
        catalogs=validate(pack['versioned_collectibles'])
    except (OSError,ValueError,KeyError,TypeError,AttributeError):return data
    return {**data,'versioned_collectibles':catalogs}


def resolve(data,version,packet=None):
    """Unmatched descriptions remain unbound, never name-only or icon-only guesses."""
    pack=complete(data).get('versioned_collectibles',{}).get(version,{})
    rows=pack.get('items',[])
    if not rows:return {}
    packet=reference.packet() if packet is None else packet
    if packet is None:return {}
    matches={}
    for identity,item in packet['current']['details']['items'].items():
        matches.setdefault((item.get('name'),item.get('iconId')),[]).append(identity)
    result={}
    for row in rows:
        candidates=matches.get((row['name'],row['iconId']),[])
        if len(candidates)==1:result[candidates[0]]=deepcopy(row)
    return result


def item(data,identity,resolved):
    doc=resolved.get(identity)
    if doc is None:return data['items'].get(identity,{'name':'未命名物品','effect':''})
    return {'id':identity,'name':doc['name'],'icon':doc['iconId'],'effect':doc.get('effect','')}


def effect_text(value):
    # Preserve every value and condition; each named grade gets its own line.
    return reference._plain(value).replace('；【','；\n【')
