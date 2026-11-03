import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
def sha(raw):
    return hashlib.sha256(raw).hexdigest()
def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT).decode('utf-8').strip()
assert git('branch', '--show-current') == 'codex/p2-development'
assert git('rev-parse', 'HEAD') == git('rev-parse', 'origin/codex/p2-development') == '87a622eea314ccce49712121fd42683eb2e7e463'
assert not git('status', '--porcelain')
cp_path = ROOT / 'DEVELOPMENT_CHECKPOINT.json'
cp_raw = cp_path.read_bytes()
cp = json.loads(cp_raw)
assert cp['completed_sections'] == 301
dest = ROOT / 'verification/sections/302-preparation'
dest.mkdir(parents=True, exist_ok=True)
scope = {
    'section': 302, 'status': 'implementation_started_not_completed',
    'started_at': datetime.now(timezone.utc).isoformat(),
    'parent_commit': git('rev-parse', 'HEAD'),
    'remaining_todo': 'P3 node events/conditions and boss mechanism references, with related fixed battle preview',
    'new_player_capability': 'Read six exact 调谐仪式 submission choices and three distinct documented boss weakening effects; manually open the related fixed 畸症 battle without implying an immediate transition or actual activation.',
    'scope': {'event': 'community_group_032', 'choices': 6, 'effects': 3, 'related_stage': 'ro6_b_6', 'choice_to_effect_order': [1, 3, 2]},
    'evidence': ['verification/sections/301-preparation/future-notes-and-ritual-research/READY.json', 'verification/sections/301-preparation/future-notes-and-ritual-research/complete-candidate-originals-and-DOM.json', 'research/p3-stage-context/community-main.html'],
    'evidence_boundaries': ['Pinned original game table and full fixed community HTML establish configuration and conditional descriptions, not current server execution.', 'Current enemy-page tool result is supplemental body text, not complete fixed HTML; historical HTTP failures remain.', 'Do not merge identical private-key choice titles, infer actual submission/inventory/eligibility, apply numeric weakening, or add a fake event-to-battle transition.'],
    'acceptance': ['Exact six full event/scene/choice identities and feature selectors/blackboard match originals; three duplicate titles remain separate.', 'Player Chinese displays required exchange, conditional effect and applicability, with actual activation explicitly unknown.', 'Default unselected; selection only reads; explicit related battle button opens the exact fixed stage and preserves parent reading.', 'Same-scope refresh preserves actual nonzero scroll/cursor and battle selections; scope/source failure clears old content and child stage; recovery stays unselected.', 'Necessary change-specific tests plus real isolated Windows UI and representative player/map screenshots; keep private five paths unchanged and original test window visible/responding.', 'Commit source, receipts, requirements and index, ordinary push and verify actual remote commit and blobs.'],
    'not_closed': ['25 original-scene entry gaps', '57 original-choice entry/condition gaps', '15 stage/floor applicability gaps', 'actual submitted/attached/executed/consumed state', 'remaining map calibration and unrelated P3/P2/P1 items'],
    'full_validation': {'last': 290, 'next': 305, 'new_full_claimed': False},
    'numeric_continuation_target': None,
}
out = dest / 'scope.json'
assert not out.exists()
out.write_text(json.dumps(scope, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
cache = ROOT / '.cache/p3-302-root'
cache.mkdir(parents=True, exist_ok=True)
private = ['.local/operator-state.json', '.local/run-state.json', '.local/desktop-chat/conversations.json', '.local/desktop-chat/conversations.json.pending', 'local-settings.json']
baseline = {'parent_commit': scope['parent_commit'], 'checkpoint_sha256': sha(cp_raw), 'private_local_only': {p: sha((ROOT/p).read_bytes()) if (ROOT/p).is_file() else None for p in private}, 'tracked_baseline': {p: sha((ROOT/p).read_bytes()) for p in ['rouge/node_catalog_view.py', 'PROJECT_PROGRESS.md', 'PROJECT_REQUIREMENTS.md', 'WORK_IN_PROGRESS.md', 'PROJECT_COMPLETED.md', 'AGENTS.md', 'CLOUD_INDEX.json', 'CLOUD_HANDOFF.md']}}
(cache/'baseline-local-only.json').write_text(json.dumps(baseline, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
cp['active_section'] = {'section': 302, 'scope': 'verification/sections/302-preparation/scope.json', 'status': 'implementation_not_yet_completed', 'functional_progress_claimed': False}
cp_path.write_text(json.dumps(cp, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps({'section':302, 'scope':str(out.relative_to(ROOT)), 'completed_sections':301, 'new_function_completed':False, 'private_baseline_published':False}))
