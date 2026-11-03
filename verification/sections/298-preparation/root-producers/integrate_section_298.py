from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def edit(name,pairs):
 p=ROOT/name;raw=p.read_bytes();newline=b'\r\n'if b'\r\n'in raw else b'\n'
 for old,new in pairs:
  a=old.replace('\n',newline.decode()).encode();b=new.replace('\n',newline.decode()).encode()
  assert raw.count(a)==1,(name,old[:100],raw.count(a));raw=raw.replace(a,b)
 p.write_bytes(raw)
edit('rouge/node_catalog.py',[
 ('from .stage_context import stage_context','from .stage_context import stage_context\nfrom . import event_node_requirements as natural_requirements'),
 ("def event_candidates(node_type=None,floor=None,special_region=False,include_indirect=False):\n    _floor(floor,special_region)",'''def natural_event_requirements(event,*,floor=None,entry_mode='unknown',special_region=False,historical=False):
    """Bind independent rules to the complete actual reading object too."""
    result=natural_requirements.event_requirements(event['id'],floor=floor,entry_mode=entry_mode,
        special_region=special_region,historical=historical)
    if result and result['source_valid'] and not natural_requirements._same_json(event,result['expected_event']):
        return {'status':'source_unavailable','source_valid':False,'event_id':event['id'],
            'context_applicable':result['context_applicable'],'context':result['context'],
            'documented_floor_match':None,'documented_excluded_main_floors':[],
            'check':None,'source':None,'source_reference':None,'technology_enabling_reference':None,
            'actual_server_eligible':None,'probability':None,
            'notice':'节点主层资料与当前阅读内容不一致；不能沿用旧禁区排除事件。'}
    return result

def event_candidates(node_type=None,floor=None,special_region=False,include_indirect=False,*,entry_mode='natural',historical=False):
    _floor(floor,special_region)
    if entry_mode not in ('unknown','natural','content','processed_item','history') or type(historical) is not bool:
        raise ValueError('入口范围或历史标记不正确。')'''),
 ("        e['floor_status']='目录主层条件相符'",'''        reference=natural_event_requirements(_event(e['id']),floor=floor,entry_mode=entry_mode,
            special_region=special_region,historical=historical)
        if reference and reference['documented_floor_match'] is False:
            excluded.append({**e,'reason':reference['check']['source_text'],
                'entry_condition_excluded_reference':True,'natural_requirement_reference':reference});continue
        e['floor_status']='目录主层条件相符' '''.rstrip()),
 ("    by_id={}\n    for t in types:\n        for e in event_candidates(t,floor,special_region)['rows']:by_id[e['id']]=e\n    return _result(list(by_id.values()),history_candidates=history,type_candidates=deepcopy(types),",'''    by_id={};excluded={}
    for t in types:
        candidates=event_candidates(t,floor,special_region)
        for e in candidates['rows']:by_id[e['id']]=e
        for e in candidates['excluded']:excluded[e['id']]=e
    return _result(list(by_id.values()),excluded=list(excluded.values()),history_candidates=history,type_candidates=deepcopy(types),'''),
 ("        generic_event_candidates=deepcopy(events['rows']),generic_battle_candidates=generic_battles,", "        generic_event_candidates=deepcopy(events['rows']),generic_battle_candidates=generic_battles,\n        excluded_event_candidates=deepcopy(events.get('excluded',[])) if not observed_refs and not pass_through else [],")])
edit('rouge/event_planning.py',[
 ("    mode=context.get('entry_mode','unknown')\n    if event['natural'] is False:",'''    mode=context.get('entry_mode','unknown')
    historical=context.get('reference_context_scope')=='historical_title_reference_only'
    reference=catalog.natural_event_requirements(event,floor=floor,entry_mode=mode,
        special_region=context.get('special_region',False),historical=historical)
    if reference and reference['context_applicable']:
        checks.append(deepcopy(reference['check']) if reference['source_valid'] else
            _check('documented_node_natural_main_floor',None,
                '自然主层限制资料暂时无法核对；不能据此排除。',kind='source_node_floor_requirement',source_valid=False))
    if event['natural'] is False:''')])
edit('rouge/node_catalog_view.py',[
 ("            events=[*self.dossier['rows'],*self.dossier.get('history_observed_event_rows',[])]",'''            current_ids={e['id'] for e in self.dossier['rows']}
            excluded=[e for e in self.dossier.get('excluded_event_candidates',[]) if e['id'] not in current_ids]
            events=[*self.dossier['rows'],*excluded,*self.dossier.get('history_observed_event_rows',[])]''')])
edit('rouge/player_node_information.py',[
 ("    scenes = result['rows']\n    numbers = {scene['key']: number for number, scene in enumerate(scenes, 1)}",'''    scenes = result['rows']
    if context.get('entry_mode') in ('natural','content','processed_item'):
        reading=deepcopy(catalog._event(event_id));reading['scenes']=deepcopy(scenes)
        reference=catalog.natural_event_requirements(reading,floor=context.get('floor'),
            entry_mode=context['entry_mode'],special_region=context.get('special_region',False),
            historical=historical or context.get('reference_context_scope')=='historical_title_reference_only')
        if reference:
            lines+=['','【自然出现的已知条件】']
            if not reference['source_valid']:
                lines.append('节点主层资料暂时无法核对；不沿用旧限制，保留原文与资格未知。')
            else:
                floors='、'.join('第'+str(n)+'层' for n in reference['documented_excluded_main_floors'])
                lines.append('资料记载：'+reference['node_type']+'不会自然出现在'+floors+'。')
                match=reference['documented_floor_match']
                lines.append('当前主层不在上述自然出现范围内；下方仍可查阅完整事件资料。' if match is False else
                    '当前主层未被这条限制排除；其它出现条件和实际生成仍未知。' if match is True else
                    '本次为已读、历史、特殊区域或条件未齐的参考；不据此删除内容或判定不能进入。')
                tech=reference['technology_enabling_reference']
                if tech:
                    lines.append('已知开启途径：生命游戏中的“'+tech['name']+'”。')
                    lines.append('这是一条已知开启途径；本账号是否点亮尚未确认，不能据未点亮就认定绝不出现。')
                lines.append('以上为固定版本的资料范围，未证明当前服务器的全部出现条件。')
    numbers = {scene['key']: number for number, scene in enumerate(scenes, 1)}''')])
edit('tests/test_node_catalog.py',[("        self.assertTrue(c.event_candidates('先行一步',floor=6)['rows'])",'''        r=c.event_candidates('先行一步',floor=6)
        self.assertFalse(r['rows'])
        self.assertEqual([e['id'] for e in r['excluded']],['community_group_024'])
        self.assertFalse(r['excluded'][0]['natural_requirement_reference']['documented_floor_match'])''')])
print('298 four production seams and exact historical assertion migrated; no tests run here')
