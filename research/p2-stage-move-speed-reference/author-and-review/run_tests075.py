from pathlib import Path
import argparse, datetime, hashlib, importlib.util, io, json, subprocess, sys, tarfile, unittest

base = Path(__file__).parent
parser = argparse.ArgumentParser()
parser.add_argument('--related', action='store_true')
args = parser.parse_args()
package = base / 'draft075'
sys.path.insert(0, str(package))
sources = ('rouge/spawn_reference.py', 'rouge/battle_preview.py')
start = {name: hashlib.sha256((package / name).read_bytes()).hexdigest() for name in sources}
test_path = base / 'test_stage_move_speed_reference.py'
spec = importlib.util.spec_from_file_location('test_stage_move_speed_reference', test_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
suite = unittest.TestSuite() if args.related else unittest.defaultTestLoader.loadTestsFromModule(module)
skips = []
if args.related:
    related = base / 'fixedtests075'
    files = ('tests/test_spawn_reference_040.py', 'tests/test_battle_preview_039.py',
             'tests/test_enemy_environment.py', 'tests/test_enemy_rune_selectors.py')
    if not related.exists():
        related.mkdir()
        raw = subprocess.check_output(['git', 'archive', 'dbf1e698f56cbba03793ed13769a9f6dae2c5ff6', *files],
                                      cwd='/workspace/rougezhushou')
        with tarfile.open(fileobj=io.BytesIO(raw)) as archive:
            archive.extractall(related, filter='data')
        receipt = {'frozen_commit': 'dbf1e698f56cbba03793ed13769a9f6dae2c5ff6',
                   'method': 'git archive exact committed test paths; no root WIP',
                   'files': {name: {'sha256': hashlib.sha256((related / name).read_bytes()).hexdigest(),
                                    'bytes': (related / name).stat().st_size} for name in files}}
        (base / 'related-tests-freeze075.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
    for name in files:
        spec = importlib.util.spec_from_file_location(Path(name).stem, related / name)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        # Public frozen tests require some old noncommitted fixtures. Do not
        # replace them with fabricated data or current private screenshots.
        unavailable = {
            'test_all_options_and_extra_routes_match_pinned_levels': related / '.cache/game-data/levels',
            'test_all_images_match_pinned_receipt': related / '.cache/research/battle-039/image-receipt.json',
            'test_visible_region_updates_and_survives_partial_pages_and_restart': related / 'samples/native-client/run-map-empty.png',
        }
        for cls in vars(module).values():
            if not isinstance(cls, type) or not issubclass(cls, unittest.TestCase):
                continue
            for method, fixture in unavailable.items():
                if hasattr(cls, method) and not fixture.exists():
                    skips.append({'test': cls.__name__ + '.' + method,
                                  'required_unavailable_public_fixture': str(fixture),
                                  'not_rebuilt_or_replaced': True})
                    setattr(cls, method, unittest.skip('固定提交不包含此旧公开夹具；不重建或替换。')(getattr(cls, method)))
        suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(module))
result = unittest.TextTestRunner(verbosity=2).run(suite)
end = {name: hashlib.sha256((package / name).read_bytes()).hexdigest() for name in sources}
out = {'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'related': args.related,
       'run': result.testsRun, 'passed': result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped),
       'failures': len(result.failures), 'errors': len(result.errors), 'skipped': len(result.skipped),
       'explicit_unavailable_old_public_fixtures': skips, 'source_start_sha256': start,
       'source_end_sha256': end, 'sources_unchanged': start == end,
       'available_checks_passed': result.wasSuccessful()}
(base / ('related-tests075.json' if args.related else 'new-tests075.json')).write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
print(out)
assert start == end and result.wasSuccessful()
