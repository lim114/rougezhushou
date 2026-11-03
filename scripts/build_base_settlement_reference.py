"""Extract the public base settlement table, separately from native execution."""
import hashlib,json,re
from pathlib import Path
from scripts.build_choice_held_reference import Parser,walk,has_class
from rouge import node_catalog

ROOT=Path(__file__).resolve().parents[1]
CURRENT_SHA='8df90d811ef9516f46bb877a15c8701d83bd7d36ff744a42d9b27cfede8551e4'

def numeric(cell):
    base=[node.text() for node in walk(cell) if has_class(node,'is6-exp') and not has_class(node,'is-fulltech')]
    full=[node.text() for node in walk(cell) if has_class(node,'is-fulltech')]
    if base:
        assert len(base)==len(full)==1 and base[0].isdigit() and full[0].isdigit()
        return {'base':int(base[0]),'full_technology_reference':int(full[0]),'source_text':cell.text()}
    text=cell.text().strip()
    if text in ('?', '——'):return {'base':None,'full_technology_reference':None,'source_text':text}
    match=re.search(r'(\d+)(?:~(\d+))?\s*$',text);assert match,text
    lo=int(match.group(1));hi=int(match.group(2) or lo)
    return {'base':{'minimum':lo,'maximum':hi},'source_text':text}

def build(root=ROOT):
    root=Path(root);directory=root/'research/p3-base-settlement';raw=(directory/'current-main.html').read_bytes()
    assert hashlib.sha256(raw).hexdigest()==CURRENT_SHA
    text=raw.decode('utf8');assert '"wgRevisionId":433770' in text
    assert 'creativecommons.org/licenses/by-nc-sa/4.0/' in text
    parser=Parser();parser.feed(text)
    table=next(node for node in walk(parser.root) if node.tag=='table' and '作战指挥经验值及源石锭数量' in node.text())
    rows=[node for node in walk(table) if node.tag=='tr'];main={};special=[];previous=None;portal=None
    primary=json.loads((directory/'original-stage-meta.json').read_text(encoding='utf8'))
    original=json.loads((root/'rouge/data/node-events.json').read_text(encoding='utf8'))
    assert primary['table_sha256']==original['source']['game_data']['sha256']
    assert primary['commit']==original['source']['commit']
    assert primary['zones']['zone_6']['name']=='源流交汇处' and primary['zones']['zone_6']['zoneIconId']=='zone_6'
    assert len(primary['portal_zone_ids'])==len(set(primary['portal_zone_ids']))==19
    assert all(identity in primary['zones'] for identity in primary['portal_zone_ids'])
    assert any(has_class(node,'AKCollapse-title') and node.text()=='0 源流交汇处' for node in walk(parser.root))
    assert any(has_class(node,'AKCollapse-content') and '源流交汇处' in node.text()
        and '(VI)' in node.text() and '初始行动力：5，固定路线排布' in node.text() for node in walk(parser.root))
    floor_labels={'Ⅰ':1,'Ⅱ':2,'Ⅲ':3,'Ⅳ':4,'Ⅴ':5,'0':6}
    for index,row in enumerate(rows):
        cells=[node for node in row.children if node.tag in ('td','th')]
        if len(cells)==9 and cells[0].text() in floor_labels:
            floor=floor_labels[cells[0].text()];main[str(floor)]={}
            for offset,kind in enumerate(('normal','emergency','boss','boss_pursuit')):
                main[str(floor)][kind]={'experience':numeric(cells[1+offset*2]),'gold':numeric(cells[2+offset*2]),
                    'source_floor_label':cells[0].text(),'source_row_index':index,'source_column_kind':kind}
        if cells and cells[0].text().strip()=='/':
            assert len(cells)==6 and cells[1].attrs.get('colspan')=='4'
            assert cells[1].text()=='与战斗节点所属层/特殊战斗一致'
            assert all(cell.text().strip()=='——' for cell in cells[2:])
            portal={'source_text':cells[1].text(),'source_row_index':index,
                'inherited_column_kinds':['normal','emergency'],
                'undocumented_column_kinds':['boss','boss_pursuit'],
                'undocumented_cells':[cell.text().strip() for cell in cells[2:]],
                'blank_cells_do_not_prove_entry_impossible':True}
        links=[node for node in walk(cells[0]) if node.tag=='a' and (node.attrs.get('title') or '').startswith('ISW-')] if cells else []
        if links:
            assert len(cells)==3
            previous={'source_label':cells[0].text(),'links':[{'title':node.attrs['title'],'href':node.attrs['href']} for node in links]}
            xp,gold=cells[1:];difficulty='NORMAL'
        elif len(cells)==2 and previous and '紧急作战版本适用此掉落' in row.text():
            xp,gold=cells;difficulty='FOUR_STAR'
        else:continue
        ids=[]
        for link in previous['links']:
            code,_,name=link['title'].partition(' ')
            ids.extend(identity for identity,stage in primary['stages'].items()
                if stage['code']==code and stage['name']==name and stage['difficulty']==difficulty)
        assert ids,previous
        special.append({**previous,'difficulty':difficulty,'stage_ids':ids,'experience':numeric(xp),'gold':numeric(gold),
            'source_row_index':index,'binding':'exact page code+name+difficulty; every original ID retained',
            'native_settlement_script_verified':False})
    assert set(main)==set(map(str,range(1,7))) and len(special)==18 and portal is not None
    normalized=re.sub(r'\s+','',parser.root.text())
    ordinary='通常追猎通关时仅会掉落一张招募券，没有任何指挥经验、源石锭和收藏品报酬。'
    boss='险路恶敌追猎通关时则会正常掉落奖励。'
    assert ordinary in normalized and boss in normalized
    assert '多个指挥经验加成之间乘算叠加，最终结果向下取整' in normalized
    metadata={}
    current_stage_pages={node.attrs.get('title') for node in walk(parser.root) if node.tag=='a'}
    for row in node_catalog.battle_candidates()['rows']:
        original_stage=primary['stages'][row['id']]
        assert row['title']==original_stage['name'] and row['difficulty']==original_stage['difficulty']
        assert original_stage['code']+' '+original_stage['name'] in current_stage_pages
        zero_source=any(ref.get('display_floor')==0 and ref.get('source_membership') in
            ('normal_emergency_named_pool','boss_named_pool') for ref in row['source_references'])
        metadata[row['id']]={'original':original_stage,'documented_floors':row.get('documented_floors',row['floors']),
            'settlement_source_floors':[6] if zero_source else row['floors'],
            'floor_zero_binding':{'document_heading':'0 源流交汇处 (VI)','original_zone_id':'zone_6',
                'original_name':primary['zones']['zone_6']['name'],'original_icon':primary['zones']['zone_6']['zoneIconId'],
                'source':'public named pool label0 matches public area label0/VI and exact original name/icon; no stage suffix used'} if zero_source else None,
            'documented_categories':row['categories'],'source_pool_references':row['source_references'],
            'special_rule_indices':[i for i,rule in enumerate(special) if row['id'] in rule['stage_ids']]}
    assert len(metadata)==len(primary['stages'])==105
    return {'schema_version':1,'source':{'url':'https://m.prts.wiki/w/沉沦者的黑流树海','revision':'433770',
        'sha256':CURRENT_SHA,'file':'research/p3-base-settlement/current-main.html','license':'CC BY-NC-SA4.0',
        'scope':'base experience/gold table; not actual server settlement'},
        'original_source':original['source']['game_data']|{'commit':primary['commit']},
        'main_floor_table':main,'special_battle_table':special,'stages':metadata,'zones':primary['zones'],
        'portal_zone_ids':primary['portal_zone_ids'],'portal_zone_selector':primary['portal_zone_selector'],
        'ordinary_pursuit_rule':{'experience':0,'gold':{'minimum':0,'maximum':0},'source_text':ordinary,
            'boss_exception_text':boss,'extra_reward_total_verified':False},
        'portal_rule':portal,
        'limits':['基础分项不包含恶笼草、零件、藏品、分队、科技、难度与事件的额外或修正奖励。',
            '满级生命游戏列只是独立文档参考，没有推定本账户已解锁或当前已生效。',
            '秘境编号不是战斗所属主层；缺独立所属层声明时仅保留来源参考，无法给完整分项小计。',
            '秘境复用主层的来源列仅普通/紧急；首领及首领追猎空列保留数值未知，不证明入口不可能。',
            '同名事件战斗/普通追猎的结算入口须分别声明；不从关卡ID前缀或共用level文件选择。',
            '未核验实际胜利、领奖、服务器脚本和完整掉落池；条件小计不是实际奖励总量。']}

if __name__=='__main__':
    data=build()
    (ROOT/'rouge/data/base-settlement-reference.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    (ROOT/'research/p3-base-settlement/source-receipt.json').write_text(json.dumps({
        'source':data['source'],'original_source':data['original_source'],
        'counts':{'main_floors':6,'table_columns_per_floor':4,'special_rows':len(data['special_battle_table']),
            'special_original_ids':len({key for row in data['special_battle_table'] for key in row['stage_ids']}),
            'fixed_stage_metadata':105},
        'primary_stage_values_do_not_serialize_base_settlement':True,
        'zero_floor_binding':'Public源流交汇处(VI) heading plus exact original zone_6 name/icon; no hidden-zone suffix inference.',
        'ordinary_pursuit_scope':data['ordinary_pursuit_rule'],'portal_scope':data['portal_rule'],'limits':data['limits'],
        'license':'Community source CC BY-NC-SA4.0; original game data/text remain Hypergryph copyright.'},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
