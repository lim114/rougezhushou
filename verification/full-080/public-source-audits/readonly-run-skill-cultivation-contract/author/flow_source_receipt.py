import hashlib, json, pathlib

OUT = pathlib.Path(__file__).resolve().parent
parts = {
    'rouge/run_recognition.py': [(150, 160), (345, 381)],
    'rouge/run_state.py': [(379, 390), (410, 426)],
    'rouge/app.py': [(767, 789), (815, 825), (990, 998), (1026, 1036)],
    'rouge/damage.py': [(236, 251)],
}
records = []
for name, spans in parts.items():
    raw = (OUT / 'frozen75' / name).read_bytes()
    lines = raw.decode().splitlines()
    records.append({'source_path': name, 'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw), 'spans': [{'start_line': first, 'end_line': last, 'exact_text': '\n'.join(lines[first-1:last])} for first, last in spans]})
receipt = {'baseline_head': 'a52a4bf9217aee3c11617135b7fc9cc6c38fd0f2', 'kind': 'frozen public producer / state / scenario / API qualification selectors', 'files': records, 'closed_current_code_contract': ['run selected-member badges parse ranks1–7; E2 rank7 alone does not infer mastery0', 'roster mastery card markers queried only when fields.elite is2', 'RunState promotion preserves history and invalidates all old skill ranks until new evidence', 'current_operator_state uses only noninvalid run skill_ranks for a present run member, rather than borrowing account ranks', 'skill_rank_value uses known run rank or explicit preview default7 belowE2 and10 atE2', 'available skill choices use original profile skill.unlock_elite', 'initial scenario includes training_conditions and skill_rank_value', 'public API retains original skill unlock elite and belowE2 mastery gate'], 'does_not_prove': ['actual account-to-roguelike temporary cultivation skill inheritance', 'actual client use cap for an account-trained common skill in an E0 temporary form', 'mastery use while current run form is belowE2'], 'new_game_rule_or_gate_changed': False}
(OUT / 'flow-source-selectors.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'files': len(records), 'sha256': hashlib.sha256((OUT / 'flow-source-selectors.json').read_bytes()).hexdigest()}))
