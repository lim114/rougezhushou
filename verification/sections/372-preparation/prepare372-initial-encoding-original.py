"""Plan/apply a reviewed cache candidate after actually published section371."""
from pathlib import Path
from hashlib import sha256
from copy import deepcopy
from datetime import datetime, timezone
import argparse, ast, importlib.util, json, subprocess, textwrap
HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'rouge/app.py').is_file())
CANDIDATE = HERE / 'section372'
SELECTORS = ('tests.test_current_event_directory_372', 'tests.test_current_event_directory_view_372')
VIEW = 'rouge/expansion_view.py'; FULL = 'scripts/verify_full_available.py'
FILES = ('rouge/current_event_directory.py', 'rouge/current_event_directory_view.py',
         'rouge/data/current-event-directory.json', 'research/p3-current-event-directory-372/source-notes.json',
         'research/p3-current-event-directory-372/runtime-manifest.json',
         'scripts/build_current_event_directory_372.py', 'scripts/verify_current_event_directory_window_372.py',
         'tests/test_current_event_directory_372.py', 'tests/test_current_event_directory_view_372.py')
METHODS = '''
def _close_event_directory(self):
    child=getattr(self,'event_directory_dialog',None)
    if child is not None:
        child.panel.clear_reference();child.close()
    self.event_directory_dialog=None

def _sync_event_directory(self,ready):
    allowed=self.full_catalog and 'scenes' in self.allowed_categories
    self.event_directory_button.setVisible(allowed);self.event_directory_button.setEnabled(ready and allowed)
    child=getattr(self,'event_directory_dialog',None)
    if not ready or not allowed:
        self._close_event_directory();return False
    if child is not None and child.isVisible():
        if not child.panel.refresh_reference():
            self._close_event_directory();self.event_directory_button.setEnabled(False);return False
        if child.panel.result is None or child.panel.result.get('version_source_identity')!=self.source_identity:
            self._close_event_directory();self.event_directory_button.setEnabled(False);return False
    return True

def open_event_directory(self):
    if not self.full_catalog or 'scenes'not in self.allowed_categories:
        self._close_event_directory();return False
    fresh=model.packet()
    if fresh is None or fresh['source_identity']!=self.source_identity:
        self._unavailable();return False
    from .current_event_directory_view import CurrentEventDirectoryDialog
    self._close_event_directory();self.event_directory_dialog=CurrentEventDirectoryDialog(self)
    child=self.event_directory_dialog
    if child.panel.result is None or child.panel.result.get('version_source_identity')!=self.source_identity:
        self._close_event_directory();self.event_directory_button.setEnabled(False);return False
    child.show();return True
'''


def require(value, message):
    if not value: raise RuntimeError(message)


def digest(raw): return sha256(raw).hexdigest()
def enc(obj): return (json.dumps(obj, ensure_ascii=False, indent=2) + '\n').encode('utf8')
def git(*args): return subprocess.check_output(['git', *args], cwd=ROOT, timeout=30).decode('utf8').strip()


def helper():
    path = ROOT / '.cache/section370-integration-prepared/prepare370.py'
    require(path.is_file(), 'Prior reviewed AST helper is required in this cache-only integration session')
    spec = importlib.util.spec_from_file_location('prior370_ast_helper', path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module


def integrate(source):
    h = helper(); klass = 'ExpansionUpdatePanel'; node = h.class_node(source, klass)
    require(not {'_close_event_directory', '_sync_event_directory', 'open_event_directory'} & {n.name for n in node.body if isinstance(n, ast.FunctionDef)}, 'Event directory adapter already installed')
    constructor = h.method(source, klass, '__init__')
    anchors = [n for n in constructor.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name) and t.value.id == 'self' and t.attr == 'tickets_button' for t in n.targets)]
    require(len(anchors) == 1, 'Unique existing tickets assignment required')
    source = h.insert_before_line(source, anchors[0].lineno, '''
        self.event_directory_dialog=None
        self.event_directory_button=QPushButton('节点事件：按条件原文查找与进入完整流程')
        self.event_directory_button.setAccessibleName('当前节点事件目录与准确对话入口')
        layout.addWidget(self.event_directory_button)
        self.event_directory_button.setVisible(self.full_catalog and 'scenes' in self.allowed_categories)
        self.event_directory_button.clicked.connect(self.open_event_directory)
    ''')
    source = h.prepend(source, klass, '_unavailable', 'self._close_event_directory();self.event_directory_button.setEnabled(False)')
    refresh = h.method(source, klass, 'refresh_reference')
    returns = [n for n in refresh.body if isinstance(n, ast.Return) and isinstance(n.value, ast.Name) and n.value.id == 'ready']
    require(len(returns) == 1, 'Unique ordinary refresh return required')
    source = h.insert_before_line(source, returns[0].lineno, 'self._sync_event_directory(ready)')
    source = h.prepend(source, klass, 'close_children', 'self._close_event_directory()')
    node = h.class_node(source, klass); lines = source.splitlines(keepends=True); eol = '\r\n' if '\r\n' in source else '\n'
    return ''.join(lines[:node.end_lineno]) + eol + h.rendered(METHODS, '    ', eol) + ''.join(lines[node.end_lineno:])


def preserve(before, after):
    h = helper(); oldtree, newtree = ast.parse(before), ast.parse(after)
    old, new = h.class_node(before, 'ExpansionUpdatePanel'), h.class_node(after, 'ExpansionUpdatePanel')
    require([ast.dump(n) for n in oldtree.body if not isinstance(n, ast.ClassDef) or n.name != old.name] == [ast.dump(n) for n in newtree.body if not isinstance(n, ast.ClassDef) or n.name != new.name], 'Unrelated top-level code changed')
    methods = {n.name: n for n in new.body if isinstance(n, ast.FunctionDef)}; retained = []
    for prior in (n for n in old.body if isinstance(n, ast.FunctionDef)):
        now = methods[prior.name]
        if prior.name in ('__init__', '_unavailable', 'refresh_reference', 'close_children'):
            a, b = deepcopy(prior), deepcopy(now); a.body = []; b.body = []
            require(ast.dump(a) == ast.dump(b), 'Existing method header changed')
            require(h.is_subsequence([ast.dump(n) for n in prior.body], [ast.dump(n) for n in now.body]), 'Existing statements removed or reordered')
        else: require(ast.dump(prior) == ast.dump(now), 'Unrelated existing method changed: ' + prior.name)
        retained.append(prior.name)
    require(set(methods) - {n.name for n in old.body if isinstance(n, ast.FunctionDef)} == {'_close_event_directory', '_sync_event_directory', 'open_event_directory'}, 'Unexpected new methods')
    return retained


def main():
    p = argparse.ArgumentParser(); p.add_argument('--expected-head', required=True); p.add_argument('--inventory-sha256', required=True); p.add_argument('--apply', action='store_true'); args = p.parse_args()
    require(git('branch', '--show-current') == 'codex/p2-development', 'Wrong branch')
    require(git('rev-parse', 'HEAD') == args.expected_head and len(args.expected_head) == 40, 'Exact published371 metadata HEAD required')
    require(not git('status', '--porcelain', '--untracked-files=normal'), 'Clean public checkout required')
    cp = json.loads((ROOT / 'DEVELOPMENT_CHECKPOINT.json').read_bytes())
    require(cp.get('completed_sections') == 371 and cp.get('next_section') == 372, 'Completed371 / next372 checkpoint required')
    policy = cp.get('policy', {}); require(policy.get('new_functional_sections_paused') is not True and policy.get('development_paused_by_latest_user_request') is not True, 'Installer cannot resume a paused project')
    proof_name = 'verification/sections/371-publication.json'; proof_raw = (ROOT / proof_name).read_bytes(); proof = json.loads(proof_raw)
    require(proof.get('passed') is True and proof.get('ordinary_push') is True and proof.get('force_push') is False and proof.get('section') == 371, 'Actual successful ordinary371 proof required')
    saved = cp.get('last_verified_cloud_save', {})
    require(saved.get('section') == 371 and saved.get('proof') == proof_name and saved.get('proof_sha256') == digest(proof_raw) and saved.get('commit') == proof.get('commit'), 'Checkpoint must bind actual371 proof')
    require(git('ls-remote', 'origin', 'refs/heads/codex/p2-development').split() == [args.expected_head, 'refs/heads/codex/p2-development'], 'Actual remote metadata HEAD differs')
    raw_inventory = (CANDIDATE / 'inventory.json').read_bytes(); require(digest(raw_inventory) == args.inventory_sha256, 'Reviewed candidate inventory differs')
    inventory = json.loads(raw_inventory); require(set(inventory['files']) == set(FILES), 'Exact nine public candidate files required')
    copies = {}
    for name in FILES:
        raw = (CANDIDATE / name).read_bytes(); require(digest(raw) == inventory['files'][name]['sha256'] and len(raw) == inventory['files'][name]['bytes'], 'Candidate byte differs: ' + name)
        if name.endswith('.py'): ast.parse(raw.decode('utf8-sig'), filename=name)
        require(not (ROOT / name).exists(), 'New destination already exists: ' + name); copies[name] = raw
    manifest = json.loads(copies['research/p3-current-event-directory-372/runtime-manifest.json'])
    for name, pin in manifest['files'].items():
        raw = copies[name] if name in copies else (ROOT / name).read_bytes()
        require(digest(raw) == pin['sha256'] and len(raw) == pin['bytes'], 'Actual public upstream source changed since preparation: ' + name)
    before = (ROOT / VIEW).read_bytes(); after = integrate(before.decode('utf8')); retained = preserve(before.decode('utf8'), after)
    selector_before = (ROOT / FULL).read_bytes(); h = helper(); original_selectors = h.SELECTORS; h.SELECTORS = SELECTORS
    selector_after = h.add_selectors(selector_before); h.SELECTORS = original_selectors
    plan = {'section': 372, 'status': 'planned_not_installed', 'expected_prior_HEAD': args.expected_head,
            'inventory_sha256': digest(raw_inventory), 'public_files': {n: digest(raw) for n, raw in copies.items()},
            'view_before': digest(before), 'view_after': digest(after.encode('utf8')), 'all_existing_view_methods_preserved': retained,
            'new_full_check_selectors': SELECTORS, 'no_tests_or_window_started': True, 'no_commit_or_index_written': True,
            'at_utc': datetime.now(timezone.utc).isoformat()}
    if not args.apply: print(json.dumps(plan, ensure_ascii=False, indent=2)); return 0
    require(git('rev-parse', 'HEAD') == args.expected_head and not git('status', '--porcelain', '--untracked-files=normal'), 'Checkout changed during planning')
    require((ROOT / VIEW).read_bytes() == before and (ROOT / FULL).read_bytes() == selector_before, 'Existing adapter changed concurrently')
    scope = ROOT / 'verification/sections/372-preparation'; require(not scope.exists(), 'Preparation evidence already exists')
    ledger = HERE / ('installation372-' + args.expected_head[:12]); require(not ledger.exists(), 'Prior installation ledger cannot be overwritten'); ledger.mkdir()
    for name, raw in ((VIEW, before), (FULL, selector_before)):
        path = ledger / 'before' / name; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(raw)
    for name, raw in copies.items():
        target = ROOT / name; target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('xb') as stream: stream.write(raw)
    (ROOT / VIEW).write_bytes(after.encode('utf8')); (ROOT / FULL).write_bytes(selector_after)
    scope.mkdir(); (scope / 'scope.json').write_bytes(enc({**plan, 'status': 'active_not_completed',
        'remaining_work': '当前固定节点事件与条件文献的完整合流查找、准确对话入口与所属窗口清理',
        'new_capability': '39份当前事件、38个旧分组和277个准确对话选项位置可跨全文筛选并回到21种已有reader',
        'acceptance': ['未分类和完整资格未知保留', '同名来源/阶段/结果参考不混合', '父刷新保留搜索筛选选择与两非零阅读', '坏源清实际资料和整树，恢复手选', '普通页/主窗关闭，七类外部零且临时态不变'],
        'validation_or_completion_claimed': False}))
    runner = (HERE / 'run372.py').read_bytes()
    with (ROOT / '.cache/run372.py').open('xb') as stream: stream.write(runner)
    require(all((ROOT / name).read_bytes() == raw for name, raw in copies.items()), 'Copied candidate readback differs')
    plan['status'] = 'installed_unverified'; (ledger / 'result.json').write_bytes(enc(plan)); print(json.dumps(plan, ensure_ascii=False, indent=2)); return 0


if __name__ == '__main__': raise SystemExit(main())
