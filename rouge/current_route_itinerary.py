"""Every fixed route, in original checkpoint order, without runtime selection."""
from copy import deepcopy
from hashlib import sha256
import json,math
from . import current_battle_reference as battle
from .battle_preview import display_cell
PACK='research/p3-current-route-itinerary-375'
MANIFEST=PACK+'/runtime-manifest.json'
MANIFEST_SHA256='76e93128f74926d3f7a52ec20c38f1fceafac9f8e87429b2cf2954246924d462'
SCOPES=((None,'总览（全部原路线）'),('base','基础路线'),('extra','额外候选路线'))
TYPES={'START':'出生声明','END':'终点声明','MOVE':'移动目标','WAIT_FOR_SECONDS':'停留等待','WAIT_CURRENT_FRAGMENT_TIME':'本组计时等待','DISAPPEAR':'消失','APPEAR_AT_POS':'再出现'}
NOTICE='逐条阅读固定路线的完整先后顺序，不拼接成实际敌人路径。条件分支究竟采用基础还是额外路线尚未确认；对应关系未证的出怪记录单独列出。'
UNAVAILABLE='本关完整路线资料无法核对；旧行程、出怪跳转及地图已清除，资料恢复后请重新选择。'
def same(a,b):
    if type(a)is not type(b):return False
    if type(a)is dict:return a.keys()==b.keys()and all(same(a[k],b[k])for k in a)
    if type(a)in(list,tuple):return len(a)==len(b)and all(same(x,y)for x,y in zip(a,b))
    return a==b
def packet():
    try:
        raw=battle.version._file(MANIFEST).read_bytes()
        if sha256(raw).hexdigest()!=MANIFEST_SHA256:return None
        m=json.loads(raw)
        if m['schema']!='current_route_itinerary_375_manifest_v1'or set(m['files'])!={PACK+'/scope-inventory.json',PACK+'/source-notes.json'}:return None
        objects={}
        for name,pin in m['files'].items():
            body=battle.version._file(name).read_bytes()
            if type(pin['bytes'])is not int or len(body)!=pin['bytes']or sha256(body).hexdigest()!=pin['sha256']:return None
            objects[name]=json.loads(body)
        return{'inventory':objects[PACK+'/scope-inventory.json'],'notes':objects[PACK+'/source-notes.json'],'identity':MANIFEST_SHA256}
    except(OSError,ValueError,KeyError,TypeError):return None
def _derive(current,source_identity):
    level=current['level'];grid=level['mapData']['map'];rows=len(grid);cols=len(grid[0]);entries=[];bound=set();unassigned=[]
    for scope,field in(('base','routes'),('extra','extraRoutes')):
        for i,raw in enumerate(level.get(field)or[]):
            key=f'$.{field}[{i}]';motion=raw.get('motionMode');steps=[]
            def add(kind,value,selector):
                pos=value.get('position');spatial=kind in('START','END','MOVE','APPEAR_AT_POS')and motion in('WALK','FLY');cell=display_cell(pos,rows,cols)if spatial else None
                steps.append({'key':str(len(steps)),'kind':kind,'name':TYPES.get(kind,'未核实类型'),'raw':deepcopy(value),'source_selector':selector,'cell':cell,'spatial_reference_permitted':cell is not None,'actual_time':None,'actual_position':None})
            add('START',{'position':raw.get('startPosition'),'spawnOffset':raw.get('spawnOffset'),'spawnRandomRange':raw.get('spawnRandomRange')},key+'.startPosition')
            for j,point in enumerate(raw.get('checkpoints')or[]):add(point.get('type'),point,key+f'.checkpoints[{j}]')
            add('END',{'position':raw.get('endPosition')},key+'.endPosition')
            actions=[deepcopy(a)for a in current['actions']if scope=='base'and a['queue']['kind']=='main'and a['raw'].get('actionType')=='SPAWN'and type(a['raw'].get('routeIndex'))is int and a['raw']['routeIndex']==i]
            bound.update(a['key']for a in actions);names=list(dict.fromkeys(e['name']for a in actions for e in a['enemy_candidates']))
            entries.append({'key':key,'scope':scope,'ordinal':i+1,'label':('基础路线'if scope=='base'else'额外候选路线')+str(i+1),'raw':deepcopy(raw),'motion_mode':motion,'steps':steps,'actions':actions,'enemy_names':names,'actual_selection':None,'actual_count':None,'actual_path':None,'absolute_time':None})
    for a in current['actions']:
        if a['raw'].get('actionType')=='SPAWN'and a['key']not in bound:
            unassigned.append({'action':deepcopy(a),'reason':'条件分支采用哪组路线尚未确认'if a['queue']['kind']=='branch'else'基础路线编号无效或未取得','actual_route':None})
    return{'stage_id':current['id'],'stage_name':current['name'],'entries':entries,'unassigned_actions':unassigned,'level_key':current['level_key'],'original_level_source':deepcopy(current['source']),'battle_source_identity':current['source_identity'],'source_identity':(source_identity,current['source_identity']),'actual_path':None,'absolute_time':None,'actual_server_verified':False,'run_updated':False}
def stage_reference(stage_id):
    if type(stage_id)is not str:return None
    current=battle.stage_reference(stage_id);ref=packet()
    if current is None or ref is None or ref['inventory']['battle_identity']!=current['source_identity']:return None
    selected=ref['inventory']['stages'].get(stage_id)
    if selected is None or selected['level_key']!=current['level_key']or selected['original_source']!=current['source']:return None
    try:return _derive(current,ref['identity'])
    except(ValueError,KeyError,TypeError,IndexError):return None
def routes(result,query='',scope=None):
    if type(result)is not dict or type(query)is not str or scope not in dict(SCOPES):return[]
    q=query.strip().casefold()
    return[deepcopy(r)for r in result['entries']if(scope is None or r['scope']==scope)and(not q or q in(r['label']+' '+' '.join(r['enemy_names'])).casefold())]
def resolve(result,route_key=None,step_key=None,action_key=None):
    if type(result)is not dict or any(v is not None and type(v)is not str for v in(route_key,step_key,action_key)):return None
    fresh=stage_reference(result.get('stage_id'))
    if fresh is None or not same(fresh,result):return None
    route=next((r for r in fresh['entries']if r['key']==route_key),None)if route_key is not None else None
    if route_key is not None and route is None:return None
    step=next((s for s in route['steps']if s['key']==step_key),None)if route is not None and step_key is not None else None
    if step_key is not None and step is None:return None
    actions=route['actions']if route is not None else[a['action']for a in fresh['unassigned_actions']]
    action=next((a for a in actions if a['key']==action_key),None)if action_key is not None else None
    if action_key is not None and action is None:return None
    if route is None and action is None:return None
    return{'reference':fresh,'route':deepcopy(route),'step':deepcopy(step),'action':deepcopy(action),'actual_route':None,'run_updated':False}
def position_reference(result,route_key,step_key):
    selected=resolve(result,route_key,step_key)
    if selected is None or selected['step']is None or not selected['step']['spatial_reference_permitted']:return None
    from . import current_map_position as positions
    grid=positions.stage_reference(result['stage_id'])
    if grid is None or grid['current_level_key']!=result['level_key']:return None
    cell=selected['step']['cell'];point=positions.cell_reference(grid,**cell)
    if point is None:return None
    return{'stage_id':result['stage_id'],'route':selected['route'],'step':selected['step'],'cell':cell,'center':deepcopy(point['point']),'grid':grid,'source_identity':(result['source_identity'],grid['source_identity']),'actual_time':None,'actual_position':None,'actual_path':None,'run_updated':False}
def step_label(step):
    text=('第'+str(int(step['key']))+'处：'if step['kind']not in('START','END')else'')+step['name'];cell=step['cell']
    if cell is not None:text+=f" · 第{cell['row']+1}行第{cell['col']+1}列"
    if step['kind']in('WAIT_FOR_SECONDS','WAIT_CURRENT_FRAGMENT_TIME'):text+=' · 参数'+battle.number(step['raw'].get('time'))+'秒'
    return text
def player_text(result,route=None,step=None,action=None,unassigned=False):
    lines=[result['stage_name'],'','【完整行程资料】',f"本关保留{len(result['entries'])}条原路线；不是实际采用条数。",'基础路线与额外候选路线分开查看，同名关卡的不同配置不互借。']
    if route is not None:
        lines+=['',route['label'],'资料中的行动方式：'+{'WALK':'地面移动','FLY':'飞行移动'}.get(route['motion_mode'],'未取得明确移动方式；占位位置不标图。'),'','【原行程先后顺序】']
        for point in route['steps']:lines.append(step_label(point))
        if route['scope']=='extra':lines+=['额外路线可以独立阅读原顺序，但未证明具体由哪条条件分支采用；没有按相同编号借用出怪记录。']
        elif not route['actions']:lines+=['没有找到准确引用这条基础路线的主波次出怪记录；不据此断言不会被其它脚本采用。']
    if step is not None:
        lines+=['','【所选环节】',step_label(step)]
        if step['kind']=='WAIT_FOR_SECONDS':lines+=['这是该处停留的等待参数，不是开场后的时刻；是否实际经过和何时到达仍待核对。']
        elif step['kind']=='WAIT_CURRENT_FRAGMENT_TIME':lines+=['这是本组计时的等待参数，不能与路程耗时或其它等待直接相加；实际计时起点和放行时刻尚未核对。']
        elif step['kind']=='DISAPPEAR':lines+=['这里声明消失。原记录中的占位坐标不画到地图，也不跨过此处连成实际移动路线。']
        elif step['kind']=='APPEAR_AT_POS':lines+=['这里声明再出现的名义格，不证明实际传送配对、出现时刻或偏移后的脚点。']
        if step['cell']is not None:lines+=['这里只查看这一处名义格；出生偏移、随机范围、到达偏移和实际寻路没有加入。']
    if action is not None:
        if unassigned:lines+=['','【路线尚未确认的出怪】','可以返回这条出怪条件，但没有把它归到任何基础或额外路线。']
        lines+=['',*battle.action_text(action).splitlines()]
    lines+=['','【重要边界】','移动、停留、消失和再出现按原顺序列出；不按直线连接格子，不累计为全局出怪时间，不推实际走位、触发、次数或概率。','等待和消失的占位位置不标图；没有明确移动方式的路线仍可查原记录，但位置不作准入。','只有主波次直接出怪的明确基础路线引用才提供绑定入口。其余出怪单列，当前服务器实际执行仍未知。']
    return'\n'.join(lines)
