"""Read-only map registration from current-frame geometry and sourced layouts."""
import json
from collections import Counter
from itertools import combinations
from functools import lru_cache
from pathlib import Path
import cv2
import numpy as np


@lru_cache(maxsize=1)
def map_data():
    return json.loads((Path(__file__).with_name('data')/'map-templates.json').read_text(encoding='utf-8'))


@lru_cache(maxsize=1)
def generation_data():
    return json.loads((Path(__file__).with_name('data')/'node-generation.json').read_text(encoding='utf-8'))


def predict_map(graph):
    """Constraint candidates only; no frequency data or random-state access."""
    if graph.get('status') != 'matched': return graph
    rules = map_data()['rules']; zid = graph['zone_id']
    revealed = {n['id']: n['observed_type'] for n in graph['nodes']
                if n.get('observed_type') and not n['observed_type'].startswith('未知')
                and n['observed_type'] != '林间空地'}
    remembered = {n['id']: n['remembered_type'] for n in graph['nodes'] if n.get('remembered_type')}
    remembered.update(revealed)
    # Fixed generation slots contribute once; repeated frames/labels do not.
    counted = {n['id']: n['template_type'] for n in graph['nodes'] if n.get('template_type')}
    counted.update(remembered)
    counts = Counter(counted.values())
    generation=generation_data();fixed_only=generation['fixed_only'].get(zid,[])
    always_visible=generation['always_revealed']+generation.get('zone_always_revealed',{}).get(zid,[])
    difficulty=graph.get('difficulty_value')
    def hidden_eligible(name):
        if name in always_visible:return False
        if name=='险路尽头' and difficulty is not None and difficulty<3:return False
        return True
    fixed=Counter(n['template_type'] for n in graph['nodes'] if n.get('template_type'))
    graph['generation_budget']={name:{'fixed':fixed[name], 'known_total':counts[name],
        'revealed_additional':sum(t==name and key not in {n['id'] for n in graph['nodes'] if n.get('template_type')}
                                  for key,t in remembered.items()),
        'source_max':rule['zones'][zid]['max_count'],
        'remaining_capacity':max(0,rule['zones'][zid]['max_count']-counts[name]) if rule['zones'][zid]['max_count'] is not None else None,
        'random_eligible':name not in fixed_only,'hidden_eligible':hidden_eligible(name)}
        for name,rule in rules.items() if zid in rule['zones']}
    graph['generation_evidence']=generation['source']
    graph['generation_limitations']=generation['limitations']
    conflicts = [n['id'] for n in graph['nodes'] if n.get('template_type') and
                 n['id'] in remembered and remembered[n['id']] != n['template_type']]
    visibility_conflicts=[n['id'] for n in graph['nodes'] if n.get('observed_type','') and
        n['observed_type'].startswith('未知') and n.get('template_type') and not hidden_eligible(n['template_type'])]
    visits=set(graph.get('vantage_confirmed_visits',[]))
    vantage_nodes=[n for n in graph['nodes'] if remembered.get(n['id'])=='羽瞰点']
    if graph.get('current_node') in {n['id'] for n in vantage_nodes}:visits.add(graph['current_node'])
    graph['vantage_confirmed_visits']=sorted(visits)
    graph['reveal_ranges']=[{'node_id':n['id'],'row':n['row'],'col':n['col'],
        'minimum_radius':2 if n['id'] in visits else 1,'metric':'grid_manhattan',
        'notice':'只使用已知基础最小揭示范围；未确认长期科技不增加半径。'} for n in vantage_nodes]
    range_conflicts=[n['id'] for n in graph['nodes'] if (n.get('observed_type') or '').startswith('未知')
        and any(abs(n['row']-v['row'])+abs(n['col']-v['col'])<=v['minimum_radius'] for v in graph['reveal_ranges'])]
    graph['reveal_range_conflicts']=range_conflicts
    visibility_conflicts.extend(range_conflicts)
    hidden_exits=[n['id'] for n in graph['nodes'] if n.get('observed_type','') and
        n['observed_type'].startswith('未知') and n.get('template_type')=='险路尽头']
    if len(hidden_exits)>1:visibility_conflicts.extend(hidden_exits)
    graph['visibility_conflicts']=sorted(set(visibility_conflicts))
    graph['capacity_conflicts']=[name for name,record in graph['generation_budget'].items()
        if record['source_max'] is not None and record['known_total']>record['source_max']]
    conflicts=sorted(set(conflicts+visibility_conflicts))
    graph['constraint_conflicts'] = conflicts
    for node in graph['nodes']:
        label = node.get('observed_type')
        if not label or not label.startswith('未知'): continue
        if node['id'] in remembered:
            node['prediction'] = {'status': 'remembered', 'candidates': [remembered[node['id']]],
                'probability': None, 'evidence': 'visible_history', 'reason': '本局该网格先前已揭示，保留原记录。'}
            continue
        if conflicts or graph['capacity_conflicts']:
            node['prediction'] = {'status': 'conflict', 'candidates': [], 'probability': None,
                'evidence': 'community_constraints', 'reason': '已知类型、明示状态或数量与约束冲突，暂停候选筛选。'}
            continue
        candidates = []
        reason = '沿模板连线的起点最短步数、节点类别和已知数量上限'
        if node.get('template_type'):
            candidates = [node['template_type']]; reason = '来源模板的固定生成位置；并非本帧直接揭示'
        else:
            category = 'battle' if label=='未知的凶戾' else 'other'
            for name, rule in rules.items():
                limits = rule['zones'].get(zid)
                if (rule['category'] != category or not limits or name in fixed_only or not hidden_eligible(name)
                        or zid in generation.get('ordinary_generation_disabled',{}).get(name,[])): continue
                if limits['min'] is not None and node['distance'] < limits['min']: continue
                if limits['max'] is not None and node['distance'] > limits['max']: continue
                if limits['max_count'] is not None and counts[name] >= limits['max_count']: continue
                candidates.append(name)
        node['prediction'] = {'status': 'candidates' if candidates else 'unresolved',
            'candidates': candidates, 'probability': None, 'evidence': 'community_constraints',
            'distance_from_start': node['distance'], 'reason': reason,
            'notice': '社区生成约束推断；单候选也不是游戏已揭示信息。'}
        node['prediction']['excluded_revealed_types']=always_visible
        node['prediction']['excluded_fixed_only_types']=fixed_only
    return graph


def _axis(values, count):
    if not values or count<2:return None
    tolerance=max(1e-5,(max(values)-min(values))/(count-1)*.12)
    groups = []
    for value in sorted(values):
        if groups and value - np.median(groups[-1]) < tolerance: groups[-1].append(value)
        else: groups.append([value])
    if len(groups)<count or len(groups)>count+3:return None
    candidates=[]
    for indices in combinations(range(len(groups)),count):
        centers=np.array([np.median(groups[i]) for i in indices])
        pitch,origin=np.polyfit(np.arange(count),centers,1)
        residual=float(np.max(np.abs(origin+pitch*np.arange(count)-centers)))
        if pitch>tolerance*3 and residual<=pitch*.12:
            candidates.append((sum(len(groups[i]) for i in indices),residual,float(origin),float(pitch)))
    if not candidates:return None
    candidates.sort(key=lambda c:(-c[0],c[1]))
    support,error,origin,pitch=candidates[0]
    # Extra circular UI artwork is an outlier, but competing grids remain unknown.
    if any(c[0]==support and (abs(c[2]-origin)>pitch*.16 or abs(c[3]-pitch)>pitch*.16)
           for c in candidates[1:]):return None
    return origin,pitch


def _rings(image, labels):
    h,w=image.shape[:2]
    if not labels:return []
    font=float(np.median([(max(p[1] for p in n['box'])-min(p[1] for p in n['box']))*h for n in labels]))
    centers=[(float(np.mean([p[0] for p in n['box']]))*w,
              float(np.mean([p[1] for p in n['box']]))*h-font*1.8) for n in labels]
    xs,ys=zip(*centers);padding=max(font*6,(max(xs)-min(xs))*.5)
    x0=max(0,round(min(xs)-padding));x1=min(w,round(max(xs)+padding))
    y0=max(0,round(min(ys)-font*4));y1=min(h,round(max(ys)+font*4))
    content=image[y0:y1,x0:x1]
    if not content.size:return []
    scale=min(1.,1500/content.shape[1],1000/content.shape[0])
    small=cv2.resize(content,None,fx=scale,fy=scale) if scale<1 else content
    sh,sw=small.shape[:2];gray=cv2.cvtColor(small,cv2.COLOR_BGR2GRAY)
    local_font=font*scale
    circles=cv2.HoughCircles(gray,cv2.HOUGH_GRADIENT,1.2,max(10,local_font*1.3),
        param1=80,param2=26,minRadius=max(4,round(local_font*.25)),maxRadius=max(9,round(local_font*.85)))
    points = []
    for x, y, radius in (() if circles is None else circles[0]):
        x, y, r = round(float(x)), round(float(y)), round(float(radius))
        k = round(r*1.5)
        if not (k <= x < sw-k and k <= y < sh-k): continue
        patch = gray[y-k:y+k+1, x-k:x+k+1]
        yy, xx = np.ogrid[-k:k+1, -k:k+1]; radial = np.sqrt(xx*xx+yy*yy)/r
        inner = np.median(patch[radial < .3])
        # Hough can select either inner or outer ring. Check its radial trough
        # instead of assuming the detected radius is the dark annulus itself.
        bands = [(q, np.median(patch[(radial>q)&(radial<q+.12)])) for q in (.5,.6,.7,.8,.9,1.)]
        q, rim = min(bands, key=lambda pair: pair[1])
        outer = np.median(patch[(radial>q+.18)&(radial<q+.32)])
        # Empty graph nodes have a dark ring between lighter center and route.
        # Sprite decorations and letters may be circular but lack this profile.
        if inner-rim >= 20 and outer-rim >= 15 and np.mean(patch[radial<.5]>200)<.15:
            points.append({'center': [(x/scale+x0)/w, (y/scale+y0)/h], 'source': '可见空白圆环'})
    return points


def read_map(image, texts, labels, run):
    zone = (run or {}).get('config', {}).get('zone', {})
    zid = zone.get('id')
    templates = [t for t in map_data()['templates'] if t['zone_id'] == zid]
    base = {'status': 'unavailable', 'zone_id': zid, 'template_id': None,
        'difficulty_value':(run or {}).get('config',{}).get('difficulty',{}).get('value'),
        'candidate_templates': [], 'nodes': [], 'edges': [], 'current_node': None,
        'source': map_data()['source'], 'limitations': [
            '布局及生成约束来自社区采集，尚非官方隐藏生成脚本；候选不是概率。',
            '仅当前帧充分匹配才输出布局；局部遮挡或滚动裁剪不强行认定。']}
    if not templates:
        base['reason'] = '本帧区域未确认，或特殊区域/第六层尚无模板。'
        return base
    labels=[n for n in labels if not n.get('detail_panel_label')]
    points = _rings(image,labels)
    points = [p for p in points if not any(
        min(v[0] for v in t['box'])-.005 <= p['center'][0] <= max(v[0] for v in t['box'])+.005 and
        min(v[1] for v in t['box'])-.005 <= p['center'][1] <= max(v[1] for v in t['box'])+.005
        for t in texts if t['confidence']>=.7)]
    for label in labels:
        box = label['box']; x = float(np.mean([p[0] for p in box])); y = float(np.mean([p[1] for p in box]))
        height = max(p[1] for p in box)-min(p[1] for p in box)
        # Text labels sit below the icon; the exit title has a larger gap.
        y -= height * (3 if label['type']=='险路尽头' else 1.8)
        points.append({'center': [x, y], 'type': label['type'], 'source': '可见节点标签',
                       'confidence': label['confidence'], 'label_box': box})
    rows, cols = templates[0]['rows'], templates[0]['cols']
    axes = (_axis([p['center'][0] for p in points], cols), _axis([p['center'][1] for p in points], rows))
    if any(axis is None for axis in axes):
        base['status'] = 'insufficient'; base['reason'] = '无法从当前画面确认完整网格尺度。'
        return base
    (x0, dx), (y0, dy) = axes
    observed = {}
    for point in points:
        x, y = point['center']; col = round((x-x0)/dx); row = round((y-y0)/dy)
        if not (0<=row<rows and 0<=col<cols): continue
        if abs(x-x0-col*dx)>dx*.16 or abs(y-y0-row*dy)>dy*.16: continue
        key = f'{row},{col}'
        if key not in observed or 'type' in point: observed[key] = point
    scored = []
    for template in templates:
        cells = {n['id'] for n in template['nodes']}
        if not set(observed).issubset(cells): continue
        if any(p.get('type')=='险路尽头' and key not in template['ends'] for key,p in observed.items()): continue
        if any(p.get('type')=='险路恶敌' and key != template['boss'] for key,p in observed.items()): continue
        coverage = len(observed)/len(cells)
        if coverage >= .85: scored.append((coverage, template))
    scored.sort(key=lambda pair: (-pair[0], pair[1]['id']))
    base['candidate_templates'] = [{'id': t['id'], 'visible_fraction': score} for score, t in scored]
    base['grid'] = {'rows': rows, 'cols': cols, 'origin': [x0,y0], 'pitch': [dx,dy],
                    'coordinate_space': 'analysis_content_normalized'}
    if not scored:
        base['status'] = 'insufficient'; base['reason'] = '可见节点不足或与已收录模板冲突。'
        return base
    best = scored[0][0]
    # Missing nodes may be occluded, so a smaller layout's higher coverage
    # alone cannot rule out another compatible layout.
    tied = [t for _, t in scored]
    if len(tied) != 1:
        base['status'] = 'ambiguous'; base['reason'] = '多个布局同分，保留候选，不输出确定连线。'
        return base
    template = tied[0]
    base.update(status='matched', template_id=template['id'], edges=template['edges'],
        visible_fraction=best, reason='当前区域与网格节点占位匹配；连线取自来源模板。')
    for node in template['nodes']:
        evidence = observed.get(node['id'], {})
        clearing = evidence.get('source') == '可见空白圆环' and not evidence.get('type')
        base['nodes'].append({'id': node['id'], 'row': node['row'], 'col': node['col'],
            'center': [x0+node['col']*dx, y0+node['row']*dy], 'distance': node['distance'],
            'template_type': node['fixed_type'],
            # The matched layout establishes the node's position; the current
            # frame's small ring establishes its visible clearing appearance.
            # Neither a missing label nor a template slot proves a clearing.
            'observed_type': '林间空地' if clearing else evidence.get('type'),
            'observation_source': 'visible_clearing_ring' if clearing else
                'visible_node_label' if evidence.get('type') else None,
            'visible': bool(evidence), 'prediction': None})
    markers = [t for t in texts if t['text']=='YOUAREHERE' and t['confidence']>=.9]
    if not markers:
        heads=[t for t in texts if t['text'] in ('YOUAR','YOUARE') and t['confidence']>=.9]
        tails=[t for t in texts if t['text']=='HERE' and t['confidence']>=.9]
        for head in heads:
            for tail in tails:
                hx=max(p[0] for p in head['box']);tx=min(p[0] for p in tail['box'])
                hy=float(np.mean([p[1] for p in head['box']]));ty=float(np.mean([p[1] for p in tail['box']]))
                if abs(hy-ty)<.012 and -.01<tx-hx<.025:
                    points=head['box']+tail['box'];left=min(p[0] for p in points);right=max(p[0] for p in points)
                    top=min(p[1] for p in points);bottom=max(p[1] for p in points)
                    markers.append({'box':[[left,top],[right,top],[right,bottom],[left,bottom]]})
    if len(markers)==1:
        box = markers[0]['box']; x = float(np.mean([p[0] for p in box])); y = max(p[1] for p in box)
        below = [n for n in base['nodes'] if n['visible'] and abs(n['center'][0]-x)<dx*.18 and 0<n['center'][1]-y<dy*.5]
        if len(below)==1: base['current_node'] = below[0]['id']
    from .node_events import mark_selected_node
    mark_selected_node(image,base)
    return predict_map(base)
