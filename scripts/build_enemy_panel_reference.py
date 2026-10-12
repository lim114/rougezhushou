"""Build complete explicit enemy panel fields from the existing pinned originals."""
import argparse,hashlib,json
from pathlib import Path

ATTRIBUTE_FIELDS=('maxHp','atk','def','magicResistance','cost','blockCnt','moveSpeed',
    'attackSpeed','baseAttackTime','respawnTime','hpRecoveryPerSec','spRecoveryPerSec',
    'maxDeployCount','massLevel','baseForceLevel','tauntLevel','epDamageResistance',
    'epResistance','damageHitratePhysical','damageHitrateMagical','epBreakRecoverSpeed',
    'stunImmune','silenceImmune','sleepImmune','frozenImmune','levitateImmune',
    'disarmedCombatImmune','fearedImmune','palsyImmune','attractImmune','teleportImmune',
    'groundBoundImmune')
METADATA_FIELDS=('enemyTags','lifePointReduce','rangeRadius','viewRadius',
    'notCountInTotal','numOfExtraDrops')

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def explicit_fields(record):
    """Keep only explicit writes; undefined serialized placeholders are unused."""
    fields={}
    for group,names,values in (('attributes',ATTRIBUTE_FIELDS,record.get('attributes',{})),
        ('metadata',METADATA_FIELDS,record)):
        for name in names:
            raw=values.get(name)
            if raw is None:continue
            if not isinstance(raw,dict) or type(raw.get('m_defined')) is not bool or 'm_value' not in raw:
                raise ValueError('Unsupported defined-field encoding: '+name)
            if raw['m_defined']:fields[group+'.'+name]=raw['m_value']
    return fields

def build(root):
    root=Path(root)
    receipt=json.loads((root/'.cache/game-data/level-receipt.json').read_text(encoding='utf8'))
    previews=json.loads((root/'rouge/data/battle-previews.json').read_text(encoding='utf8'))
    db_path=root/'.cache/game-data/levels/enemydata/enemy_database.json'
    if digest(db_path)!=receipt['files']['enemydata/enemy_database.json']['sha256']:
        raise ValueError('Pinned enemy database hash changed')
    db={e['Key']:(i,e['Value']) for i,e in enumerate(json.loads(db_path.read_text(encoding='utf8'))['enemies'])}
    maxima={}
    for stage in previews['stages'].values():
        for e in stage['enemies']:maxima[e['id']]=max(maxima.get(e['id'],0),e['level'])
    definitions={}
    for eid,maximum in maxima.items():
        index,records=db.get(eid,(-1,[]))
        definitions[eid]={str(r['level']):{'source_selector':f'$.enemies[{index}].Value[{j}].enemyData',
            'fields':explicit_fields(r['enemyData'])} for j,r in enumerate(records) if r['level']<=maximum}
    bindings={};stage_sources={}
    for sid,stage in previews['stages'].items():
        source=stage['level_source'];url=source['url']
        name=url.split('/gamedata/levels/',1)[1]
        path=root/'.cache/game-data/levels'/name
        if digest(path)!=source['sha256']:raise ValueError('Pinned stage hash changed: '+sid)
        raw=json.loads(path.read_text(encoding='utf8'));refs=raw['enemyDbRefs'];rows={}
        for e in stage['enemies']:
            matches=[(i,r) for i,r in enumerate(refs) if r['id']==e['id'] and r['level']==e['level']]
            if len(matches)!=1:raise ValueError('Ambiguous stage reference')
            index,ref=matches[0]
            if type(ref.get('useDb')) is not bool:raise ValueError('Unsupported reference useDb mode')
            identity={}
            for key in ('name','description','prefabKey'):
                raw_value=(ref.get('overwrittenData') or {}).get(key)
                if raw_value is not None:
                    if not isinstance(raw_value,dict) or type(raw_value.get('m_defined')) is not bool or 'm_value' not in raw_value:
                        raise ValueError('Unsupported defined identity field: '+key)
                    if raw_value['m_defined']:identity[key]=raw_value['m_value']
            rows[e['id']+'@'+str(e['level'])]={'source_index':index,
                'use_db':ref['useDb'],'reference_id':ref['id'],
                'overwritten_data_present':ref.get('overwrittenData') is not None,
                'identity_overrides':identity,'overrides':explicit_fields(ref.get('overwrittenData') or {})}
        bindings[sid]=rows;stage_sources[sid]=source
    return {'schema_version':2,'scope':'source_bound_fixed_enemy_constructor_fields',
        'source':{'game_commit':receipt['commit'],
            'enemy_database':receipt['files']['enemydata/enemy_database.json'],
            'stages':stage_sources},
        'attribute_fields':list(ATTRIBUTE_FIELDS),'metadata_fields':list(METADATA_FIELDS),
        'definitions':definitions,'bindings':bindings,
        'encoding':'Only m_defined=true writes are projected; absent or false writes leave the previous explicit source field or unknown. Skills, talents and spData are excluded.'}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args();data=build(args.root)
    args.output.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps({'stages':len(data['bindings']),'references':sum(map(len,data['bindings'].values())),
        'attributes':len(data['attribute_fields']),'metadata':len(data['metadata_fields'])}))
