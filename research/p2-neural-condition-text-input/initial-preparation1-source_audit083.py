"""Read public pinned data and frozen consumers; perform no calculations."""
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
BASE = OUT / 'baseline'
REPO = Path('/workspace/rougezhushou')
SOURCE_COMMIT = 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add'


def source(name):
    data = (BASE / name).read_bytes()
    return data.decode('utf-8'), {'path': name, 'bytes': len(data),
                               'sha256': hashlib.sha256(data).hexdigest()}


def excerpt(text, first, last):
    start = text.index(first)
    end = text.index(last, start) + len(last)
    return text[start:end]


raw_records = {}
raw = {}
for name, expected in (
    ('character_table', '68e3a3b5ee0d407ce234afaa5867c6fda6379a6843c7d5317a7bbda4779f8697'),
    ('skill_table', '86f4aa64c785f39727edd06d6dd8a4f27f371c8e4ace5345ba0dc61dee1386ca'),
):
    path = REPO / '.cache/p2-s1-binding' / (name + '.json')
    data = path.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    assert digest == expected
    raw_records[name] = {'path': str(path), 'bytes': len(data), 'sha256': digest,
        'source_url': 'https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/'
        + SOURCE_COMMIT + '/zh_CN/gamedata/excel/' + name + '.json'}
    raw[name] = json.loads(data)

engine, engine_record = source('rouge/operator_engine.py')
damage, damage_record = source('rouge/damage.py')
options, options_record = source('rouge/operator_options.py')
app, app_record = source('rouge/app.py')
enemy, enemy_record = source('rouge/enemy_environment.py')
catalog_text, catalog_record = source('rouge/data/catalog.json')
catalog = json.loads(catalog_text)['operators']
operators = {}
for owner in ('char_1042_phatm2', 'char_4204_mantra'):
    original = raw['character_table'][owner]
    public = catalog[owner]
    skills = []
    for index, skill in enumerate(original['skills']):
        original_levels = raw['skill_table'][skill['skillId']]['levels']
        selected = public['skills'][index]
        assert selected['id'] == skill['skillId']
        assert selected['unlock_elite'] == int(skill['unlockCond']['phase'][-1])
        assert len(selected['levels']) == len(original_levels) == 10
        for level, old in zip(selected['levels'], original_levels, strict=True):
            assert level['values'] == {b['key']: b['value'] for b in old['blackboard']}
        skills.append({'number': index + 1, 'original_selector':
            'character_table.' + owner + '.skills[' + str(index) + ']',
            'unlock_condition': skill['unlockCond'], 'skill_id': skill['skillId'],
            'all_ten_original_levels': original_levels})
    operators[owner] = {'name': original['name'], 'original_talents': original['talents'],
                        'skills': skills}

assert "threshold=2000 if self.s.get('enemy_is_boss') else 1000" in engine
assert "breaking_until=break_end(0) if self.s.get('enemy_in_neural_break') else -1" in engine
assert "'preexisting_break_assumed':bool(self.s.get('enemy_in_neural_break'))" in engine
assert engine.count('self.neural(') == 3
assert "scenario['enemy_is_boss']=record['level_type']=='BOSS'" in enemy
assert damage.index('scenario,run_resolution=prepare_run(scenario)') < damage.index('result=calculate_extended(scenario,attributes)')
assert "widget=QCheckBox(label);widget.setChecked(default)" in app
assert "if owner==op and self.skill.currentData() in skills:" in app
assert "scenario[key]=widget.isChecked() if isinstance(widget,QCheckBox) else widget.value()" in app

receipt = {'source_commit': SOURCE_COMMIT, 'baseline_commit':
    json.loads((OUT / 'freeze-receipt083.json').read_text())['baseline_commit'],
    'raw_sources': raw_records, 'production_files': [engine_record, damage_record,
        options_record, app_record, enemy_record, catalog_record], 'operators': operators,
    'scope': {'actual_neural_owners': ['char_1042_phatm2', 'char_4204_mantra'],
        'skill_qualification': 'Existing public skill/elite/rank checks precede Combat.',
        'skills_consumed': [1, 2, 3],
        'mantra_S3': 'The unconditional postmodifier neural call still validates the threshold and records a preexisting River break; missing widgets do not prove inactivity.',
        'normal': 'calculate first executes full plan; normal plan also calls the same owner consumers when a cycle exists.',
        'other_owners': 'Ignored by the proposed two-owner guard, including unrelated selected-target boss identity.',
        'enemy_identity': 'prepare_run resolves selected enemy before evaluation, replacing stale manual enemy_is_boss.',
        'nontext': 'Preserve existing bool/null/numeric/container truthiness; reject only str.',
        'native_validation': False, 'GUI_executed': False, 'Windows_or_Wine_executed': False,
        'new_threshold_or_clock_claims': False, 'API_calls': 0},
    'consumer_excerpts': {
        'neural': excerpt(engine, '    def neural(', '        return burst_times'),
        'phatm2': excerpt(engine, "        elif op=='char_1042_phatm2':", "        elif op=='char_4204_mantra':"),
        'mantra_postmodifier': excerpt(engine, "        if op=='char_4204_mantra':\n            # Damage-dependent", '        for c in components:'),
        'public_preparation_and_evaluation': excerpt(damage, 'def _prepare_damage(', 'def _evaluate_damage(prepared,wine_phase=None)'),
        'Qt_factory': excerpt(app, '        self.model_option_widgets=[]', '        columns.addLayout(form,1)'),
        'Qt_serializer': excerpt(app, '        for owner,key,skills,widget in self.model_option_widgets:\n            if owner==op', '        state=self.current_operator_state()'),
        'identity_override': excerpt(enemy, '    # Identity-derived state wins', "    scenario['_run_damage_factor']=enemy['damage_factor']"),
    },
    'prior_contracts_reused': ['tests/test_preexisting_fragile_input_types.py',
        'tests/test_cooperative_input_types.py', 'tests/test_shu_profession_text_input.py',
        'research/p2-four-sui-text-input/prior-readonly-audit/NOTE.md'],
    'unmodified_unknowns': ['S1 attachment and same-hit order', 'S3 secondary clock',
        'River periodic scheduling and active phase masks', 'resource phase and snapshots'],
}
(OUT / 'source-receipt083.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'passed': True, 'API_calls': 0, 'raw_files': 2,
                  'original_skill_levels': 60, 'production_files': 6}))
