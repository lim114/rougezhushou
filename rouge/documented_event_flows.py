"""Current documented event choices; never infer server parents or eligibility."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path, PurePosixPath
import json
from . import expansion_reference as version

ROOT = Path(__file__).resolve().parents[1]
PACK = 'research/p3-document-flows-321'
DATA = 'rouge/data/documented-event-flows.json'
MANIFEST = PACK + '/runtime-manifest.json'
MANIFEST_SHA256 = '235fc375dfc1bcb8900a4aabcafa686ca69be7c0cde4ce1f6f2a85582a59a8a7'
UNAVAILABLE = '这份事件流程暂时无法核对，旧情景、选项和作战入口已清除；恢复后请重新选择。'


def packet():
    try:
        raw = (ROOT/MANIFEST).read_bytes()
        if sha256(raw).hexdigest() != MANIFEST_SHA256: return None
        manifest = json.loads(raw)
        expected = {DATA, PACK+'/source-receipt.json', PACK+'/documented-tables.html',
                    'research/p3-expansion-313/current-topic.json'}
        if (manifest['schema'] != 'documented_event_flows_321_manifest_v1'
                or manifest['game_commit'] != version.NEW_COMMIT or set(manifest['files']) != expected): return None
        values = {}
        for name, pin in manifest['files'].items():
            rel = PurePosixPath(name)
            if rel.is_absolute() or '..' in rel.parts or '\\' in name or ':' in name: return None
            path = ROOT.joinpath(*rel.parts)
            if path.is_symlink() or not path.resolve().is_relative_to(ROOT.resolve()): return None
            for parent in path.parents:
                if parent == ROOT: break
                if parent.is_symlink(): return None
            content = path.read_bytes()
            if len(content) != pin['bytes'] or sha256(content).hexdigest() != pin['sha256']: return None
            values[name] = content
        data = json.loads(values[DATA]); current = version.packet()
        if current is None or data['schema'] != 'documented_event_flows_321_v1': return None
        primary = current['current']['details']
        for group, table in [('choices', 'choices'), ('scenes', 'choiceScenes'), ('items', 'items'), ('stages', 'stages')]:
            if any(primary[table].get(k) != record for k, record in data['originals'][group].items()): return None
        return {'data': data, 'source_identity': (MANIFEST_SHA256, current['source_identity']),
                'actual_eligible': None, 'actual_choice': None, 'actual_received': None,
                'actual_game_parent_script_restored': False, 'run_updated': False}
    except (OSError, ValueError, KeyError, TypeError, UnicodeError, AttributeError, RecursionError):
        return None


def reference(event_id):
    if type(event_id) is not str: return None
    ref = packet()
    if ref is None: return None
    event = next((e for e in ref['data']['events'] if e['id'] == event_id), None)
    if event is None: return None
    data = ref['data']
    return {**ref, 'event': deepcopy(event),
            'scenes': {k: deepcopy(data['scenes'][k]) for k in event['scene_ids']},
            'choices': {k: deepcopy(data['choices'][k]) for k in event['choice_ids']}}


def event_for_scene(scene_id):
    if type(scene_id) is not str: return None
    ref = packet()
    row = ref['data']['scenes'].get(scene_id) if ref else None
    return row['event_id'] if row else None


def scene_label(result, scene_id):
    if scene_id == result['event']['entry_scene_id']: return '最初情景 · ' + result['event']['title']
    parents = [result['data']['originals']['choices'][c['id']]['title'] for c in result['choices'].values()
               if c['next_scene_id'] == scene_id]
    return '选择“' + ' / '.join(parents) + '”之后'


def choice_reference(result, scene_id, choice_id):
    if type(scene_id) is not str or type(choice_id) is not str: return None
    scene = result['scenes'].get(scene_id)
    choice = result['choices'].get(choice_id)
    if scene is None or choice is None or choice_id not in scene['choice_ids'] or choice['scene_id'] != scene_id: return None
    return deepcopy(choice)


def player_text(result, scene_id, choice_id=None):
    scene = result['scenes'].get(scene_id)
    if scene is None: return '请选择情景。这里只查看固定资料，不表示游戏当前已经进行到这一步。'
    originals = result['data']['originals']; original_scene = originals['scenes'][scene_id]
    lines = ['【正在查阅】' + result['event']['title'], scene_label(result, scene_id),
             '', '【当前情景】', version._plain(original_scene['description'])]
    choice = choice_reference(result, scene_id, choice_id)
    if choice is None:
        lines += ['', '本情景的文献列出' + str(len(scene['choice_ids'])) + '个选项。' if scene['choice_ids']
                  else '文献未为这个后续情景列出专属选项；不补入其它同名情景的选项。']
    else:
        original = originals['choices'][choice_id]
        lines += ['', '【查看的选项】' + version._plain(original['title']),
                  '【选项写明的结果】', version._plain(original.get('description')) or '没有独立的结果说明。']
        if choice['item_id'] is not None:
            item = originals['items'][choice['item_id']]
            lines += ['', '【关联收藏品】' + item['name'], version._plain(item.get('usage')),
                      '这是资料中的关联，不代表已经领取或生效。']
        if choice_id == 'choice_ro6_revive_1':
            lines += ['一半生命上限的整数处理尚未核验，这里不替你计算或扣除生命上限。']
        if choice_id == 'choice_ro6_end5_1':
            lines += ['原文写明1件珍贵收藏品；具体物品及完整随机池仍未知。']
        if choice['next_scene_id'] is not None:
            lines += ['', '【资料中的后续情景】', scene_label(result, choice['next_scene_id']),
                      '可点击下方按钮继续查阅；不会替你在游戏中选择。']
        elif choice['stage_ids']:
            lines += ['', '【明确关联的作战】', *[originals['stages'][sid]['name'] for sid in choice['stage_ids']],
                      '可打开固定地图、敌人及出怪资料；不会进入游戏战斗。']
        else:
            lines += ['', '原记录没有指向另一情景；不据此推断本局后续状态或奖励。']
    lines += ['', '【范围与未知】',
              '当前资料为10月16日更新版本，流程来自调查记录的三张固定事件表，并逐项对照游戏文本。',
              '完整出现前置、隐藏选项及当前是否可选仍未全部核验；这里只列文献所载分支。',
              '不会扣除资源、记录领取、改变本局记忆或给出路线建议。']
    return '\n'.join(lines)
