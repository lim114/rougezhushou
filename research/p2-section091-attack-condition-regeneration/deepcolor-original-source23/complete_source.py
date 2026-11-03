"""Resume only static anchor/receipt capture after a documented preparation error."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path('/workspace/rougezhushou')
OUT = Path(__file__).resolve().parent
BASE = '5e2ff697402d06e78b239e01f0b4307b50dd5633'

def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)

def write_json(name, value):
    target = OUT / name
    if target.exists():
        raise RuntimeError('Existing completed artifact: ' + name)
    target.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')

if git('rev-parse', 'HEAD').decode().strip() != BASE or git('status', '--porcelain'):
    raise RuntimeError('Root90 frozen Git baseline no longer clean/exact')
snap = OUT / 'git-snapshots'
files = sorted(p for p in snap.rglob('*') if p.is_file())
if len(files) != 13:
    raise RuntimeError('Expected13 already captured source leaves')
entries = []
for path in files:
    rel = path.relative_to(snap).as_posix()
    raw = path.read_bytes()
    if raw != git('show', BASE + ':' + rel) or raw != (ROOT / rel).read_bytes():
        raise RuntimeError('Captured source drift: ' + rel)
    entries.append({'repository_path': rel, 'archive_path': path.relative_to(OUT).as_posix(),
                    'git_commit': BASE, 'git_blob': git('rev-parse', BASE + ':' + rel).decode().strip(),
                    'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest(), 'worktree_equals_git': True})
code = {rel: (snap / rel).read_text() for rel in ('rouge/operator_engine.py', 'rouge/reporting.py', 'rouge/relics.py', 'rouge/damage.py')}
trees = {rel: ast.parse(text) for rel, text in code.items()}
evaluate = next(n for n in trees['rouge/damage.py'].body if isinstance(n, ast.FunctionDef) and n.name == '_evaluate_damage_once')
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
found = {}
for key, (rel, needle) in anchors.items():
    lines = code[rel].splitlines()
    hits = [i for i, line in enumerate(lines) if needle in line]
    if key == 'report_build_after_finish':
        hits = [i for i in hits if evaluate.lineno <= i + 1 <= evaluate.end_lineno]
    if len(hits) != 1:
        raise RuntimeError('Still ambiguous static source anchor: ' + key)
    i = hits[0]
    found[key] = {'repository_path': rel, 'line': i + 1,
                  'function_scope_if_needed': '_evaluate_damage_once' if key == 'report_build_after_finish' else None,
                  'excerpt': '\n'.join(lines[max(0, i - 2):i + 4])}
write_json('source-contract-paths.json', {
    'project_functions_called': 0, 'anchors': found,
    'data_flow': ['S1 full nominal plan and optional observed plan append base-rate x duration x declared-count notes',
                  'calculate stores de-duplicated notes in result.estimate.notes',
                  'relics.finish resolves numeric regeneration factor without rewriting raw base total notes',
                  'build_report uses the resolved factor for Deepcolor S1 per-token/all-token conditional rates',
                  'format_report keeps estimate notes in its user-visible scope block'],
    'supported_lead': 'Existing raw arithmetic references lose their nominal/window and base-versus-adjusted qualification',
    'native_tick_presence_lifetime_binding_or_hotupdate_verified': False,
})
write_json('source-receipt.json', {
    'scope': 'One future source-only lead; not a completed section or product draft',
    'root_branch': git('branch', '--show-current').decode().strip(), 'root_head_before': BASE,
    'source_files': entries, 'root_head_after': git('rev-parse', 'HEAD').decode().strip(),
    'root_status_after': git('status', '--porcelain').decode(),
    'calls': {'fresh_application_API': 0, 'project_helper': 0, 'project_formatter': 0,
              'tests': 0, 'game_data_AB_parser': 0, 'public_source_network_download': 0,
              'Qt': 0, 'Wine': 0, 'old_section63_replay': 0, 'section90_verifier': 0,
              'historical_raw_source_rehash': 0, 'private_cache_reads': 0},
    'preparation': {'attempt1': 'failed after snapshots/evidence at ambiguous report-build anchor',
                    'completion_attempt2': 'AST scoped anchor and receipt only; earlier files preserved',
                    'project_python_imports_or_execution': 0},
    'read_only_stdlib': ['existing public JSON/gzip loads', 'static AST/anchor inspection', 'Git blob transport checks'],
})
print(json.dumps({'status': 'SOURCE_ONLY_LEAD_COMPLETED', 'git_source_files': len(entries),
                  'saved_real_record': 389, 'fresh_application_API': 0}))
