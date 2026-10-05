"""Build offline previews from pinned levels and verified map originals."""
import hashlib,json,re,sys,urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from rouge.catalog import catalog,stage_previews

ATTRS=('maxHp','atk','def','magicResistance','attackSpeed','baseAttackTime',
       'moveSpeed','massLevel','hpRecoveryPerSec','epDamageResistance','epResistance')
IMMUNITIES=('stunImmune','silenceImmune','sleepImmune','frozenImmune','levitateImmune',
            'disarmedCombatImmune','fearedImmune','palsyImmune','attractImmune',
            'teleportImmune','groundBoundImmune')

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def clean(value):return re.sub(r'<[^>]*>','',value or '').replace('\\n','\n')

def apply_defined(target,source):
    if not isinstance(source,dict):return
    for key,value in source.items():
        if isinstance(value,dict) and 'm_defined' in value:
            if value['m_defined']:target[key]=value['m_value']
        elif isinstance(value,dict):apply_defined(target.setdefault(key,{}),value)

def resolve(db,ref):
    versions=sorted(db.get(ref['id'],[]),key=lambda x:x['level'])
    initial=next((v for v in versions if v['level']==0),{}).get('enemyData',{}).get('levelType',{})
    result={'levelType':'NORMAL'} if not initial.get('m_defined') and initial.get('m_value')=='NORMAL' else {}
    for version in versions:
        if version['level']<=ref['level']:apply_defined(result,version['enemyData'])
    apply_defined(result,ref.get('overwrittenData'))
    return result

def main():
    folder=ROOT/'.cache/research/battle-039'
    source=json.loads((ROOT/'.cache/game-data/level-receipt.json').read_text(encoding='utf-8'))
    images=json.loads((folder/'image-receipt.json').read_text(encoding='utf-8'))
    handbook_path=folder/'enemy_handbook_table.json'
    url='https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/'+source['commit']+'/zh_CN/gamedata/excel/enemy_handbook_table.json'
    if not handbook_path.exists():
        req=urllib.request.Request(url,headers={'User-Agent':'rouge-research'})
        with urllib.request.urlopen(req,timeout=30) as response:handbook_path.write_bytes(response.read())
    handbook=json.loads(handbook_path.read_text(encoding='utf-8'))['enemyData']
    dbpath=ROOT/'.cache/game-data/levels/enemydata/enemy_database.json'
    assert digest(dbpath)==source['files']['enemydata/enemy_database.json']['sha256']
    db={x['Key']:x['Value'] for x in json.loads(dbpath.read_text(encoding='utf-8'))['enemies']}
    stages={};enemy_count=spawn_count=branch_count=0
    for sid,record in catalog()['stages'].items():
        if sid not in stage_previews():continue
        name=record['levelId'].lower()+'.json';path=ROOT/'.cache/game-data/levels'/name
        assert digest(path)==source['files'][name]['sha256'],name
        image=images['images'][sid]
        assert digest(ROOT/'rouge/data'/image['file'])==image['sha256'],sid
        level=json.loads(path.read_text(encoding='utf-8'));enemies=[]
        for ref in level['enemyDbRefs']:
            resolved=resolve(db,ref);attrs=resolved.get('attributes',{});entry=handbook.get(ref['id'],{})
            existing=[e for e in stage_previews()[sid]['possible_enemies'] if e['id']==ref['id'] and e['level']==ref['level']]
            assert len(existing)==1,(sid,ref)
            assert {k:attrs.get(k) for k in existing[0]['reference_stats']}==existing[0]['reference_stats'],(sid,ref)
            enemies.append({**existing[0],
                'reference_stats':{k:attrs.get(k) for k in ATTRS},
                'immunity_reference':{k:attrs.get(k) for k in IMMUNITIES},
                'attack_way':resolved.get('applyWay'),'motion':resolved.get('motion'),
                'damage_types':entry.get('damageType') or [],
                'handbook_description':clean(entry.get('description')),
                'abilities':[clean(x.get('text')) for x in entry.get('abilityList') or [] if x.get('text')],
                'handbook_present':bool(entry)})
        branches=[]
        for key,branch in (level.get('branches') or {}).items():
            for pi,phase in enumerate(branch.get('phases') or []):
                for ai,action in enumerate(phase.get('actions') or []):
                    if action['actionType']=='SPAWN':
                        branches.append({'id':f'branch:{key}.p{pi+1}.a{ai+1}',
                            'branch':key,'phase':pi+1,'phase_pre_delay':phase.get('preDelay'),
                            'action':action,'route_scope_verified':False})
        waves=[]
        for wi,wave in enumerate(level.get('waves') or []):
            fragments=[]
            for fi,fragment in enumerate(wave.get('fragments') or []):
                fragments.append({'index':fi+1,'pre_delay':fragment.get('preDelay'),
                    'actions':[{'id':f'w{wi+1}.f{fi+1}.a{ai+1}','action':a}
                        for ai,a in enumerate(fragment.get('actions') or [])]})
            waves.append({'index':wi+1,'pre_delay':wave.get('preDelay'),'post_delay':wave.get('postDelay'),
                'max_time_waiting_for_next_wave':wave.get('maxTimeWaitingForNextWave'),
                'advanced_wave_tag':wave.get('advancedWaveTag'),'fragments':fragments})
        stages[sid]={'id':sid,'name':record['name'],'difficulty':record['difficulty'],
            'level_source':source['files'][name],'image':image,'map':level['mapData']['map'],
            'tiles':level['mapData']['tiles'],'routes':level.get('routes') or [],
            'waves':waves,'branch_spawns':branches,'enemies':enemies,
            'runes':level.get('runes') or [],'global_buffs':level.get('globalBuffs') or [],
            'predefined_objects':(level.get('predefines') or {}).get('tokenInsts') or [],
            'initial_enemy_records':level.get('enemies') or []}
        enemy_count+=len(enemies);branch_count+=len(branches)
        spawn_count+=sum(a['action']['actionType']=='SPAWN' for w in waves for f in w['fragments'] for a in f['actions'])
    result={'version':1,'source':{'game_commit':source['commit'],'resource_commit':images['resource_commit'],
        'enemy_database':source['files']['enemydata/enemy_database.json'],
        'handbook':{'url':url,'sha256':digest(handbook_path)},'image_readme':images['source_readme'],
        'copyright':images['copyright']},
        'coordinate_rule':'display_row = rows - 1 - source_row; display_col = source_col',
        'limits':['原图与关卡数据分别固定版本；同ID绑定不等于跨版本几何一致，原图不承载坐标投影。',
            '只映射主波次的基础routes；分支路由作用域未核验，分支出怪位置保持未知。',
            '波/片段/条目延迟及间隔是原始调度参数；绝对时间与阻塞、隐藏脚本未核验。',
            '列表包含随机候选及隐藏组，不合计为实际敌人数量，不将原始权重当概率。',
            '路线显示起终点和空间检查点，非实际寻路或移动到达时间。',
            '敌人机制是图鉴/关卡参考，不覆盖所有阶段脚本；缺失免疫定义不是免疫=false。'],
        'stages':stages}
    destination=ROOT/'rouge/data/battle-previews.json'
    destination.write_text(json.dumps(result,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    receipt={'version':'0.39.0','stages':len(stages),'enemy_references':enemy_count,
        'main_spawn_rows':spawn_count,'conditional_branch_spawn_rows':branch_count,
        'data_sha256':digest(destination),'source':result['source'],
        'image_count':len(images['images']),'image_bytes':sum(i['bytes'] for i in images['images'].values()),
        'coordinate_evidence':{'stage_id':'ro6_n_1_2','enemy_id':'enemy_1093_ccsbr',
            'source_start':{'row':5,'col':8},'display_start':{'row':1,'col':8},
            'display_start_tile':'tile_start','source_end':{'row':3,'col':0},
            'display_end':{'row':3,'col':0},'display_end_tile':'tile_end'},
        'limits':result['limits']}
    (folder/'data-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:receipt[k] for k in ('stages','enemy_references','main_spawn_rows','conditional_branch_spawn_rows','image_count')}),flush=True)

if __name__=='__main__':main()
