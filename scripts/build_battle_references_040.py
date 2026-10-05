"""Attach pinned level movement fields and cited local scheduling semantics."""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from rouge.catalog import catalog

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    folder=ROOT/'.cache/research/battle-040'
    before=ROOT/'.cache/batch-040-before/rouge/data/battle-previews.json'
    data=json.loads(before.read_text(encoding='utf-8'))
    source=json.loads((folder/'source-receipt.json').read_text(encoding='utf-8'))
    fields={'scheduling_reference':'Ark_emulator/docs/MECHANICS.md',
            'route_selector_reference':'tools/enemy_health/game_structs.py'}
    for key,name in fields.items():
        receipt=source['files'][name]
        assert digest(folder/'source'/name)==receipt['sha256']
        data['source'][key]={**receipt,'repository_commit':source['commit']}
    # Action data and existing enemy/cell fields stay byte-for-value identical.
    for sid,stage in data['stages'].items():
        path=ROOT/'.cache/game-data/levels'/(catalog()['stages'][sid]['levelId'].lower()+'.json')
        assert digest(path)==stage['level_source']['sha256']
        level=json.loads(path.read_text(encoding='utf-8'))
        stage['movement_multiplier']=level.get('options',{}).get('moveMultiplier')
        stage['extra_routes']=level.get('extraRoutes') or []
    data['version']=2
    data['limits'][2]='只提供以当前片段/分支阶段动作队列开始为锚点的名义生成偏移；全局时刻、帧执行和可见入场延迟尚未核验。'
    data['limits'].append('moveSpeed是基础移速属性；另列基础属性×关卡moveMultiplier的参考，技能/阶段等仍未计算。')
    data['limits'].append('原始299分支SPAWN均缺少运行时useExtraRoute选择字段；额外路线只保存为资料，不能按routeIndex直接定位。')
    dst=ROOT/'rouge/data/battle-previews.json'
    dst.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    receipt={'version':'0.40.0','stages':len(data['stages']),'images_downloaded_this_batch':0,
        'data_sha256':digest(dst),'inherited_data_sha256':digest(before),'source':data['source'],
        'movement_multipliers':{sid:s['movement_multiplier'] for sid,s in data['stages'].items()},
        'extra_route_records':sum(len(s['extra_routes']) for s in data['stages'].values()),
        'all_priorities_1_to_3_completed':False,'limits':data['limits']}
    (folder/'data-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'stages':receipt['stages'],'extra_routes':receipt['extra_route_records']}),flush=True)

if __name__=='__main__':main()
