"""Plain test report: observed names, same-run memory, and predictions differ."""
from .node_rewards import preview_node_rewards
from .catalog import catalog
from .run_config import config_data
from .exploration_routes import route_reference


def _candidate_name(candidate):
    name = candidate.get('name')
    if name and name.startswith('空分支'):
        return '不生成对象'
    if name:
        return name
    return '名称未确认的对象' if candidate.get('entity_id') else '不生成对象'


def format_rewards(content, *, technical=False):
    """Use named conditional rewards and spawn candidates without a guessed rate."""
    if not content:
        return ''
    preview = preview_node_rewards(content)
    lines = ['奖励资料参考：'+str(content.get('title') or '身份未确认')]
    sources = []
    if preview['event_options']:
        lines.extend(['', '【选项奖励】'])
    for option in preview['event_options']:
        lines.append('选项「'+str(option['title'])+'」：')
        for candidate in option['reward_candidates']:
            item = candidate['reward']
            lines.append('  条件满足后可获得：'+item['name']+'；数量未确认')
            if candidate.get('condition_text'):
                lines.append('  条件：'+candidate['condition_text'])
            lines.append('  领取资格与当前流程尚未核实；未计入本局持有。')
            sources.append(candidate['evidence']['url'])
        if option['status'] == 'ambiguous':
            lines.append('  选项或流程存在多个候选，奖励尚未唯一确定。')
        if not option['reward_candidates'] or option['unresolved_choice_ids']:
            lines.append('  另有选项奖励未核验，保持未知。')
    if preview['battle_variants']:
        lines.extend(['', '【关卡生成候选】'])
    technical_candidates = []
    for variant in preview['battle_variants']:
        label = '紧急' if variant['difficulty'] == 'FOUR_STAR' else '普通'
        lines.append('关卡：'+variant['name']+'（'+label+'）')
        for field, label in (('battle_chest_groups','宝箱生成候选'),('rare_enemy_groups','特殊敌人生成候选')):
            for index, group in enumerate(variant[field], 1):
                names = list(dict.fromkeys(_candidate_name(c) for c in group['candidates']))
                lines.append(f'  {label}组{index}：'+' / '.join(names))
                if technical:
                    technical_candidates.extend(str(c['entity_id']) for c in group['candidates'] if c.get('entity_id'))
        lines.append('  生成条件和概率未核验；生成候选不等于击破奖励或结算掉落。')
        sources.append(variant['level_evidence']['url'])
    lines.extend(['', '【尚未核验】'])
    if preview['status'] == 'unknown':
        lines.append('尚无足够的奖励或生成候选资料。')
    for missing in preview['unresolved_pools']:
        lines.append(missing['reason'])
    if sources:
        lines.extend(['', '【资料依据】', '来源：具名选项奖励资料与游戏原始关卡资料；技术资料可查看对应引用。'])
    if technical:
        lines.extend(['', '【技术引用】'])
        if preview.get('variant_candidates'):
            lines.append('关卡引用：'+'、'.join(preview['variant_candidates']))
        if preview.get('scene_candidates'):
            lines.append('流程引用：'+'、'.join(preview['scene_candidates']))
        if technical_candidates:
            lines.append('生成对象引用：'+'、'.join(dict.fromkeys(technical_candidates)))
        if sources:
            lines.append('资料来源：'+'\n'.join(dict.fromkeys(sources)))
    return '\n'.join(lines)


def location(node, rows):
    row = ('上排', '中排', '下排')[node['row']] if rows == 3 else f"第{node['row']+1}排"
    return f"{row} · 第{node['col']+1}列"


def _map_position(graph, node_id):
    node = next((n for n in graph.get('nodes', []) if n['id'] == node_id), None)
    return location(node, graph['grid']['rows']) if node else '位置未确认'


def _zone_name(zone_id):
    return config_data()['zones'].get(zone_id, {}).get('name') or '区域名称未确认'


def _variant_label(content):
    stage = catalog()['stages'].get(content.get('variant_id'))
    if not stage or stage.get('name') != content.get('title'):
        return '未唯一确认；普通/紧急可能同名'
    return {'FOUR_STAR': '紧急作战', 'NORMAL': '普通作战'}.get(stage.get('difficulty'), '关卡难度未确认')


def format_route(graph, node_id, *, historical=False, technical=False, compact=False):
    route = route_reference(graph, node_id, historical=historical)
    if route['status'] == 'unavailable':
        reason = route['reason']
        return {'historical_frame': '当前路线未计算：画面为历史参考。',
                'current_unconfirmed': '当前路线未计算：本帧位置未确认，最近历史位置不作为起点。',
                'disconnected': '当前路线未计算：模板连线中没有通向此节点的路径。',
                'invalid_graph': '当前路线未计算：布局连线资料不完整。',
                'target_unconfirmed': '请选择地图上的节点查看路线。',
                'layout_unconfirmed': '当前路线未计算：布局尚未确认。'}[reason]
    if route['status'] == 'same_position':
        return '当前已在所选位置；移动距离为0。重新进入可重复节点通常另耗1行动力，不计为免费进入。'
    path = route['topology']; corridor = route['corridor']
    lines = [f"从当前确认位置出发：模板最短连线 {path['steps']} 步。"]
    if path['equal_shortest_paths'] > 1:
        lines.append(f"同长拓扑路线 {path['equal_shortest_paths']} 条。"+
                     ('图上展示其中一条参考。' if not corridor or corridor['steps']==path['steps']
                      else '图上展示满足途中类型条件的较长绕行路线。'))
    if corridor:
        lines.append(f"途中均为本帧已读空地或曲折密道的最短路线：{corridor['steps']} 步；正常徒步基础消耗 {corridor['base_walking_ap']} 行动力。")
        if corridor['equal_shortest_paths'] > 1:
            lines.append(f"满足上述途中类型条件的同长路线 {corridor['equal_shortest_paths']} 条。")
    else:
        lines.append('橙色虚线仅表示拓扑参考；未确认存在可直接徒步的路线。')
        if not route['target_revealed']:
            lines.append('目标尚未在本帧明确揭示；模板或历史名称不证明现在可进入。')
        if path['unconfirmed_intermediate_nodes']:
            lines.append('途中通过情况未确认：'+'、'.join(_map_position(graph,key)
                         for key in path['unconfirmed_intermediate_nodes'])+'。已揭示节点仍可能需要先完成。')
    if compact:
        summary = (f"途中类型符合穿越条件的路线：{corridor['steps']} 步，普通徒步基础 {corridor['base_walking_ap']} 行动力。"
                   if corridor else '橙色虚线仅作拓扑参考，尚未确认可直接徒步。')
        return lines[0]+'\n'+summary+'实际阻碍和当前行动力尚未确认；详见节点报告。'
    lines.append('图上路线：'+' → '.join(_map_position(graph,key) for key in route['display_path']))
    lines.append('住民占领、弥散虚雾、完成标志及当前行动力未完整读取；连线尚未独立核验，不保证可出发。基础消耗未计羽瞰点返还与其他修正；结局和难度收益未参与比较。')
    if technical:
        lines.append('徒步规则来源：PRTS《沉沦者的黑流树海》；当前页面观察及原文哈希见本批路线证据。')
        lines.append('https://prts.wiki/w/沉沦者的黑流树海')
    return '\n'.join(lines)


def format_node(graph, node_id, *, historical=False, technical=False):
    node = next((n for n in graph['nodes'] if n['id']==node_id), None) if graph else None
    if node is None:
        return ''
    lines = [location(node, graph['grid']['rows']), '', '【节点状态】']
    if historical:
        lines.append('历史参考；不代表本帧状态。')
    if node.get('visible'):
        lines.append(('当时可见：' if historical else '本帧可见：')+(node.get('observed_type') or '类型未读到'))
    else:
        lines.append('位置由模板推测；该帧未观察到节点。')
    if not historical and graph.get('current_node')==node_id:
        lines.append('当前确认位置')
    elif (graph.get('last_confirmed_current_node') or graph.get('current_node'))==node_id and (historical or not graph.get('current_node')):
        lines.append('最近确认位置（历史；本帧未确认）')
    if node.get('remembered_type'):
        lines.append('本局已揭示记录：'+node['remembered_type'])
    if node.get('template_type'):
        lines.append('模板固定类型：'+node['template_type'])
    content=node.get('content') or node.get('remembered_content')
    if content:
        lines.extend(['', '【具体内容】'])
        lines.append(('本局内容记录：' if historical or not node.get('content') else '具体内容：')+content['title'])
        if content.get('kind')=='battle':
            lines.append('关卡变体：'+_variant_label(content))
        elif content.get('scene_candidates'):
            lines.append(f"流程阶段候选：{len(content['scene_candidates'])}个；标题和描述可能重复，不按名称强行唯一。")
        if content.get('visible_options'):
            lines.append('本帧可见选项：'+' / '.join(o['title'] for o in content['visible_options']))
        lines.extend(['', format_rewards(content, technical=technical)])
    else:
        lines.append('具体事件/关卡尚未揭示；节点类型不能唯一决定内容。')
    prediction = node.get('prediction')
    if prediction:
        lines.extend(['', '【类型候选】'])
        label = '本局历史类型' if prediction.get('evidence')=='visible_history' else '社区约束候选'
        lines.append(label+'：'+(' / '.join(prediction.get('candidates',[])) or '未能确定'))
        if prediction.get('reason'): lines.append('依据：'+prediction['reason'])
        if prediction.get('notice'): lines.append(prediction['notice'])
        if prediction.get('evidence')!='visible_history':
            lines.append('候选没有统计概率，也不表示游戏已揭示。')
    lines.extend(['', '【路线参考】', f"距初始起点最短 {node['distance']} 步（沿模板连线；不是从当前位置出发）"])
    lines.append(format_route(graph,node_id,historical=historical,technical=technical))
    budget=graph.get('generation_budget',{})
    counts=[name for name in (node.get('prediction') or {}).get('candidates',[]) if name in budget]
    if counts:
        lines.append('类型预算（固定格与已知格去重；不是概率）：')
        for name in counts:
            b=budget[name]
            lines.append(f"{name}：固定{b['fixed']} + 其他已知{b['revealed_additional']}；来源总上限{b['source_max'] if b['source_max'] is not None else '未知'}")
    lines.extend(['', '【资料依据】', '来源：社区模板资料与本局已揭示记录；技术资料可查看对应引用。'])
    if technical:
        lines.extend(['', '【地图技术引用】', '区域引用：'+str(graph.get('zone_id')),
                      '模板引用：'+str(graph.get('template_id')), '节点引用：'+str(node_id),
                      '来源：'+graph['source']['url']])
    return '\n'.join(lines)


def format_map(current, remembered, *, technical=False):
    lines = []
    if current and current.get('status')=='matched':
        graph = remembered or current
        lines.append('当前帧布局匹配；以下隐藏节点为社区约束候选，不是概率或游戏揭示。')
    elif remembered:
        graph = remembered
        lines.append('历史参考：本局最近一次充分匹配的地图。本帧未确认新布局，保留旧记录。')
        if current: lines.append('本帧：'+current.get('reason', '识别状态未确认'))
    else:
        lines.append('尚无可用地图记录。请在游戏显示探索地图后等待自动采样；可以处于后台。')
        if current:
            lines.append('本帧：'+current.get('reason','未能确认布局'))
            choices = current.get('candidate_templates',[])
            if choices:
                lines.append(f'布局候选：{len(choices)}种；尚未唯一确认。')
                if technical: lines.append('布局引用：'+'、'.join(t['id'] for t in choices))
        return '\n'.join(lines)
    lines.extend(['', '【地图概况】', '区域：'+_zone_name(graph.get('zone_id')),
        f"节点 {len(graph['nodes'])} · 连线 {len(graph['edges'])} · 当前节点：{_map_position(graph, graph.get('current_node'))}",
        '步数由沿模板连线从初始起点的最短路径计算；固定位置来自模板，不冒充当前已揭示。', ''])
    if not graph.get('current_node') and graph.get('last_confirmed_current_node'):
        lines.append('最近确认位置：'+_map_position(graph, graph['last_confirmed_current_node'])+'（历史；本帧标记未读到）')
    lines.extend(['', '【节点列表】'])
    for node in graph['nodes']:
        observed = node.get('observed_type') or ('类型未读到' if node.get('visible') else '本帧未观察到')
        text = f"{location(node, graph['grid']['rows'])} · 距初始起点最短{node['distance']}步 · 可见：{observed}"
        if node.get('remembered_type'): text += ' · 本局已揭示记录：'+node['remembered_type']
        if node.get('template_type'): text += ' · 模板固定：'+node['template_type']
        prediction = node.get('prediction')
        if prediction:
            prefix = '本局历史' if prediction.get('evidence')=='visible_history' else '社区约束候选'
            text += ' · '+prefix+'：'+(' / '.join(prediction['candidates']) or '未能确定')
        lines.append(text)
    lines.extend(['', '【资料依据与限制】', '来源：社区模板资料与本局已揭示记录；技术资料可查看对应引用。', *graph.get('limitations',[])])
    if graph.get('generation_budget'):
        lines.extend(['', '【生成数量约束】', '生成预算：固定位置与已揭示记录按节点去重；候选没有生成权重，不进行等概率归一化。'])
        for name,b in graph['generation_budget'].items():
            if not b['known_total']:continue
            lines.append(f"{name}：固定{b['fixed']} / 已知总数{b['known_total']} / 来源上限{b['source_max'] if b['source_max'] is not None else '未知'}"+
                         ('；本层仅固定生成，不进入随机池' if not b['random_eligible'] else ''))
        lines.extend(graph.get('generation_limitations',[]))
    if graph.get('constraint_conflicts'):
        lines.append('约束冲突：已揭示记录与模板约束不一致；暂停其他隐藏节点候选筛选。')
    if technical:
        lines.extend(['', '【地图技术引用】', '区域引用：'+str(graph.get('zone_id')),
                      '模板引用：'+str(graph.get('template_id')), '来源：'+graph['source']['url']])
        lines.extend('节点引用：'+str(node['id'])+' → '+location(node, graph['grid']['rows']) for node in graph['nodes'])
        if graph.get('constraint_conflicts'):
            lines.append('冲突引用：'+','.join(graph['constraint_conflicts']))
    return '\n'.join(lines)
