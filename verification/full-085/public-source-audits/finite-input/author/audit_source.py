"""Bounded public source audit; never import or execute project functions."""
import ast
import hashlib
import json
import subprocess
from pathlib import Path

REPO = Path('/workspace/rougezhushou')
OUT = Path(__file__).resolve().parent
COMMIT = '2dfd9fa2c9a62db0112bc0fb98cd23123dd3b48b'
PRODUCTION = [
    'rouge/damage.py', 'rouge/operator_engine.py', 'rouge/estimate.py',
    'rouge/timing.py', 'rouge/catalog.py', 'rouge/relics.py',
    'rouge/relic_attributes.py', 'rouge/deployment.py',
    'rouge/enemy_environment.py', 'rouge/animation_reference.py',
    'rouge/attribute_limits.py', 'rouge/sp_events.py',
    'rouge/reporting.py', 'rouge/app.py',
]
HISTORY = [
    'tests/test_damage.py', 'tests/test_zero_lifetime_aliases.py',
    'tests/test_training_input_types.py', 'tests/test_declared_count_input_types.py',
    'tests/test_target_count_input_types.py',
    'research/p2-zero-lifetime-aliases/NOTE.md',
    'research/p2-zero-lifetime-aliases/ARCHIVE.md',
    'research/p2-zero-lifetime-aliases/public-comparison-055.json',
    'research/p2-zero-lifetime-aliases/independent-review/receipt.json',
    'research/p2-integer-option-input-types/NOTE.md',
    'research/p2-integer-option-input-types/handoff-receipt.json',
    'research/p2-integer-option-input-types/independent/receipt.json',
    'research/p2-declared-count-input-types/NOTE.md',
    'research/p2-declared-count-input-types/ARCHIVE.md',
    'research/p2-declared-count-input-types/handoff-receipt.json',
]
records = {}
texts = {}
for name in PRODUCTION + HISTORY:
    content = subprocess.check_output(['git', 'show', f'{COMMIT}:{name}'], cwd=REPO)
    destination = OUT / 'fixed-public' / name
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(content)
    records[name] = {'source_commit': COMMIT, 'archive_path': 'fixed-public/' + name,
        'bytes': len(content), 'sha256': hashlib.sha256(content).hexdigest(),
        'git_blob': subprocess.check_output(['git', 'rev-parse', f'{COMMIT}:{name}'],
                                          cwd=REPO, text=True).strip()}
    texts[name] = content.decode('utf-8').replace('\r\n', '\n')


def function(name, qualified):
    parsed = ast.parse(texts[name])
    body = parsed.body
    for part in qualified.split('.'):
        node = next(node for node in body if isinstance(node, (ast.FunctionDef, ast.ClassDef))
                    and node.name == part)
        body = node.body
    return {'source_path': name, 'function': qualified, 'line': node.lineno,
            'end_line': node.end_lineno, 'source': ast.get_source_segment(texts[name], node)}


guards = [function(name, qualified) for name, qualified in [
    ('rouge/damage.py', '_prepare_damage'),
    ('rouge/damage.py', '_skill_damage_base'),
    ('rouge/damage.py', '_evaluate_damage_once'),
    ('rouge/damage.py', 'calculate_damage'),
    ('rouge/operator_engine.py', 'Combat.__init__'),
    ('rouge/operator_engine.py', 'Combat.value'),
    ('rouge/operator_engine.py', 'Combat.option'),
    ('rouge/estimate.py', 'build_estimate.nonnegative'),
    ('rouge/timing.py', 'finite'),
    ('rouge/timing.py', 'AttackTimeline.__init__'),
    ('rouge/timing.py', 'AttackTimeline.ranges'),
    ('rouge/catalog.py', 'operator_attributes'),
    ('rouge/relics.py', 'context_value'),
    ('rouge/relic_attributes.py', 'prepare_attribute_runes'),
    ('rouge/relic_attributes.py', 'apply_attribute_runes'),
    ('rouge/deployment.py', '_single'),
    ('rouge/deployment.py', '_fp'),
    ('rouge/enemy_environment.py', 'resolve_enemy'),
]]
inventory = []


class NumericCalls(ast.NodeVisitor):
    def __init__(self, name):
        self.name = name
        self.scope = []

    def visit_FunctionDef(self, node):
        self.scope.append(node.name)
        self.generic_visit(node)
        self.scope.pop()

    def visit_ClassDef(self, node):
        self.scope.append(node.name)
        self.generic_visit(node)
        self.scope.pop()

    def visit_Call(self, node):
        call = ast.unparse(node.func)
        if call in ('float', 'math.isfinite', 'finite', 'self.value', 'self.option', 'nonnegative'):
            inventory.append({'source_path': self.name, 'scope': '.'.join(self.scope),
                              'line': node.lineno, 'call': ast.unparse(node)})
        self.generic_visit(node)


for name in PRODUCTION:
    NumericCalls(name).visit(ast.parse(texts[name]))

engine = texts['rouge/operator_engine.py']
damage = texts['rouge/damage.py']
assert "self.base=float(scenario['base_attack'])\n        self.value(self.base,'基础攻击')" in engine
assert "self.enemy_def=self.option('enemy_defense',0)" in engine
assert "self.enemy_res=self.option('enemy_resistance',0,maximum=100)" in engine
assert 'not math.isfinite(value)' in function('rouge/operator_engine.py', 'Combat.value')['source']
assert 'not math.isfinite(value)' in function('rouge/estimate.py', 'build_estimate.nonnegative')['source']
assert 'not math.isfinite(value)' in function('rouge/timing.py', 'finite')['source']
assert 'not math.isfinite(value)' in function('rouge/deployment.py', '_single')['source']
assert "for field in ('base_attack','enemy_defense','enemy_resistance','window_seconds','companion_attack'):" in damage
assert "scenario['enemy_defense']=stats['def'];scenario['enemy_resistance']=stats['magicResistance']" in texts['rouge/enemy_environment.py']

findings = {
    'status': 'bounded_negative_source_audit_not_numbered', 'fixed_commit': COMMIT,
    'confirmed_missing_public_float_consumer_guards': [], 'actionable_candidates': [],
    'maximum_candidates_requested': 2,
    'traced_boundaries': [
        {'fields': ['base_attack'], 'outcome': 'Existing protection found.',
         'paths': ['Combat.__init__ -> Combat.value', '_skill_damage_base finite scalar loop',
                   'prepare_attribute_runes -> apply_attribute_runes -> _fp/_single when a rune is present'],
         'qualification': 'Actual operator paths; no-rune path remains subject to the later engine guard.'},
        {'fields': ['enemy_defense', 'enemy_resistance'], 'outcome': 'Existing protection found.',
         'paths': ['Combat.option -> Combat.value', '_skill_damage_base finite scalar loop'],
         'qualification': 'Fixed selected enemy identity replaces stale manual fields before engine checks; this is an existing precedence, not a missing manual-field guard.'},
        {'fields': ['window_seconds', 'skill_duration_seconds', 'healing_targets'],
         'outcome': 'Existing finite checks at actual numeric consumers; capability/raw-bool distinction is historical and must stay scoped.',
         'paths': ['Combat.option', 'build_estimate.nonnegative', 'AttackTimeline.attacks/finite']},
        {'fields': ['initial_sp_bonus', 'sp_recovery_bonus', 'deployment_elapsed_seconds'],
         'outcome': 'Existing finite checks on actual legacy estimate/selected elapsed/relic finisher paths; unused owner fields are not new candidates.',
         'paths': ['build_estimate.nonnegative', 'Combat.option for selected elapsed consumer',
                   'relics.finish -> timing.finite for finite deployment-speed rules']},
        {'fields': ['effects[*].value', 'relic_context numeric conditions', 'timing numeric scalars and ranges'],
         'outcome': 'Finite checks already present before active numeric consumption.',
         'paths': ['Combat.__init__/value', '_skill_damage_base effect loop',
                   'relics.context_value', 'AttackTimeline.__init__/ranges -> finite/frame_time',
                   'sp_events finite event times']},
    ],
    'existing_error_precedence': [
        'Public skill/rank and cultivated attributes/module validation precede engine evaluation.',
        'prepare_run/fixed enemy identity, relic resolution and attribute rune conversion precede both engines.',
        'Extended constructor checks effect kinds/values, then enemy defense/resistance, explicit windows/duration, base attack, and active talents.',
        'Legacy scalar checks precede legacy declared counts and later estimate nonnegative checks.',
        'The existing report/finishers and scoped string conditions remain after the original numeric validations; no new validator or error is proposed.',
    ],
    'historical_receipts_reused': [
        {'path': 'research/p2-zero-lifetime-aliases/public-comparison-055.json',
         'claim': 'Historical saved preservation of nonzero invalid timing inputs, not current fresh API verification.'},
        {'path': 'research/p2-integer-option-input-types/handoff-receipt.json',
         'claim': 'Historical integer raw-bool correction keeps noninteger controls and inactive fields unchanged.'},
        {'path': 'research/p2-declared-count-input-types/handoff-receipt.json',
         'claim': 'Historical owner/capability-specific raw-bool boundary, not a global float-only type policy.'},
    ],
    'limits': [
        'No new execution proves current behavior for NaN/inf; conclusions are source and existing receipt checks only.',
        'No claim that every possible field or every derived arithmetic overflow is covered.',
        'No new numerical bounds or boolean/number policy is inferred from UI ranges.',
        'Inactive or identity-overwritten fields cannot be declared bugs merely because their raw value is nonfinite.',
        'The separate 86 twelve boolean contract fields, module/talent qualification audits, native attachments and clocks are not reaudited.',
    ],
    'counters': {'API_calls': 0, 'project_helper_calls': 0, 'tests': 0,
                 'Qt': 0, 'Wine': 0, 'product_patches': 0, 'matrices': 0, 'tracked_edits': 0},
    'restart': 'Stop this negative audit. Only reopen for a named active float field, an exact absent finite gate, and qualified old public evidence supplied or separately authorized; do not repeat existing matrices or manufacture a section.',
}
history = {}
for name in HISTORY:
    if name.endswith('.json'):
        history[name] = json.loads(texts[name])
(OUT / 'fixed-source-receipt.json').write_text(json.dumps({'fixed_commit': COMMIT,
    'files': records, 'production_files': len(PRODUCTION), 'history_files': len(HISTORY),
    'project_code_imported_or_executed': False}, indent=2) + '\n')
(OUT / 'guard-function-excerpts.json').write_text(json.dumps(guards, ensure_ascii=False, indent=2) + '\n')
(OUT / 'numeric-call-ast-inventory.json').write_text(json.dumps(inventory, ensure_ascii=False, indent=2) + '\n')
(OUT / 'historical-saved-receipts-read.json').write_text(json.dumps(history, ensure_ascii=False, indent=2) + '\n')
(OUT / 'findings.json').write_text(json.dumps(findings, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'passed': True, 'API_calls': 0, 'project_helper_calls': 0,
                  'confirmed_candidates': 0, 'fixed_public_files': len(records),
                  'guard_functions': len(guards), 'numeric_AST_call_sites': len(inventory)}))
