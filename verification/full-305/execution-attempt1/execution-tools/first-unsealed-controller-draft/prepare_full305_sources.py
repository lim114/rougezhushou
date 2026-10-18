"""Prepare independent exact305 cache sources only; no freeze/activation/tests/Qt."""
from pathlib import Path
from hashlib import sha256
import argparse
import ast
import difflib
import json

ROOT = Path(__file__).resolve().parents[2]
BASE = Path(__file__).resolve().parent
LEGACY_SOURCE = 'verification/full-290/legacy-retry-attempt4/executed-legacy-bundle'
CURRENT_SOURCE = 'verification/full-290/execution-attempt2/executed-tools/current'
LEGACY_ACTIVATION = 'verification/full-290/legacy-retry-attempt4/activation-final-A3.json'
CURRENT_ACTIVATION = CURRENT_SOURCE + '/activation275.json'


def pin(path):
    raw = path.read_bytes(); return {'sha256': sha256(raw).hexdigest(), 'bytes': len(raw)}


def write_new(path, raw):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as stream: stream.write(raw)


def encoded(value): return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf8')


def assertions(text):
    return [ast.dump(node, include_attributes=False) for node in sorted(
        (node for node in ast.walk(ast.parse(text)) if isinstance(node, ast.Assert)), key=lambda node: (node.lineno, node.col_offset))]


def named_node(text, name):
    return next(node for node in ast.parse(text).body if isinstance(node, (ast.ClassDef, ast.FunctionDef)) and node.name == name)


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    if not args.prepare_only: raise ValueError('Explicit cache preparation action required.')
    if (BASE / 'prepared-inputs.json').exists(): raise FileExistsError('Preserve first prepared packet; use a new revision for changes.')
    plan = json.loads((BASE / 'PLAN.json').read_bytes())
    source_text = (ROOT / 'scripts/verify_full_available.py').read_text(encoding='utf8')
    additions = plan['missing_new_modules_from_current_maintained_union']
    marker = '\n\ndef source_hashes():'
    assert source_text.count(marker) == 1
    assignment = '\n\n# Complete post290 modules append after the preserved original selector union.\nADDITIONAL_MODULES = ' + repr(tuple(additions))
    candidate = source_text.replace(marker, assignment + marker, 1)
    old = "    from verify_cloud import MODULES\n    selectors = list(dict.fromkeys(historical['test_modules'] + list(NEW_MODULES) + list(MODULES)))"
    assert candidate.count(old) == 1
    candidate = candidate.replace(old, '    selectors = maintained_selectors()', 1)
    helper = """\n\ndef maintained_selectors():
    \"\"\"Original maintained ordered union, then all explicit post290 additions.\"\"\"
    historical = json.loads((ROOT / 'CORE_0.70_VERIFICATION.json').read_bytes())
    from verify_cloud import MODULES
    original = list(dict.fromkeys(historical['test_modules'] + list(NEW_MODULES) + list(MODULES)))
    return list(dict.fromkeys(original + list(ADDITIONAL_MODULES)))
"""
    candidate = candidate.replace('\n\ndef main():', helper + '\n\ndef main():', 1)
    for name in ('source_hashes', 'AvailableResult', 'probe_windows_symlink_prerequisite'):
        assert ast.dump(named_node(source_text, name), include_attributes=False) == ast.dump(named_node(candidate, name), include_attributes=False)
    write_new(BASE / 'candidate/scripts/verify_full_available.py', candidate.encode('utf8'))
    write_new(BASE / 'maintained-runner.diff', ''.join(difflib.unified_diff(source_text.splitlines(True), candidate.splitlines(True), fromfile='original', tofile='candidate')).encode('utf8'))
    observed_source = ROOT / 'verification/full-290/execution-attempt2/controller-tools/run_full290_orchestration.py'
    observed_text = observed_source.read_text(encoding='utf8'); tree = ast.parse(observed_text)
    header = '"""Exact actual290 observed-Popen/job helpers; no invocation at import."""\nimport json,os,subprocess,time,traceback\nfrom full305_common import ROOT,now,sha,write_new\n\n'
    functions = []
    extracted = {}
    for name in ('checkpoint', 'execute_observed', 'terminal_job_record'):
        node = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == name)
        body = ast.get_source_segment(observed_text, node)
        functions.append(body); extracted[name] = sha256(body.encode('utf8')).hexdigest()
    write_new(BASE / 'execution305.py', (header + '\n\n'.join(functions) + '\n').encode('utf8'))
    supervisor = ROOT / 'verification/full-290/legacy-retry-attempt4/execution-tools/supervisor3690.py'
    assert pin(supervisor)['sha256'] == 'b073d86b1ddb6d697278380e34b29fd3887a8ea14448f29ffd8a8852dc4b2309'
    write_new(BASE / 'supervisor305.py', supervisor.read_bytes())
    templates = {}; original_refs = {}
    for mode, authority, folder in (('legacy', LEGACY_ACTIVATION, LEGACY_SOURCE), ('current', CURRENT_ACTIVATION, CURRENT_SOURCE)):
        activation = json.loads((ROOT / authority).read_bytes()); entries = activation['execution_tools_sha256']
        expected_count = 84 if mode == 'legacy' else 18
        assert len(entries) == expected_count
        values = {}
        for relative, expected in entries.items():
            source = ROOT / folder / relative
            assert source.is_file() and not source.is_symlink() and pin(source)['sha256'] == expected
            write_new(BASE / ('template-' + mode) / relative, source.read_bytes())
            values[relative] = expected
            original_refs[source.relative_to(ROOT).as_posix()] = pin(source)
        templates[mode] = values
    original294 = (ROOT / 'scripts/verify_direct_map_window_294.py').read_text(encoding='utf8')
    adapted294 = original294.replace("CANONICAL='scripts/verify_direct_map_window_294.py'", "CANONICAL='scripts/verify_direct_map_window_294_full305.py'", 1)
    old_guard = "    if sha(ROOT/'rouge/data/fixed-landmark-references.json')!=comparison['output_sha256']:\n        raise ValueError('Actual compared runtime output bytes changed.')"
    replacement = """    #305: current107 dataset must preserve the complete original58 records;
    # the old18 accepted source observations and every UI assertion stay intact.
    if sha(ROOT/'rouge/data/fixed-landmark-references.json')!='dc43bbbe70eab6f11cc8661c3bfeab994000ea614ea0f8c999a596f5cb2c445a':
        raise ValueError('Reviewed current107 direct dataset changed.')
    old58_path=ROOT/'research/p3-map-direct-ground-303/prior-direct-references.json'
    if sha(old58_path)!=comparison['output_sha256'] or comparison['output_sha256']!='63ec9488f8f905d2ced1a4e349413e9c92d78125b9f1c94c00293cafa4d348f5':
        raise ValueError('Original compared58 complete output authority changed.')
    old58=read(old58_path)
    if any(runtime[group].get(key)!=value for group in('references','stages')for key,value in old58[group].items()):
        raise ValueError('Original58 full records changed in current107 dataset.')"""
    assert adapted294.count(old_guard) == 1
    adapted294 = adapted294.replace(old_guard, replacement, 1)
    old_names = "    names={CANONICAL,'rouge/app.py'"
    assert adapted294.count(old_names) == 1
    adapted294 = adapted294.replace(old_names, "    names={CANONICAL,'research/p3-map-direct-ground-303/prior-direct-references.json','rouge/app.py'", 1)
    assert assertions(original294) == assertions(adapted294)
    write_new(BASE / 'candidate/scripts/verify_direct_map_window_294_full305.py', adapted294.encode('utf8'))
    write_new(BASE / 'native294-adaptation.diff', ''.join(difflib.unified_diff(original294.splitlines(True), adapted294.splitlines(True), fromfile='original294', tofile='current305')).encode('utf8'))
    original304 = (ROOT / 'scripts/verify_curiosity_node_rules_window_304.py').read_text(encoding='utf8')
    adapted304 = original304.replace("CANONICAL = 'scripts/verify_curiosity_node_rules_window_304.py'", "CANONICAL = 'scripts/verify_curiosity_node_rules_window_304_full305.py'", 1)
    helper304 = """\n\ndef _fresh305_parent_pin():
    freeze=read(ROOT/'verification/full-305/source-freeze.json')
    if freeze.get('section')!=305 or freeze.get('root_declared')is not True:
        raise ValueError('Actual305 declared source input required for this parent compatibility pin.')
    expected=freeze['source_sha256']['rouge/node_catalog_view.py']
    if sha(ROOT/'rouge/node_catalog_view.py')!=expected:
        raise ValueError('Fresh305 parent source differs from its declared pin.')
    return expected
"""
    adapted304 = adapted304.replace('\n\ndef main():', helper304 + '\n\ndef main():', 1)
    marker304 = '    args = parser.parse_args()'
    assert adapted304.count(marker304) == 1
    adapted304 = adapted304.replace(marker304, marker304 + "\n    EXPECTED_SOURCE_PINS['rouge/node_catalog_view.py'] = _fresh305_parent_pin()", 1)
    assert assertions(original304) == assertions(adapted304)
    write_new(BASE / 'candidate/scripts/verify_curiosity_node_rules_window_304_full305.py', adapted304.encode('utf8'))
    write_new(BASE / 'native304-adaptation.diff', ''.join(difflib.unified_diff(original304.splitlines(True), adapted304.splitlines(True), fromfile='original304', tofile='current305')).encode('utf8'))
    pin_audit = []
    scripts = {}
    old_receipts = json.loads((ROOT / 'verification/full-290/summary.json').read_bytes())['p3_supplementary_windows']
    for path in sorted((ROOT / 'scripts').glob('verify_*_window_*.py')):
        try: section = int(path.stem.rsplit('_', 1)[1])
        except ValueError: continue
        if not 286 <= section <= 304: continue
        scripts['p3_' + str(section)] = path.relative_to(ROOT).as_posix()
        tree = ast.parse(path.read_bytes())
        for node in tree.body:
            if not isinstance(node, ast.Assign): continue
            try: value = ast.literal_eval(node.value)
            except (ValueError, TypeError): continue
            if not isinstance(value, dict): continue
            for relative, expected in value.items():
                if type(relative)is not str or '/' not in relative: continue
                digest = expected if type(expected)is str else expected.get('sha256')if isinstance(expected,dict)else None
                if type(digest)is not str or len(digest)!=64: continue
                source = ROOT / relative
                if source.is_file():
                    actual = pin(source)['sha256']
                    if actual != digest:
                        pin_audit.append({'script': path.relative_to(ROOT).as_posix(), 'source': relative,
                                          'expected_sha256': digest, 'current_sha256': actual,
                                          'changed_by_preparation': False})
    assert len(scripts) == 19
    scripts['p3_294'] = 'scripts/verify_direct_map_window_294_full305.py'
    scripts['p3_304'] = 'scripts/verify_curiosity_node_rules_window_304_full305.py'
    record = {'section': 305, 'kind': 'EXACT_CACHE_TEMPLATES_AND_CANDIDATE_ADAPTATIONS_NOT_FROZEN_OR_EXECUTED',
              'template_bundle_sha256': templates, 'original_public_tool_references': original_refs,
              'observed_helpers_source': {'path': observed_source.relative_to(ROOT).as_posix(), **pin(observed_source)},
              'exact_extracted_function_sha256': extracted, 'p3_scripts': scripts,
              'prior_p3_actual_receipts_for_scope_only': {key: value['receipt'] for key, value in old_receipts.items()},
              'missing_new_modules': additions,
              'public_promote_candidates': {path.relative_to(BASE / 'candidate').as_posix(): pin(path) for path in sorted((BASE / 'candidate/scripts').glob('*.py'))},
              'known_static_pin_mismatches_not_guessed_repairs': pin_audit,
              '305_native_and_modules_pending_root_final_binding': True,
              'legacy_internal_watchdogs_from_actual_success': 3600,
              'actual_sourcefreeze_activation_tests_Qt_windows_Git_or_private_actions': False}
    write_new(BASE / 'prepared-inputs.json', encoded(record))
    print(json.dumps({'prepared': str(BASE / 'prepared-inputs.json'), **pin(BASE / 'prepared-inputs.json'),
                      'legacy_tools': len(templates['legacy']), 'current_tools': len(templates['current']),
                      'canonical_scripts': len(scripts), 'static_pin_mismatches': pin_audit,
                      'candidate_promote': record['public_promote_candidates'], 'actual_tests_or_Qt': False}, ensure_ascii=False))


if __name__ == '__main__': main()
