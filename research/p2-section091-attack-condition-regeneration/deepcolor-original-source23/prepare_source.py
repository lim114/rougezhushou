"""Capture one static source lead. No project imports or execution."""
import ast
import gzip
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path('/workspace/rougezhushou')
OUT = Path(__file__).resolve().parent
BASE = '5e2ff697402d06e78b239e01f0b4307b50dd5633'
PATHS = (
    'PROJECT_PROGRESS.md', 'rouge/operator_engine.py', 'rouge/reporting.py',
    'rouge/relics.py', 'rouge/damage.py', 'rouge/data/catalog.json',
    'rouge/data/relic-mechanics.json', 'tests/test_summon_count_reporting.py',
    'tests/test_summon_modules_038.py', 'tests/test_relics.py',
    'research/p2-token-count-reporting/NOTE-source.md',
    'research/p2-token-count-reporting/source-closure.json',
    'research/p2-token-count-reporting/validation-after61/draft63.json.gz',
)


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def write_json(name, value):
    p = OUT / name
    if p.exists():
        raise RuntimeError('Refusing to replace existing artifact: ' + name)
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')


head = git('rev-parse', 'HEAD').decode().strip()
if head != BASE:
    raise RuntimeError('Expected frozen root90 baseline, observed ' + head)
if git('status', '--porcelain'):
    raise RuntimeError('Source lead requires clean root checkout')
snapshots = []
for rel in PATHS:
    raw = git('show', BASE + ':' + rel)
    if raw != (ROOT / rel).read_bytes():
        raise RuntimeError('Git/worktree source mismatch: ' + rel)
    destination = OUT / 'git-snapshots' / rel
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        raise RuntimeError('Snapshot exists: ' + rel)
    destination.write_bytes(raw)
    snapshots.append({'repository_path': rel, 'archive_path': destination.relative_to(OUT).as_posix(),
                      'git_commit': BASE, 'git_blob': git('rev-parse', BASE + ':' + rel).decode().strip(),
                      'bytes': len(raw), 'sha256': sha(raw), 'worktree_equals_git': True})

snap = OUT / 'git-snapshots'
catalog = json.loads((snap / 'rouge/data/catalog.json').read_text())
mechanics = json.loads((snap / 'rouge/data/relic-mechanics.json').read_text())
closure = json.loads((snap / 'research/p2-token-count-reporting/source-closure.json').read_text())
skill = catalog['operators']['char_110_deepcl']['skills'][0]
rank10 = skill['levels'][9]
rose = mechanics['relics']['rogue_6_relic_legacy_81']
old = snap / 'research/p2-token-count-reporting/validation-after61/draft63.json.gz'
with gzip.open(old, 'rt', encoding='utf-8') as handle:
    saved = json.load(handle)
selected = [(index, row) for index, row in enumerate(saved['records']) if row['id'] == 389]
if len(selected) != 1:
    raise RuntimeError('Saved real record389 selector not unique')
index, row = selected[0]
notes = [note for note in row['result']['estimate']['notes'] if note.startswith('触手数量')]
expected = ['触手数量 2；技能生命回复 4200，生命回复不计直接治疗。',
            '触手数量 2；技能生命回复 1400，生命回复不计直接治疗。']
if notes != expected:
    raise RuntimeError('Saved record389 does not match the read-only finding')
write_json('saved-real-record389.json', row)
write_json('selected-source-evidence.json', {
    'classification': 'STATIC_SOURCE_AND_EXISTING_REAL_SAVED_RESULT',
    'source_git_commit': BASE,
    'pinned_game_commit': catalog['source']['commit'],
    'current_raw_table_downloads_or_rehashes': 0,
    'catalog_s1_rank10_selector': 'operators.char_110_deepcl.skills[0].levels[9]',
    'catalog_s1_id': skill['id'], 'catalog_s1_rank10': rank10,
    'prior_original_table_receipt_reused': {
        'source': 'git-snapshots/research/p2-token-count-reporting/source-closure.json',
        'fresh_pinned_raw_tables_historical_only': closure['fresh_pinned_raw_tables'],
        's1_rank10': next(r for r in closure['raw_skill_records'] if r['skill_number'] == 1 and r['rank'] == 10),
    },
    'rose81_selector': 'relics.rogue_6_relic_legacy_81', 'rose81': rose,
    'rose81_runtime_qualification': 'game_data_verified_runtime_pending, stacking unverified; existing single-relic offline reference only',
    'saved_record389': {'source_archive_path': old.relative_to(OUT).as_posix(),
                        'source_sha256': sha(old.read_bytes()), 'selector': 'records[' + str(index) + '], id=389',
                        'copied_row_archive_path': 'saved-real-record389.json',
                        'real_calls_in_prior_saved_receipt': saved['calls'],
                        'fresh_replay_calls_in_this_lead': 0,
                        'input': row['input'], 'unqualified_total_notes': notes,
                        'regeneration_multiplier': row['result']['relic_regeneration_multiplier'],
                        'regeneration_report': next(b for b in row['result']['report']['sections'] if b['id'] == 'regeneration')},
    'facts': {
        'old_real_result_contains_two_different_totals_with_same_unqualified_label': True,
        'old_real_record_has_rose81': False,
        'single_rose81_note_rate_disagreement': 'STATIC_CODE_PATH_PREDICTION_ONLY_NOT_A_NEW_REAL_REPRODUCTION',
        'native_regeneration_tick_or_lifetime_or_hotupdate_verified': False,
    },
})

engine = (snap / 'rouge/operator_engine.py').read_text()
report = (snap / 'rouge/reporting.py').read_text()
relics = (snap / 'rouge/relics.py').read_text()
damage = (snap / 'rouge/damage.py').read_text()
for source in (engine, report, relics, damage):
    ast.parse(source)  # Syntax/selection only; no project functions execute.
anchors = {
    'base_total_note_creation': ('rouge/operator_engine.py', '技能生命回复'),
    'full_and_observed_plan_creation': ('rouge/operator_engine.py', 'full=self.plan()'),
    'notes_merge': ('rouge/operator_engine.py', "'warnings':self.warnings,'notes':list(dict.fromkeys(self.notes))"),
    'regeneration_factor_write': ('rouge/relics.py', "result['relic_regeneration_multiplier']=factor"),
    'report_rate_uses_post_finish_factor': ('rouge/reporting.py', "factor=result.get('relic_regeneration_multiplier',1)"),
    'formatter_retains_estimate_notes': ('rouge/reporting.py', "for note in estimate['notes']:"),
    'finish_before_report': ('rouge/damage.py', 'finish(result,resolution,attributes,scenario)'),
    'report_build_after_finish': ('rouge/damage.py', "result['report']=build_report(scenario,result)"),
}
code = {'rouge/operator_engine.py': engine, 'rouge/reporting.py': report,
        'rouge/relics.py': relics, 'rouge/damage.py': damage}
found = {}
for key, (rel, needle) in anchors.items():
    lines = code[rel].splitlines()
    hits = [i for i, line in enumerate(lines) if needle in line]
    if len(hits) != 1:
        raise RuntimeError('Source anchor not unique: ' + key)
    i = hits[0]
    found[key] = {'repository_path': rel, 'line': i + 1,
                  'excerpt': '\n'.join(lines[max(0, i - 2):i + 4])}
write_json('source-contract-paths.json', {
    'project_functions_called': 0, 'anchors': found,
    'data_flow': ['calculate.plan full and optional observed plan append raw base-rate x duration x declared-count notes',
                  'calculate stores de-duplicated notes in result.estimate.notes',
                  'damage finisher relics.finish resolves regeneration multiplier and modifies numeric regeneration sources, not the existing raw total note',
                  'build_report computes Deepcolor S1 fixed-rate reference with result.relic_regeneration_multiplier',
                  'format_report retains the two estimate notes in the user-visible scope block'],
    'unknowns_preserved': ['native fixed-regeneration first tick and cadence', 'real token presence and deployment',
                          'actual S1 coverage and end clock', 'current-client hotupdate equivalence',
                          'multiple received-regeneration relic stacking'],
})
write_json('source-receipt.json', {
    'scope': 'One future source-only lead; not a completed section or product draft',
    'root_branch': git('branch', '--show-current').decode().strip(), 'root_head_before': head,
    'source_files': snapshots, 'root_head_after': git('rev-parse', 'HEAD').decode().strip(),
    'root_status_after': git('status', '--porcelain').decode(),
    'calls': {'fresh_application_API': 0, 'project_helper': 0, 'project_formatter': 0,
              'tests': 0, 'source_parser': 0, 'network': 0, 'Qt': 0, 'Wine': 0,
              'old_section63_replay': 0, 'section90_verifier': 0},
    'read_only_stdlib': ['json/gzip loads of existing public bytes', 'Python AST syntax/anchor reads', 'Git read-only blob capture'],
})
print(json.dumps({'status': 'SOURCE_CAPTURED', 'source_git_files': len(snapshots),
                  'source_commit': head, 'saved_real_record': 389, 'new_application_calls': 0}))
