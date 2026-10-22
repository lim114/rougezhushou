"""Source-checked exit choices; declared reading conditions never update a run."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path,PurePosixPath
import json
from . import expansion_reference as version
ROOT=Path(__file__).resolve().parents[1];PACK='research/p3-current-exit-339';DATA='rouge/data/current-exit.json';MANIFEST=PACK+'/runtime-manifest.json'
MANIFEST_SHA256='756980d08c5828cde691823eb6a89c57a3df626c1b8d3fc6a095a030e8c6e987'
UNAVAILABLE='险路尽头的完整资料暂时无法核对，旧对话和结果入口已清除；恢复后请重新选择。'

def packet():
    try:
        raw=(ROOT/MANIFEST).read_bytes()
        if sha256(raw).hexdigest()!=MANIFEST_SHA256:return None
        m=json.loads(raw);expected={DATA,PACK+'/source-receipt.json',PACK+'/documented-section.html',PACK+'/source-notes.json','research/p3-expansion-313/current-topic.json','research/p3-expansion-313/baseline-topic.json','rouge/data/node-catalog.json'}
        if m['schema']!='current_exit_339_manifest_v1'or m['game_commit']!=version.NEW_COMMIT or set(m['files'])!=expected:return None
        values={}
        for name,pin in m['files'].items():
            rel=PurePosixPath(name)
            if rel.is_absolute()or'..'in rel.parts or'\\'in name or':'in name:return None
            path=ROOT.joinpath(*rel.parts)
            if path.is_symlink()or not path.resolve().is_relative_to(ROOT.resolve()):return None
            for parent in path.parents:
                if parent==ROOT:break
                if parent.is_symlink():return None
            content=path.read_bytes()
            if len(content)!=pin['bytes']or sha256(content).hexdigest()!=pin['sha256']:return None
            values[name]=content
        data=json.loads(values[DATA]);current=version.packet()
        if current is None or data['schema']!='current_exit_339_v1':return None
        for group,table in(('choices','choices'),('scenes','choiceScenes'),('items','items'),('stages','stages')):
            if any(current['current']['details'][table].get(k)!=v for k,v in data['originals'][group].items()):return None
        if data['difficulty16']not in current['current']['details']['difficulties']:return None
        return {'data':data,'source_identity':(MANIFEST_SHA256,current['source_identity']),'actual_eligible':None,'actual_entered':None,'run_updated':False}
    except(OSError,ValueError,KeyError,TypeError,UnicodeError,AttributeError,RecursionError):return None

def _targets(data, category, key):
    if category == 'scenes': return [(sid, None) for sid, s in data['scenes'].items() if s['raw_scene_id'] == key]
    if category == 'choices': return [(c['scene_id'], cid) for cid, c in data['choices'].items() if key in c['variant_ids']]
    if category == 'relics' and key == 'rogue_6_relic_final_7':
        return [(c['scene_id'], cid) for cid, c in data['choices'].items() if c['role'] == 'help']
    return []

def reference(event_id='exit', action_points=None, gold=None, difficulty=None, source_request=None):
    if type(event_id) is not str or event_id != 'exit': return None
    if any(v is not None and (type(v) is not int or v < 0) for v in (action_points, gold)): return None
    if difficulty is not None and (type(difficulty) is not int or not 0 <= difficulty <= 16): return None
    p = packet()
    if p is None: return None
    d = p['data']; targets = []
    if source_request is not None:
        if type(source_request) is not dict or set(source_request) != {'category', 'key'}: return None
        cat, key = source_request['category'], source_request['key']
        if type(cat) is not str or type(key) is not str: return None
        targets = _targets(d, cat, key)
        if not targets: return None
    return {**p, 'event': deepcopy(d['event']), 'scenes': deepcopy(d['scenes']), 'choices': deepcopy(d['choices']),
            'declared': {'action_points': action_points, 'gold': gold, 'difficulty': difficulty},
            'source_request': deepcopy(source_request), 'source_targets': targets,
            'actual_received': None, 'actual_consumed': None, 'actual_transition': None, 'actual_recruited': None}

def locate(category, key):
    if type(category) is not str or type(key) is not str: return None
    p = packet()
    if p is None or not _targets(p['data'], category, key): return None
    return {'event_id': 'exit', 'source_request': {'category': category, 'key': key}}

def scene_label(result, sid):
    s = result['scenes'].get(sid)
    if s is None: return '请选择查阅位置'
    if s['kind'] == 'original_followup_only':
        cid = s['choice_ids'][0]; number = '一' if result['data']['originals']['choices'][cid]['type'] == 'NEXT' else '二'
        return '未写加工品的原选项对照'+number+' · 前置未知'
    if sid == 'document:exit-repeat-result': return '分支1.2后的对话 · 本表结束'
    if sid == result['event']['entry_scene_id']: return '最初对话 · 险路尽头'
    titles = {'scene_ro6_final1_1': '招募后的对话 · 本表未列后续', 'scene_ro6_final1_2': '离开后的对话',
              'scene_ro6_final1_3': '说服同伴后的文献分支', 'scene_ro6_final1_4': '援助探险家后的对话'}
    return titles[sid]

def choice_reference(result, sid, cid):
    if type(sid) is not str or type(cid) is not str: return None
    c = result['choices'].get(cid); s = result['scenes'].get(sid)
    if c is None or s is None or c['scene_id'] != sid or cid not in s['choice_ids']: return None
    row = deepcopy(c); v = result['declared']; match = None
    if c['role'] == 'help': match = None if v['gold'] is None else v['gold'] >= 10
    if c['role'] == 'persuade_part' and v['difficulty'] == 16: match = False
    row['listed_condition_match'] = match
    row['equal_conversion_reference'] = v['action_points'] if c['role'] in ('persuade_part', 'persuade_no_part', 'confirm') else None
    row['base_exit_processed_part_reference'] = (None if v['difficulty'] is None else 0 if v['difficulty'] == 16 else 1) if c['role'] == 'persuade_part' else None
    row['actual_received'] = None; return row

def player_text(result, sid, cid=None):
    lines = ['【正在查阅】险路尽头', '仅作常规模式固定资料对照；不代表本局已经到达、支付、领取或换层。']
    if result['source_request']:
        lines += ['', '【打开来源】从原始条目或谒日之祈说明打开，保留准确原件。']
        if len(result['source_targets']) > 1: lines += ['这份原件在文献里对应不止一处位置；请在上方选择，不替你判定本局阶段。']
    s = result['scenes'].get(sid)
    if s is None: return '\n'.join(lines + ['', '请选择要查阅的文献位置；两次相同对话分别保留。'])
    lines += ['', '【文献位置】'+scene_label(result, sid)]
    if s['raw_scene_id']:
        lines += ['', '【当前对话】', version._plain(result['data']['originals']['scenes'][s['raw_scene_id']]['description'])]
    else: lines += ['', '这份原选项明确指向本事件的后续对话，但前置情景没有文献证据；不把它接在初始菜单上。']
    c = choice_reference(result, sid, cid)
    if c:
        role = c['role']; lines += ['', '【查看的选项】'+c['title'], version._plain(c['description'])]
        if role in ('persuade_part', 'persuade_no_part', 'confirm'):
            amount = c['equal_conversion_reference']
            lines += ['', '【行动力与希望】', '结算前行动力未确认，等量希望暂不填数值。' if amount is None else '按本页填写的结算前行动力，等量希望为'+str(amount)+'。']
            lines += ['这里只对照等量规则，不计算本局最终希望或上限修正；不把取得加工品与后续确认当成两次希望奖励相加。']
        if role == 'persuade_part':
            count = c['base_exit_processed_part_reference']
            lines += ['', '【加工品与难度】', '保密等级未确认：原文的1件只作普通分支参考，不能直接当本局奖励。' if count is None else '常规模式保密等级16：本节点不再获得加工品；上方旧分支原文仍保留，不能据此预测获得1件。' if count == 0 else '按本页常规模式难度，资料基础奖励为1件加工品；具体成员与额外奖励修正未知。', '保密等级16的规则已由完整难度原件与主题资料核对；不据此替你挑选同文案原件或推断隐藏选项。']
        elif role == 'persuade_no_part':
            lines += ['', '【原件覆盖范围】这份原文没有写加工品奖励。', '仅保留明确的后续对话；不能只凭保密等级决定这两份原件中的哪份在本局出现，也不补原菜单或实际加工品数量。']
        elif role == 'confirm': lines += ['', '【换层确认】原件未写下一段对话；本表也没有证明具体下一层地图。只查阅，不实际移动。']
        elif role == 'recruit':
            lines += ['', '【留存招募券】此选项用于取出留存券招募。', '原文未列当前券库存、招募费用、干员与培养结果；不能显示免费招募或已获得干员。主题资料提示取出时会重新判定随机效果，取出的券不能再次存入。', '不要把招募后的文献对话当成已经换层或已经领取加工品。']
        elif role == 'help':
            item = result['data']['originals']['items']['rogue_6_relic_final_7']
            lines += ['', '【本分支代价】10源石锭', '【具名物品提示】'+item['name'], version._plain(item['usage']), '完整原选项和物品均已核对。没有独立件数，不补成1件；实际资格、发放及具体余径配置仍未知。',
                      '【仅本页源石锭对照】'+('未确认。' if c['listed_condition_match'] is None else '满足已列10源石锭条件，完整资格仍未知。' if c['listed_condition_match'] else '不足10源石锭；其它分支不受影响。')]
        else: lines += ['', '【离开】只查看离开后的对话，不进行换层。']
        if len(c['variant_ids']) > 1:
            lines += ['', '【同文案原件】完整保留两份不同原件，生命上限提示字段不同；实际选择与生命上限触发条件/数值仍未知，不额外加生命上限。']
        if c['next_scene_id']: lines += ['', '【文献后续】'+scene_label(result, c['next_scene_id']), '只翻阅这次明确的后续，不执行选项。']
    elif s['choice_ids']: lines += ['', '请选择本位置的选项；只列资料支持的分支，不表示全部都能在本局选择。']
    else: lines += ['', '本表没有列出本处之后的更多选项，不自动返回或循环领奖。']
    lines += ['', '【资料状态与未知】原页仍标“调查中”。编号缺少的选项三不补造；完整服务器资格、原件选择、加工品池和实际结算仍未知。',
              '本页填写值只供查阅，不读取或修改本局库存、资源、地图和计算，不提供路线建议或概率。']
    return '\n'.join(lines)

def catalogue_binding(record):
    if type(record) is not dict or record.get('id') != 'community_group_033': return None
    from .current_node_readers import same
    from . import node_catalog
    r = reference()
    if r is None: return None
    row = r['data']['catalogue_binding']
    if any(k not in record or not same(record[k], v) for k, v in row['expected_summary'].items()): return None
    if 'scenes' in record and not same(record['scenes'], row['expected_legacy_event']['scenes']): return None
    if not same(node_catalog._event(record['id']), row['expected_legacy_event']): return None
    return {**deepcopy(row), 'legacy_event_id': record['id'], 'title': '险路尽头', 'reader': 'exit339',
            'current_event': deepcopy(r['event']), 'current_original_scenes': deepcopy(r['data']['originals']['scenes']),
            'current_source_identity': json.loads(json.dumps(r['source_identity'])),
            'source_identity': (MANIFEST_SHA256, json.loads(json.dumps(r['source_identity']))), 'reference_only': True,
            'actual_node_version_confirmed': False, 'actual_scene': None, 'actual_choice': None, 'run_updated': False}
