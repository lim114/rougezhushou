"""Fresh410 guards. Importing this module never starts a test, Qt or a window."""
from pathlib import Path, PurePosixPath
from hashlib import sha256
from datetime import datetime, timezone
import json
import subprocess
import sys

BASE = Path(__file__).resolve().parent
ROOT = next(path for path in BASE.parents if (path / 'rouge/app.py').is_file())
PYTHON = ROOT / '.venv/Scripts/python.exe'
CAPSULE = json.loads((BASE / 'capsule410.json').read_bytes())
ATTEMPT = CAPSULE['attempt']
if type(ATTEMPT) is not int or ATTEMPT < 1: raise ValueError('Explicit positive root attempt required.')
FREEZE = ROOT / 'verification/full-410' / ('source-freeze-attempt' + str(ATTEMPT) + '.json')
READY_PATH = BASE / 'CONTROLLER_READY410.json'


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



# Exactly five original public game-data inputs selected only by canonical369.
# Generic public() remains unchanged and continues to reject every cache path.
CANONICAL_LOCAL_PUBLIC_INPUT_BINDINGS = [{'mode': 'p3_369', 'canonical_script': 'scripts/verify_current_boss_documents_window_369.py', 'local_path': '.cache/game-data/levels/enemydata/enemy_database.json', 'public_path': 'verification/full-410/explicit-public-build-inputs/f8dd03997d0e3eae65cc4b77bcb6b5ef198488504f738defc31cad5e13c3680c.json', 'sha256': 'f8dd03997d0e3eae65cc4b77bcb6b5ef198488504f738defc31cad5e13c3680c', 'bytes': 15022043, 'origin_manifests': [{'path': 'research/p3-boss-phase-309/source-manifest.json', 'sha256': 'ae8448916f2b8355e0d946f95d4e6748fcaa2a74838e9949794e7485b18b036d', 'bytes': 4332, 'json_pointer': '/build_authority_files/.cache~1game-data~1levels~1enemydata~1enemy_database.json'}, {'path': 'research/p3-boss-cycle-310/source-manifest.json', 'sha256': 'cddc4465769edd6e74a231838ea325a895562665bee5e2283f6c20880b1e8052', 'bytes': 6015, 'json_pointer': '/build_authority_files/.cache~1game-data~1levels~1enemydata~1enemy_database.json'}, {'path': 'research/p3-boss-hunt-311/source-manifest.json', 'sha256': 'dc1024855751338d2b4b536c53c83e8cd56e75f548b12296dfa34d3b12335321', 'bytes': 5912, 'json_pointer': '/build_authority_files/.cache~1game-data~1levels~1enemydata~1enemy_database.json'}]}, {'mode': 'p3_369', 'canonical_script': 'scripts/verify_current_boss_documents_window_369.py', 'local_path': '.cache/game-data/levels/obt/roguelike/ro6/level_rogue6_b-4-b.json', 'public_path': 'research/p3-auxiliary-mechanisms/level_rogue6_b-4-b.json', 'sha256': 'fc2f7ae7371829259bd445a45704d79f30f84094f8eedbfa74b026fe075c51ea', 'bytes': 202372, 'origin_manifests': [{'path': 'research/p3-boss-hunt-311/source-manifest.json', 'sha256': 'dc1024855751338d2b4b536c53c83e8cd56e75f548b12296dfa34d3b12335321', 'bytes': 5912, 'json_pointer': '/build_authority_files/.cache~1game-data~1levels~1obt~1roguelike~1ro6~1level_rogue6_b-4-b.json'}]}, {'mode': 'p3_369', 'canonical_script': 'scripts/verify_current_boss_documents_window_369.py', 'local_path': '.cache/game-data/levels/obt/roguelike/ro6/level_rogue6_b-4.json', 'public_path': 'verification/full-410/explicit-public-build-inputs/1161795429a9dd4f36b6fcf4e6cf5b6300e2bcce6f04a860e9f7b31e6619d292.json', 'sha256': '1161795429a9dd4f36b6fcf4e6cf5b6300e2bcce6f04a860e9f7b31e6619d292', 'bytes': 207445, 'origin_manifests': [{'path': 'research/p3-boss-hunt-311/source-manifest.json', 'sha256': 'dc1024855751338d2b4b536c53c83e8cd56e75f548b12296dfa34d3b12335321', 'bytes': 5912, 'json_pointer': '/build_authority_files/.cache~1game-data~1levels~1obt~1roguelike~1ro6~1level_rogue6_b-4.json'}]}, {'mode': 'p3_369', 'canonical_script': 'scripts/verify_current_boss_documents_window_369.py', 'local_path': '.cache/game-data/levels/obt/roguelike/ro6/level_rogue6_b-5.json', 'public_path': 'verification/full-410/explicit-public-build-inputs/aec26f5d1146281bdc50b73d0c88ce99c37c07c3bd6361ed2af8980ce53c1faf.json', 'sha256': 'aec26f5d1146281bdc50b73d0c88ce99c37c07c3bd6361ed2af8980ce53c1faf', 'bytes': 205518, 'origin_manifests': [{'path': 'research/p3-boss-cycle-310/source-manifest.json', 'sha256': 'cddc4465769edd6e74a231838ea325a895562665bee5e2283f6c20880b1e8052', 'bytes': 6015, 'json_pointer': '/build_authority_files/.cache~1game-data~1levels~1obt~1roguelike~1ro6~1level_rogue6_b-5.json'}]}, {'mode': 'p3_369', 'canonical_script': 'scripts/verify_current_boss_documents_window_369.py', 'local_path': '.cache/game-data/levels/obt/roguelike/ro6/level_rogue6_b-6.json', 'public_path': 'research/p3-spawn-candidates-299/levels/57db7782a27808e0187f1fbaf41c3886a85e7687d40dc451281846d4297efad9.json', 'sha256': '57db7782a27808e0187f1fbaf41c3886a85e7687d40dc451281846d4297efad9', 'bytes': 165191, 'origin_manifests': [{'path': 'research/p3-boss-phase-309/source-manifest.json', 'sha256': 'ae8448916f2b8355e0d946f95d4e6748fcaa2a74838e9949794e7485b18b036d', 'bytes': 4332, 'json_pointer': '/build_authority_files/.cache~1game-data~1levels~1obt~1roguelike~1ro6~1level_rogue6_b-6.json'}]}]


def canonical_binding_plan():
    return json.loads(json.dumps(CANONICAL_LOCAL_PUBLIC_INPUT_BINDINGS))


def canonical_local_path(name, mode):
    rows = {row['local_path']: row for row in CANONICAL_LOCAL_PUBLIC_INPUT_BINDINGS}
    if mode != 'p3_369' or name not in rows:
        raise ValueError('Only the exact five canonical369 local public originals are permitted.')
    path = ROOT / name
    if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(ROOT.resolve()):
        raise ValueError('Exact regular canonical369 local original required: ' + name)
    for parent in path.parents:
        if parent == ROOT: break
        if parent.is_symlink(): raise ValueError('Linked canonical369 local parent refused.')
    return path


def canonical_selected_source(name, mode=None):
    if name.startswith('.cache/'):
        return canonical_local_path(name, mode)
    return public(name)


def canonical_inputs(bindings, selected_paths=None):
    if bindings != CANONICAL_LOCAL_PUBLIC_INPUT_BINDINGS:
        raise ValueError('Exact original five canonical369 bindings/order/provenance required.')
    expected_names = {row['local_path'] for row in CANONICAL_LOCAL_PUBLIC_INPUT_BINDINGS}
    if selected_paths is not None:
        actual = {(mode, name) for mode, names in selected_paths.items() for name in names if name.startswith('.cache/')}
        if actual != {('p3_369', name) for name in expected_names}:
            raise ValueError('Local originals must remain selected exactly by369, never other workflows.')
    observed = {}
    for row in bindings:
        local = canonical_local_path(row['local_path'], row['mode']); other = public(row['public_path'])
        for origin in row['origin_manifests']:
            authority = public(origin['path'])
            if sha(authority) != origin['sha256'] or authority.stat().st_size != origin['bytes']:
                raise ValueError('Original canonical build authority manifest drift: ' + origin['path'])
            document = json.loads(authority.read_bytes())
            if document['build_authority_files'].get(row['local_path']) != {'sha256': row['sha256'], 'bytes': row['bytes']}:
                raise ValueError('Exact canonical original manifest entry changed.')
            expected_pointer = '/build_authority_files/' + row['local_path'].replace('~','~0').replace('/','~1')
            if origin['json_pointer'] != expected_pointer:
                raise ValueError('Original canonical authority pointer changed.')
        local_raw = local.read_bytes(); public_raw = other.read_bytes()
        if (len(local_raw) != row['bytes'] or len(public_raw) != row['bytes']
                or sha256(local_raw).hexdigest() != row['sha256'] or sha256(public_raw).hexdigest() != row['sha256']
                or local_raw != public_raw):
            raise ValueError('Exact whole canonical local/public input bytes differ: ' + row['local_path'])
        observed[row['local_path']] = row['sha256']
    return observed


def canonical_frozen_inputs(data):
    observed = canonical_inputs(data.get('canonical_local_public_input_bindings'), data['p3_script_selected_paths'])
    if observed != data.get('canonical_local_public_input_sha256'):
        raise ValueError('Frozen exact canonical369 local source map differs.')
    for row in CANONICAL_LOCAL_PUBLIC_INPUT_BINDINGS:
        if data['supplemental_public_inputs_sha256'].get(row['public_path']) != row['sha256']:
            raise ValueError('Exact canonical public counterpart absent from supplemental range.')
    return observed


def runner_snapshot():
    path = public('scripts/verify_full_available.py'); raw = path.read_bytes()
    api = {'__file__': str(path), '__name__': '_maintained410_source_api_only'}
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
    if ready.get('kind') != 'FULL410_CONTROLLER_CACHE_READY_NOT_EXECUTED': raise ValueError('Reviewed controller READY required.')
    for relative, expected in ready['files'].items():
        path = BASE / relative
        if path.is_symlink() or not path.resolve().is_relative_to(BASE) or sha(path) != expected['sha256'] or path.stat().st_size != expected['bytes']:
            raise ValueError('Reviewed410 preparation tool drift: ' + relative)
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
    if sha(FREEZE) != freeze_sha: raise ValueError('Exact root-declared410 freeze required.')
    data = json.loads(FREEZE.read_bytes())
    if data.get('section') != 410 or data.get('root_declared') is not True or data.get('parent_commit') != parent:
        raise ValueError('Wrong410 input declaration.')
    if data.get('actual_validation_attempt') != ATTEMPT: raise ValueError('Wrong actual attempt.')
    if data['preparation_ready_sha256'] != sha(READY_PATH):
        raise ValueError('Freeze preparation authority changed.')
    for reference in data['functional_validation'].values():
        if sha(public(reference['path'])) != reference['sha256']:
            raise ValueError('Original root final410 functional receipt changed.')
    expected_diagnostic=['legacy','current30','current29',*[mode for mode in data['p3_scripts'] if int(mode.split('_')[1])<=380]]
    if data.get('diagnostic_layout_modes')!=expected_diagnostic or data.get('diagnostic_layout_is_not_default_player_UI_coverage')is not True:raise ValueError('Explicit old-layout compatibility scope differs.')
    canonical_frozen_inputs(data)
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
            if sha(BASE / ('template-' + mode) / name) != value: raise ValueError('Immutable410 template drift.')
    return data


def bound(parent, freeze_sha, activation_sha):
    data = validate_freeze(parent, freeze_sha)
    path = BASE / 'activation410.json'
    if sha(path) != activation_sha: raise ValueError('Root activation changed.')
    activation = json.loads(path.read_bytes())
    if activation.get('status') != 'CURRENT410_SOURCE_BOUND_NOT_EXECUTED' or activation['root_freeze_sha256'] != freeze_sha:
        raise ValueError('410 input binding is inactive/wrong freeze.')
    for mode, values in activation['bundles'].items():
        folder = BASE / ('bound-' + mode)
        for name, expected in values['execution_tools_sha256'].items():
            if sha(folder / name) != expected: raise ValueError('Bound410 executed tool drift: ' + mode + '/' + name)
        if sha(folder / 'activation410.json') != values['activation_sha256']: raise ValueError('Child activation changed.')
    return data, activation
