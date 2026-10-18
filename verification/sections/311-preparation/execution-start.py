from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
import json, re, subprocess

ROOT = Path(__file__).resolve().parents[1]

def enc(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf8')

def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)

assert git('branch', '--show-current').decode().strip() == 'codex/p2-development'
assert git('rev-parse', 'HEAD').decode().strip() == '09f5ec9888342f03bbb8c8fd4b56c96e29e3d7a2'
assert not git('status', '--porcelain').strip()
origin = ROOT / '.cache/p3-311-boss-research'
raw = (origin / 'HANDOFF.json').read_bytes()
assert sha256(raw).hexdigest() == '43a21c4cf43b55546cf33bcb6b433a7cbdfc5b54713bee3a64dea7c1a28320d3'
handoff = json.loads(raw)
assert handoff['complete_skill_cards'] == 8 and handoff['complete_ability_cards'] == 3
destination = ROOT / 'research/p3-boss-hunt-311'
destination.mkdir()
out = ROOT / 'verification/sections/311-preparation'
out.mkdir()
pins = {}
for group in ('source_files', 'source_preparation_evidence'):
    for name, pin in handoff[group].items():
        content = (origin / name).read_bytes()
        assert sha256(content).hexdigest() == pin['sha256'] and len(content) == pin['bytes']
        target = destination / name
        assert target.resolve().is_relative_to(destination.resolve())
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        pins[target.relative_to(ROOT).as_posix()] = pin
(destination / 'HANDOFF.json').write_bytes(raw)
cp_path = ROOT / 'DEVELOPMENT_CHECKPOINT.json'
cp = json.loads(cp_path.read_bytes())
assert cp['completed_sections'] == 310 and cp['next_section'] == 311
cp['batch_start_section'] = 311
cp['batch_status'] = 'P3_SECTION311_IN_PROGRESS'
cp['current_batch'].update(start=311, end=cp['batch_target_section'], status=cp['batch_status'],
                           batch_closed=False, next_section_started=True)
cp['active_section'] = {'number': 311, 'completed': False,
    'remaining_todo': 'P3敌人面板与机制：未覆盖首领及其关联敌人的完整文献条件',
    'proposed_capability': '普通版永无安宁中的卡德霍、痛楚化身及猎犬proto完整招式、条件退场及版本差异阅读',
    'acceptance': [
        '仅三个严格普通版身份显示入口；痛苦将息与自定义2/3不借用普通版技能',
        '四主题覆盖击倒休整、分担与位移、痛楚退场及猎犬锁定；完整8技能与3能力及术语原文保留',
        '明确20/10秒、关卡生成/摘要召唤、全场敌方/旧图鉴、存疑波次差异；不恢复实际时序或数值',
        '同来源刷新保留主题页签选区滚动；换身份或来源失效清空、恢复后手动重开',
        '不修改本局、地图或数值模型；适当必要检查与实际Windows阅读、要求索引及远端核对后才计完成']}
cp['next_action'] = '第311节进行中：补齐永无安宁三主体的有条件机制说明。完成与发布之前已交付仍310。'
cp_path.write_bytes(enc(cp))
now = datetime.now(timezone.utc).isoformat()
wip = ROOT / 'WORK_IN_PROGRESS.md'
wip.write_text('## 当前进行第311节（尚未验收、发布）\n\n' + now +
    '。拟交付：普通版永无安宁的卡德霍、痛楚化身与猎犬proto招式、退场及来源版本差异，四组条件手动阅读。只认三个明确身份，不把存疑波次、技能冷却或关卡生成当本局时钟/召唤；不覆盖本局记忆。必要验证与实际发布前已交付仍310。\n\n以下为已交付历史。\n\n' + wip.read_text('utf8'), encoding='utf8')
(out / 'source-promotion.json').write_bytes(enc({'section': 311,
    'kind': 'source_only_before_implementation_not_acceptance', 'at_utc': now,
    'source_pins': pins, 'source_handoff_sha256': sha256(raw).hexdigest(),
    'root_reviewed_all_eleven_visible_skill_and_ability_cards_and_four_topic_paragraphs': True,
    'root_reviewed_normal_and_pursuit_full_reference_identity_and_custom_useDb_difference': True,
    'complete_public_revisions': ['436092', '441718', '436178', '427937', '428754'],
    'original_empty_tooltip_index_preserved_with_DOM_and_explicit_amended_index': True,
    'actual_game_state_clock_damage_or_server_verified': False,
    'private_game_or_chat_used': False}))
(out / 'usage-threshold.json').write_bytes(enc({'section': 311,
    'source': 'actual get_usage_limits response observed in this root turn before section start',
    'recorded_at_utc': now, 'window_duration_minutes': 10080, 'used_percent': 15,
    'remaining_percent': 85, 'threshold_remaining_percent': 15,
    'strict_below15_triggered': False, 'unavailable_secondary_window_inferred': False,
    'account_identifiers_or_full_response_saved': False}))
(out / 'execution-start.py').write_bytes(Path(__file__).read_bytes())
print(json.dumps({'started': 311, 'still_completed': 310, 'frozen_public_members': len(pins),
                  'source_scope': handoff['targets']}, ensure_ascii=False))
