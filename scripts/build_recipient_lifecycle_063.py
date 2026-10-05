"""Export only evidenced recipient triggers; these do not assign a recipient."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / '.cache/game-data/roguelike_topic_table.json'
EXPECTED = 'f5867e55d09472253083486174aa47bd94dd48b07684b74b60a5b29ca00eda86'


def main():
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == EXPECTED
    topic = json.loads(SOURCE.read_text(encoding='utf-8'))['details']['rogue_6']
    mechanics = json.loads((ROOT / 'rouge/data/relic-mechanics.json').read_text(encoding='utf-8'))
    rows = {}
    for rid, entry in mechanics['relics'].items():
        if not entry.get('recipient_binding'):
            continue
        raw = topic['relics'][rid]
        assert len(raw['buffs']) == 1
        buff = raw['buffs'][0]
        values = {v['key']: v['valueStr'] if v['valueStr'] is not None else v['value'] for v in buff['blackboard']}
        ids = entry['recipient_binding']['char_buff_ids']
        if buff['key'] == 'rand_gain_char_buff':
            assert ids == values['char_buff_list'].split('|') and values['count'] == 2
            trigger = 'gain_random'
        elif buff['key'] == 'next_recruit_upgrade_char_buff':
            assert ids == [values['char_buff']]
            trigger = 'next_recruit_or_upgrade'
        elif buff['key'] == 'immediate_reward':
            ticket = topic['upgradeTickets'][values['id']]
            assert values['count'] == 1
            assert all(mechanics['char_buffs'][bid]['required_profession'] == ticket['profession'].lower() for bid in ids)
            trigger = 'upgrade_ticket'
        else:
            raise AssertionError(buff['key'])
        rows[rid] = {'trigger': trigger, 'char_buff_ids': ids, 'raw_parent': raw}
    assert len(rows) == 7
    result = {'schema': 1, 'source_sha256': EXPECTED,
        'source_url': 'https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/a550f5e048bb94e7cdefc6eb97a4091f0c4c7add/zh_CN/gamedata/excel/roguelike_topic_table.json',
        'scope': 'Invalidate stale negative recipient evidence only; never choose a recipient or infer repeated stacks.',
        'rules': rows}
    (ROOT / 'rouge/data/recipient-lifecycle.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'rules': len(rows)}))


if __name__ == '__main__':
    main()
