"""Fresh320 guards. Importing this module never starts a test, Qt or a window."""
from pathlib import Path, PurePosixPath
from hashlib import sha256
from datetime import datetime, timezone
import json
import subprocess
import sys

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
PYTHON = ROOT / '.venv/Scripts/python.exe'
FREEZE = ROOT / 'verification/full-320/source-freeze-attempt1.json'
READY_PATH = BASE / 'CONTROLLER_READY320.json'


def sha(path): return sha256(path.read_bytes()).hexdigest()
def now(): return datetime.now(timezone.utc).isoformat()


def write_new(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as stream:
        stream.write((json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf8'))


def git(*args): return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()


def native():
    if sys.platform != 'win32' or Path(sys.executable).resolve() != PYTHON.resolve():
        raise ValueError('Use the exact project native Windows Python; no Wine/offscreen GUI substitute.')


def public(name):
    if type(name) is not str: raise ValueError('Public relative path must be text.')
    relative = PurePosixPath(name)
    if relative.is_absolute() or '..' in relative.parts or '\\' in name or ':' in name or relative.as_posix() != name:
        raise ValueError('Unsafe public relative source path: ' + name)
    if relative.parts[0] not in ('rouge', 'scripts', 'tests', 'research', 'verification') and name != 'CORE_0.70_VERIFICATION.json':
        raise ValueError('Private, cache and document sources cannot enter the standard source map: ' + name)
    path = ROOT.joinpath(*relative.parts)
    if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(ROOT.resolve()):
        raise ValueError('Regular existing public source required: ' + name)
    for parent in path.parents:
        if parent == ROOT: break
        if parent.is_symlink(): raise ValueError('Linked public parent refused: ' + name)
    return path


def runner_snapshot():
    path = public('scripts/verify_full_available.py'); raw = path.read_bytes()
    api = {'__file__': str(path), '__name__': '_maintained320_source_api_only'}
    sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / 'scripts'))
    exec(compile(raw, str(path), 'exec'), api)
    if not callable(api.get('maintained_selectors')):
        raise ValueError('Root must promote reviewed maintained_selectors() and all post290 modules before freeze.')
    selectors = api['maintained_selectors']()
    sources = api['source_hashes']()
    if type(selectors) is not list or len(selectors) != len(set(selectors)) or path.read_bytes() != raw:
        raise ValueError('Maintained selector API/source changed.')
    return {'selectors': selectors, 'source_sha256': sources,
            'maintained_runner_sha256': sha256(raw).hexdigest(),
            'cloud_selector_api_sha256': sha(public('scripts/verify_cloud.py'))}


def native_source_snapshot():
    result = {}
    for name in ('rouge', 'tests', 'scripts'):
        for path in sorted((ROOT / name).rglob('*')):
            relative = path.relative_to(ROOT)
            if '__pycache__' in relative.parts or path.suffix not in ('.py', '.json'): continue
            if path.is_symlink(): raise ValueError('Native maintained source link refused.')
            if path.is_file(): result[relative.as_posix()] = sha(path)
    return dict(sorted(result.items()))


def tool_pins():
    ready = json.loads(READY_PATH.read_bytes())
    if ready.get('kind') != 'FULL320_CONTROLLER_CACHE_READY_NOT_EXECUTED': raise ValueError('Reviewed controller READY required.')
    for relative, expected in ready['files'].items():
        path = BASE / relative
        if path.is_symlink() or not path.resolve().is_relative_to(BASE) or sha(path) != expected['sha256'] or path.stat().st_size != expected['bytes']:
            raise ValueError('Reviewed320 preparation tool drift: ' + relative)
    return ready


def input_bindings(bindings):
    """Only explicit original public replay/tool paths; never discover private state."""
    observed = {}
    for row in bindings:
        local = row['local_path']; counterpart = row['public_path']
        if not local.startswith('.cache/') or any(part in ('..', '.local', '.private') for part in PurePosixPath(local).parts):
            raise ValueError('Only explicit known public cache dependencies may be dual-bound.')
        path = ROOT / local
        if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(ROOT):
            raise ValueError('Missing original public local input: ' + local)
        other = public(counterpart)
        if sha(path) != row['sha256'] or sha(other) != row['sha256'] or path.stat().st_size != row['bytes'] or other.stat().st_size != row['bytes']:
            raise ValueError('Actual local/public source pair differs: ' + local)
        observed[local] = sha(path)
    return observed


def validate_freeze(parent, freeze_sha):
    native(); ready = tool_pins()
    if git('branch', '--show-current') != 'codex/p2-development' or git('rev-parse', 'HEAD') != parent:
        raise ValueError('Actual parent/branch changed.')
    if sha(FREEZE) != freeze_sha: raise ValueError('Exact root-declared320 freeze required.')
    data = json.loads(FREEZE.read_bytes())
    if data.get('section') != 320 or data.get('root_declared') is not True or data.get('parent_commit') != parent:
        raise ValueError('Wrong320 input declaration.')
    if data['preparation_ready_sha256'] != sha(READY_PATH):
        raise ValueError('Freeze preparation authority changed.')
    for reference in data['functional_validation'].values():
        if sha(public(reference['path'])) != reference['sha256']:
            raise ValueError('Original root final320 functional receipt changed.')
    actual = runner_snapshot()
    for key in ('selectors', 'source_sha256', 'maintained_runner_sha256', 'cloud_selector_api_sha256'):
        if actual[key] != data[key]: raise ValueError('Fresh complete maintained scope drift: ' + key)
    if native_source_snapshot() != data['legacy_native_source_sha256']:
        raise ValueError('Complete current native source map drift.')
    for name, expected in data['supplemental_public_inputs_sha256'].items():
        if sha(public(name)) != expected: raise ValueError('Supplemental public input drift: ' + name)
    if input_bindings(data['local_public_input_bindings']) != data['local_public_input_sha256']:
        raise ValueError('Original local/public replay input set changed.')
    for name, expected in data['legacy_external_additional_sha256'].items():
        path = ROOT / name
        if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(ROOT) or sha(path) != expected:
            raise ValueError('Explicit original legacy dependency drift: ' + name)
    for mode, expected in data['template_bundle_sha256'].items():
        for name, value in expected.items():
            if sha(BASE / ('template-' + mode) / name) != value: raise ValueError('Immutable320 template drift.')
    return data


def bound(parent, freeze_sha, activation_sha):
    data = validate_freeze(parent, freeze_sha)
    path = BASE / 'activation320.json'
    if sha(path) != activation_sha: raise ValueError('Root activation changed.')
    activation = json.loads(path.read_bytes())
    if activation.get('status') != 'CURRENT320_SOURCE_BOUND_NOT_EXECUTED' or activation['root_freeze_sha256'] != freeze_sha:
        raise ValueError('320 input binding is inactive/wrong freeze.')
    for mode, values in activation['bundles'].items():
        folder = BASE / ('bound-' + mode)
        for name, expected in values['execution_tools_sha256'].items():
            if sha(folder / name) != expected: raise ValueError('Bound320 executed tool drift: ' + mode + '/' + name)
        if sha(folder / 'activation320.json') != values['activation_sha256']: raise ValueError('Child activation changed.')
    return data, activation
