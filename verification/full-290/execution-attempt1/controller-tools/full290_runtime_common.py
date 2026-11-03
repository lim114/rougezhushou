"""Shared periodic290 guards; stdlib and maintained public runner APIs only."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
FREEZE = ROOT / 'verification/full-290/source-freeze.json'
PYTHON = ROOT / '.venv/Scripts/python.exe'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_new(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as file:
        file.write((json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode('utf8'))


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()


def native():
    if sys.platform != 'win32' or Path(sys.executable).resolve() != PYTHON.resolve():
        raise ValueError('Use the exact original project native Windows Python')


def runner_api_snapshot():
    """Call existing source_hashes/NEW_MODULES/MODULES without calling main/tests.

    Fresh compile avoids a stale pyc defining a different selector API. No
    project app/test module or Qt object is imported by these two maintained
    runner module bodies; main is deliberately not entered.
    """
    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(ROOT / 'scripts'))
    path = ROOT / 'scripts/verify_full_available.py'
    raw = path.read_bytes()
    module = {'__file__': str(path), '__name__': '_full290_maintained_runner_api'}
    exec(compile(raw, str(path), 'exec'), module)
    cloud_path = ROOT / 'scripts/verify_cloud.py'
    cloud_raw = cloud_path.read_bytes()
    cloud = {'__file__': str(cloud_path), '__name__': '_full290_cloud_selector_api'}
    exec(compile(cloud_raw, str(cloud_path), 'exec'), cloud)
    historical = json.loads((ROOT / 'CORE_0.70_VERIFICATION.json').read_bytes())
    selectors = list(dict.fromkeys(historical['test_modules'] + list(module['NEW_MODULES']) + list(cloud['MODULES'])))
    sources = module['source_hashes']()
    if sha(path) != hashlib.sha256(raw).hexdigest() or sha(cloud_path) != hashlib.sha256(cloud_raw).hexdigest():
        raise ValueError('Runner source changed while its existing APIs were read')
    return {'source_sha256': sources, 'selectors': selectors,
            'maintained_runner_sha256': hashlib.sha256(raw).hexdigest(),
            'cloud_selector_api_sha256': hashlib.sha256(cloud_raw).hexdigest()}


def preparation_pins():
    names = ('prepare_full290_window.py', 'offline290_launcher.py', 'full290_runtime_common.py',
             'produce_final_freeze_290.py', 'run_full290_orchestration.py', 'archive_full290_outputs.py',
             'run_p3_supplementary_windows_290.py', 'supplementary290_launcher.py',
             'archive_p3_supplementary_290.py')
    return {('.cache/p3-full290-prep/' + name): sha(BASE / name) for name in names}


def validate_freeze(parent, check_live=True):
    if git('branch', '--show-current') != 'codex/p2-development' or git('rev-parse', 'HEAD') != parent:
        raise ValueError('Exact branch/current parent changed')
    data = json.loads(FREEZE.read_bytes())
    if data.get('section') != 290 or data.get('root_declared') is not True or data.get('parent_commit') != parent:
        raise ValueError('Root290 declaration/parent missing')
    if data.get('preparation_tools_sha256') != preparation_pins():
        raise ValueError('Reviewed preparation/controller bytes or their exact pin set changed')
    if check_live:
        live = runner_api_snapshot()
        if live['source_sha256'] != data['source_sha256'] or live['selectors'] != data['selectors']:
            raise ValueError('Root frozen source/complete selector union changed')
    if supplemental_public_inputs() != data.get('supplemental_public_inputs_sha256'):
        raise ValueError('Frozen supplemental public input set/bytes changed')
    return data


def safe_public_source(name):
    path = Path(name)
    if path.is_absolute() or '..' in path.parts or '\\' in name or path.as_posix() != name:
        raise ValueError('Unsafe public source path')
    if name != 'CORE_0.70_VERIFICATION.json' and (not path.parts or path.parts[0] not in ('rouge', 'tests', 'scripts') or path.suffix not in ('.py', '.json')):
        raise ValueError('Freeze source path outside maintained public scope')
    full = ROOT / path
    if full.is_symlink() or not full.resolve().is_relative_to(ROOT):
        raise ValueError('Public source link/escape refused')
    return full


def bound_bundles(parent):
    """Check actual explicit binding and tool maps, without starting any fixture."""
    result = {}
    for label in ('legacy', 'current'):
        folder = BASE / label
        path = folder / 'activation275.json'
        binding = json.loads(path.read_bytes())
        if (binding.get('status') != 'CURRENT290_SOURCE_BOUND_NOT_EXECUTED'
                or binding.get('binding_ready') is not True
                or binding.get('actual_section') != 290
                or binding.get('tested_worktree_parent_commit') != parent
                or binding.get('root_freeze_sha256') != sha(FREEZE)
                or binding.get('scope_not_reduced') is not True):
            raise ValueError('Reviewed final290 bundle is not genuinely bound: ' + label)
        for name, expected in binding['execution_tools_sha256'].items():
            relative = Path(name)
            full = folder / relative
            if (relative.is_absolute() or '..' in relative.parts or '\\' in name
                    or full.is_symlink() or not full.resolve().is_relative_to(folder)
                    or sha(full) != expected):
                raise ValueError('Bound tool path/bytes changed: ' + label + '/' + name)
        result[label] = {'activation_sha256': sha(path), 'binding': binding}
    return result


SUPPLEMENTAL_DIRECTORIES = (
    'research/p3-moving-reward-current',
    'research/p3-map-direct-road-288',
    'research/p3-event-named-rewards-289',
    'research/p3-choice-recruitment-290',
)
SUPPLEMENTAL_FILES = (
    'verification/sections/289-preparation/prior-288/rouge/node_catalog.py',
    'verification/sections/290-preparation/prior-289/rouge/event_planning.py',
)


def safe_supplemental_source(name):
    relative = Path(name)
    if (relative.is_absolute() or '..' in relative.parts or '\\' in name
            or relative.as_posix() != name
            or not (name in SUPPLEMENTAL_FILES
                    or any(name.startswith(directory + '/') for directory in SUPPLEMENTAL_DIRECTORIES))):
        raise ValueError('Supplemental public path outside exact approved scope')
    path = ROOT / relative
    if not path.is_file() or path.is_symlink() or not path.resolve().is_relative_to(ROOT):
        raise ValueError('Supplemental file missing, linked or escaped: ' + name)
    for parent in path.parents:
        if parent == ROOT:
            break
        if parent.is_symlink():
            raise ValueError('Supplemental parent must not be a symlink: ' + name)
    return path


def supplemental_public_inputs():
    """Exact regular public source packets, never private or arbitrary trees."""
    names = set(SUPPLEMENTAL_FILES)
    for name in SUPPLEMENTAL_DIRECTORIES:
        folder = ROOT / name
        if not folder.is_dir() or folder.is_symlink():
            raise ValueError('Required public source packet absent or linked: ' + name)
        for path in sorted(folder.rglob('*')):
            if path.is_symlink():
                raise ValueError('Linked public packet entry refused')
            if path.is_file():
                names.add(path.relative_to(ROOT).as_posix())
    return {name: sha(safe_supplemental_source(name)) for name in sorted(names)}
