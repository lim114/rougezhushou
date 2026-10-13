"""Build only frozen table facts; documented layering is attributed separately."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMMIT = 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add'
HASHES = {'character_table': '68e3a3b5ee0d407ce234afaa5867c6fda6379a6843c7d5317a7bbda4779f8697',
          'skill_table': '86f4aa64c785f39727edd06d6dd8a4f27f371c8e4ace5345ba0dc61dee1386ca'}


def build():
    tables = {}; sources = {}
    for name, expected in HASHES.items():
        raw = (ROOT / '.cache' / 'game-data' / (name + '.json')).read_bytes()
        actual = hashlib.sha256(raw).hexdigest()
        if actual != expected:
            raise ValueError('Fixed primary table bytes differ: ' + name)
        tables[name] = json.loads(raw)
        sources[name] = {'sha256': actual,
            'url': f'https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/{COMMIT}/zh_CN/gamedata/excel/{name}.json'}
    character = tables['character_table']; skills = tables['skill_table']
    if character['char_2023_ling']['skills'][2]['overrideTokenKey'] != 'token_10020_ling_soul3':
        raise ValueError('Owner-token identity changed.')
    token_id = character['token_10020_ling_soul3']['skills'][0]['skillId']
    raw_levels = skills[token_id]['levels']
    boards = [{v['key']: v['value'] for v in level['blackboard']} for level in raw_levels]
    if not boards or any(b != boards[0] for b in boards):
        raise ValueError('Passive form coefficients differ across levels; do not select by guess.')
    names = {'hp': '2.max_hp', 'attack': '2.atk', 'defense': '2.def',
             'resistance': '2.magic_resistance', 'base_interval': '2.base_attack_time', 'block': '2.block_cnt'}
    result = {'schema_version': 1, 'source_commit': COMMIT,
        'token_id': 'token_10020_ling_soul3', 'owner_skill_id': 'skchr_ling_3',
        'token_skill_id': token_id, 'all_token_skill_levels_equal': True,
        'merged_additions': {field: boards[0][key] for field, key in names.items()},
        'owner_skill_levels': [
            {'rank': i + 1, 'attack': next(b['value'] for b in level['blackboard'] if b['key'] == 'atk'),
             'defense': next(b['value'] for b in level['blackboard'] if b['key'] == 'def')}
            for i, level in enumerate(skills['skchr_ling_3']['levels'])],
        'sources': sources,
        'documentation': [
            {'url': 'https://prts.wiki/w/%E2%80%9C%E5%BC%A6%E6%83%8A%E2%80%9D',
             'checked_date': '2026-10-14', 'role': 'community mechanics documentation, separate from native proof',
             'facts': ['高级形态参数按对应属性直接加算/乘算；高级形态普攻为法术，占用两部署位。',
                       '模式切换与阻挡重判属于实际生命周期，未由本算式验证。']},
            {'url': 'https://prts.wiki/w/Ling', 'checked_date': '2026-10-14',
             'role': 'community same-layer clarification',
             'facts': ['技能攻击/防御百分比与高级形态同层累加，不做两个倍率的叠乘。']}],
        'limitations': ['This is documented formula arithmetic, not native fusion/attachment proof.',
                        'Token cultivation endpoints and equipment additions reuse their frozen reference.',
                        'No relic/squad combination, actual current panel, skill clocks or complete damage claim.']}
    return result


if __name__ == '__main__':
    (ROOT / 'rouge/data/ling-fusion-source.json').write_bytes(
        (json.dumps(build(), ensure_ascii=False, indent=2) + '\n').encode('utf-8'))
