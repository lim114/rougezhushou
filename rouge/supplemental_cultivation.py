"""Independent cultivation and recruitment scenarios, not account mutations."""
from copy import deepcopy
from .supplemental_run import run_skill_reference
from .supplemental_comparison import comparison_rows,format_comparison


def cultivation_defaults(operator_preview,environment):
    base={k:operator_preview[k] for k in ('elite','level','trust','potential')}
    kind=environment['operator_metadata'].get(operator_preview['operator'],{}).get('recruitment_kind')
    return {'proposals':[
        {'name':'当前培养及来源',**base,'recruitment_kind':kind},
        {'name':'精零培养方案',**base,'elite':0,'level':min(base['level'],40),'recruitment_kind':kind},
        {'name':'满潜能方案',**base,'potential':6,'recruitment_kind':kind},
        {'name':'应急助力来源方案',**base,'recruitment_kind':'emergency_hire'}]}


def compare_cultivation(operator_preview,environment,preview):
    required={'name','elite','level','trust','potential','recruitment_kind'}
    if type(preview) is not dict or set(preview)!={'proposals'}:
        raise ValueError('培养对照需要proposals列表。')
    proposals=preview['proposals']
    if type(proposals) is not list or not 1<=len(proposals)<=12:
        raise ValueError('需要1–12个培养方案。')
    names=set()
    for proposal in proposals:
        if type(proposal) is not dict or set(proposal)!=required:
            raise ValueError('每个方案需要name、elite、level、trust、potential、recruitment_kind。')
        name=proposal['name'];kind=proposal['recruitment_kind']
        if (type(name) is not str or not name.strip() or len(name)>80 or name in names or
            any(ord(c)<32 or 0xD800<=ord(c)<=0xDFFF for c in name)):
            raise ValueError('方案名需为唯一、非空的可显示短文本。')
        if kind is not None and (type(kind) is not str or kind not in ('non_emergency','emergency_hire')):
            raise ValueError('招募来源仅支持non_emergency、emergency_hire或null（未知）。')
        names.add(name)
    original=deepcopy(operator_preview);environment=deepcopy(environment)
    baseline=run_skill_reference(original,environment);rows=[];variants=[]
    for proposal in proposals:
        proposed={**original,**{k:proposal[k] for k in ('elite','level','trust','potential')}}
        env=deepcopy(environment)
        member=env['operator_metadata'].setdefault(original['operator'],{})
        member['recruitment_kind']=proposal['recruitment_kind']
        variant={'proposal':proposal['name'],'operator_preview':proposed,'environment':env,'result':None,'error':None}
        try:variant['result']=run_skill_reference(proposed,env)
        except (ValueError,TypeError,KeyError) as error:
            variant['error']=proposal['name']+'：'+str(error)
            rows.append({'proposal':proposal['name'],'key':'invalid','name':'方案不可测算',
                         'value':None,'base_value':None,'delta':None,'unit':'—'})
        else:rows.extend(comparison_rows(variant['result'],baseline,proposal=proposal['name']))
        variants.append(variant)
    return {'operator_preview':original,'environment':environment,'preview':deepcopy(preview),
            'baseline':baseline,'variants':variants,'rows':rows,
            'notes':['所有方案都是独立局外声明；不改写账户培养、已招募成员或领取者状态。',
                     '相同技能等级、目标和藏品条件下，每个方案重新读取成长、信赖、潜能、天赋门及适用选择器。',
                     '招募来源仅改变同行者等既有合格来源的条件；不模拟进阶、招募或应急消失事件。',
                     '差值相对打开时当前培养和来源；来源未知时仅列部分参考，不将遗漏增益标为完整面板。',
                     '精零高公共技能等级的实际使用资格仍未证明；无效方案逐行说明原因，不补零或排序未知。']}


format_cultivation_comparison=format_comparison
