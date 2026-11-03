"""Nominal local spawn offsets. No global clock, live state or RNG inference."""
import math
from decimal import Decimal

def finite_nonnegative(value):
    if not isinstance(value,(int,float)) or isinstance(value,bool):return False
    try:return math.isfinite(value) and value>=0
    except OverflowError:return False

def local_sequence(row,limit=256):
    """Anchor is after the fragment/phase pre-delay, at action-queue start."""
    action=row['action'];count=action.get('count');delay=action.get('preDelay');interval=action.get('interval')
    if isinstance(limit,bool) or not isinstance(limit,int) or not 0<=limit<=4096:
        raise ValueError('序列展示上限需要0–4096的整数。')
    result={'anchor':'branch_phase_action_queue_start' if row.get('branch') else 'fragment_action_queue_start',
        'count':count,'occurrences':[],'first_offset':None,'last_offset':None,
        'global_times_verified':False,'visible_entry_times_verified':False,'frame_execution_verified':False,
        'conditional':bool(row.get('branch') or action.get('hiddenGroup') or
            action.get('randomSpawnGroupKey') or action.get('randomSpawnGroupPackKey')),
        'truncated':False,'pending':[]}
    if isinstance(count,bool) or not isinstance(count,int) or count<0 or count>1000000:
        result['pending'].append('条目count缺失/无效，不推定为1。');return result
    if not finite_nonnegative(delay) or not finite_nonnegative(interval):
        result['pending'].append('条目延迟/间隔缺失或无效，不推定为0。');return result
    if count==0:return result
    delay=Decimal(str(delay));interval=Decimal(str(interval))
    last=delay+(count-1)*interval
    try:
        first=float(delay);end=float(last)
    except (OverflowError,ValueError):
        result['pending'].append('生成偏移超出有限数值范围。');return result
    if not math.isfinite(first) or not math.isfinite(end):
        result['pending'].append('生成偏移超出有限数值范围。');return result
    result.update(first_offset=first,last_offset=end,truncated=count>limit)
    result['occurrences']=[{'ordinal':i+1,'offset_seconds':float(delay+i*interval)} for i in range(min(count,limit))]
    return result

def ordinal_offset(row,ordinal):
    result=local_sequence(row,limit=0)
    if result['pending']:return None
    if isinstance(ordinal,bool) or not isinstance(ordinal,int) or not 1<=ordinal<=result['count']:return None
    a=row['action'];value=float(Decimal(str(a['preDelay']))+(ordinal-1)*Decimal(str(a['interval'])))
    return value if math.isfinite(value) else None

def movement_reference(stage,base_speed):
    multiplier=stage.get('movement_multiplier')
    result={'base_attribute':base_speed,'stage_multiplier':multiplier,
        'base_times_stage_speed':None,'complete_effective_speed_verified':False}
    if finite_nonnegative(base_speed) and finite_nonnegative(multiplier):
        speed=base_speed*multiplier
        if finite_nonnegative(speed):result['base_times_stage_speed']=speed
    return result

def sequence_text(row):
    seq=local_sequence(row,limit=32)
    anchor='所选分支阶段动作队列开始' if row.get('branch') else '本波本片段动作队列开始'
    lines=['局部生成计划（以'+anchor+'为0秒）：']
    if seq['pending']:return '\n'.join(lines+[s.replace('条目count','条目生成数量') for s in seq['pending']])
    if not seq['count']:return '\n'.join(lines+['本条目生成数量为0，无计划生成项。'])
    def seconds(value):return f'{value:.9f}'.rstrip('0').rstrip('.')
    for start in range(0,len(seq['occurrences']),4):
        lines.append('；'.join('第'+str(o['ordinal'])+'次 +'+seconds(o['offset_seconds'])+'秒'
            for o in seq['occurrences'][start:start+4]))
    if seq['truncated']:lines.append('仅展示前32次；最后一次 +'+seconds(seq['last_offset'])+'秒。')
    lines.append('锚点已在片段/阶段开始前延迟之后；不重复加此前延迟，不跨片段使用同一个0秒。')
    lines.append('名义偏移不是开局绝对时刻；帧执行、生成回调和可见入场延迟尚未校准。')
    if seq['conditional']:lines.append('此条目含条件或随机候选；序列仅在该条目实际启用/入选时适用。')
    return '\n'.join(lines)
