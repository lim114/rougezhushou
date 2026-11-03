"""Rebuild the fixed entry catalogue from exact IDs and a frozen public receipt."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def read(path):return json.loads(path.read_text(encoding='utf8'))


def build(root=ROOT):
    pool=read(root/'rouge/data/battle-node-pools.json')
    metadata=read(root/'rouge/data/view-catalog.json')['stages']
    stages=read(root/'rouge/data/battle-previews.json')['stages']
    receipt=read(root/'research/p3-stage-context/source-receipt.json')
    assert pool['sources']['game_display_table']['sha256']==receipt['game_table_sha256']
    assert pool['sources']['community_main_page']['revision']==str(receipt['community_revision'])
    body=(root/receipt['community_file']).read_bytes()
    assert hashlib.sha256(body).hexdigest()==receipt['community_sha256']
    records={}
    titles={'ro6_t_6':'死箱','ro6_t_7':'活木','ro6_t_10':'枯枝','ro6_t_11':'败叶',
            'ro6_duel_1':'搏杀','ro6_duel_2':'共斗'}
    for sid,title in titles.items():
        assert stages[sid]['name']==pool['stages'][sid]['name']==title
        assert sum(s['name']==title for s in stages.values())==1
    for sid,meta in metadata.items():
        if meta['group']!='unconfirmed':continue
        p=pool['stages'][sid];conditions=[]
        assert p['stage_id']==sid and p['name']==stages[sid]['name']
        links={r['source_membership'] for r in p['source_references']}
        if 'shop_battle_named_pool' in links:
            group='shop_challenge';label='诡意行商 · 坎诺特挑战';entry='诡意行商中选择请坎诺特降价；公开说明另列历史最高投资额50门槛，该跨局资格未自动取得。'
            assert sid in ('ro6_t_6','ro6_t_7')
            allowed=[1,2,3] if sid=='ro6_t_6' else [4,5,6]
            conditions=[{'kind':'main_floor','allowed':allowed,'node_type':'诡意行商','entry_scope':'shop_challenge',
                         'description':'仅商店挑战入口：到达第4主层前对应死箱，第4主层及之后对应活木；秘境口径未证。',
                         'source_rule':'shop_before_after_four'}]
        elif p['natural_node_types']==['“居民”据点']:
            group='resident_stronghold';label='自然“居民”据点';entry='原具名自然据点池与结算标签直接对应；流窜居民占领不是此入口。'
            assert sid in ('ro6_t_10','ro6_t_11')
            conditions=[{'kind':'main_floor','allowed':[2,3,4,5],'node_type':'“居民”据点','entry_scope':'natural_node',
                         'description':'仅自然“居民”据点入口：不在第I、VI主层出现。','source_rule':'resident_natural_node'},
                        {'kind':'difficulty','minimum':4,'node_type':'“居民”据点','entry_scope':'natural_node',
                         'description':'仅自然“居民”据点入口：保密等级4及以上可能出现。','source_rule':'resident_natural_node'}]
        elif 'resident' in p['categories']:
            group='roaming_resident';label='流窜“居民”占领战斗';entry='原结算标签直接列为流窜居民；各原ID分别保留，不套自然据点层数、难度或克隆后缀规则。'
        elif 'duel_event_named_pool' in links:
            group='duel';label='狭路相逢 · 特殊战斗';entry='狭路相逢节点选择公平战斗；原具名池直接对应搏杀/共斗。'
            assert sid in ('ro6_duel_1','ro6_duel_2')
            conditions=[{'kind':'main_floor','allowed':[3,4,5],'node_type':'狭路相逢','entry_scope':'natural_node',
                         'description':'仅自然狭路相逢节点入口：不在第I、II、VI主层出现。','source_rule':'duel_natural_node'}]
        elif 'special' in p['categories']:
            group='special_challenge';label='事件 / 特殊挑战';entry='固定社区具名特殊挑战池；若兼有事件来源，两项均保留，层数资格仍未取得。'
        else:
            assert 'event' in p['categories'];group='event';label='不期而遇 · 事件内战斗';entry='固定社区具名事件战斗池与原结算上下文对应；各普通/紧急原ID分别保留，事件入口条件另核验。'
        assert p['game_stage_field_path']=='$.details.rogue_6.stages.'+sid
        records[sid]={'stage_id':sid,'name':stages[sid]['name'],'group':group,'label':label,
                      'conditions':conditions,'entry_reference':entry,
                      'source_references':p['source_references'],
                      'natural_node_types':p['natural_node_types'],'content_node_types':p['content_node_types'],
                      'game_stage_field_path':p['game_stage_field_path'],
                      'original_floor_metadata':meta,'settlement_context_references':p['settlement_context_references']}
    assert len(records)==21 and sum(bool(r['conditions']) for r in records.values())==6
    return {'schema_version':1,'source':receipt,'stages':records,
            'limitations':['匹配仅指已列条件；挑战解锁、其他前置及完整服务器资格仍未知。',
                          '特殊区域层数口径未证；不能用秘境区域ID后缀充当主层。',
                          '自然节点范围不用于内容强制入口、历史读取或流窜居民克隆。',
                          '15个原事件/特殊关卡尚无层数适用依据；未把同类关卡当当前可发生全集。',
                          '固定原件与社区条件引用分别保留，不宣称当前客户端全覆盖。']}


if __name__=='__main__':
    target=ROOT/'rouge/data/stage-context-reference.json'
    target.write_text(json.dumps(build(),ensure_ascii=False,indent=2),encoding='utf8')
