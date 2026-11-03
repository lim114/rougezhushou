"""Source-prepared metadata sealer. Root alone may execute after Source review.

Never import/execute authored helpers, codecs, project, tests, Wine or Git.
Bind only actual physical Root-final context/binding/prelaunch references and
write one exclusive Source-only FINAL evidence helper packet with byte inverses.
"""
import argparse
import ast
import base64
import hashlib
import json
import re
import stat
from pathlib import Path

BASE = Path('/workspace/.continuation')
OUTPUT = BASE / 'full095-ui-identity-evidence-final-v1'
CONTEXT = BASE / 'full095-regression-ui-identity-resume-final-v1'
BINDING = CONTEXT / 'actual-full095-source-binding.json'
PRELAUNCH = BASE / 'root-full095-ui-identity-retry-v1-prelaunch.json'
PACKETS = {
    'acceptance': {'directory': 'full095-actual-acceptance-ui-identity-source-v1',
                   'manifest_sha256': 'b6c1485e7c89ade2e577920279fa015c572bd6486276388942991d1078d371cd',
                   'file': 'assemble_actual_acceptance095.py'},
    'archive': {'directory': 'full095-archive-ui-identity-spec-source-v2',
                'manifest_sha256': '0672576bf7d64e326eb67f3961f3c11dbb97f16a2d2e728aac2918dc013a037d',
                'file': 'assemble_archive_spec095.py'},
    'reviewer': {'directory': 'full095-ui-identity-archive-final-review-source-v1',
                 'manifest_sha256': '6dfa425755431dd4d1af8512b3eeb132b6b2f8fa295cf0ba353a92941a1bf689',
                 'file': 'review_actual_archive_spec095.py'},
}
CHECKED = {}


def demand(value, message):
    if not value:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def reference(path, expected=None):
    p = Path(path)
    demand(p.is_absolute() and str(p.resolve(strict=True)) == str(p)
           and not p.is_symlink() and stat.S_ISREG(p.lstat().st_mode), 'Canonical regular actual input required')
    raw = p.read_bytes()
    full = {'path': str(p), 'bytes': len(raw), 'sha256': sha(raw)}
    if expected is not None:
        demand(type(expected) is dict and full == expected, 'Actual immutable file_ref differs: ' + str(p))
    demand(str(p) not in CHECKED or CHECKED[str(p)] == full, 'Input changed during Source seal')
    CHECKED[str(p)] = full
    return full


def document(path, expected=None):
    full = reference(path, expected)
    return json.loads(Path(path).read_bytes()), full


def write(path, raw):
    with path.open('xb') as stream:
        stream.write(raw)


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode('utf-8')


def source_packet(packet):
    folder = BASE / packet['directory']
    mf_path = folder / 'public-artifacts-manifest-source-preparation095.json'
    mf, mf_ref = document(mf_path)
    demand(mf_ref['sha256'] == packet['manifest_sha256'] and mf['STOPWRITE'] is True
           and mf['runtime_pass'] is False and mf['target_execution_calls'] == 0,
           'Exact frozen SOURCE packet required')
    for name, row in mf['files'].items():
        demand(Path(name).name == name and row['path'] == str(folder / name), 'Source payload path differs')
        reference(row['path'], row)
    hand, hand_ref = document(folder / 'handoff-source-preparation095.json')
    demand(hand['manifest'] == mf_ref and hand['runtime_calls'] == 0, 'Source handoff binding differs')
    return folder, mf_ref, hand_ref


def replacement(raw, before, after):
    before, after = before.encode('utf-8'), after.encode('utf-8')
    demand(raw.count(before) == 1, 'One exact Source placeholder required')
    start = raw.index(before)
    candidate = raw[:start] + after + raw[start + len(before):]
    operation = {'pending_byte_start': start, 'pending_byte_count': len(after),
                 'pending_sha256': sha(after), 'before_base64': base64.b64encode(before).decode('ascii'),
                 'before_sha256': sha(before)}
    return candidate, operation


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--binding', type=Path, required=True)
    parser.add_argument('--binding-sha256', required=True)
    parser.add_argument('--prelaunch', type=Path, required=True)
    parser.add_argument('--prelaunch-sha256', required=True)
    parser.add_argument('--context-manifest', type=Path, required=True)
    parser.add_argument('--context-manifest-sha256', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    demand(args.binding == BINDING and args.prelaunch == PRELAUNCH and args.output == OUTPUT,
           'Only exact identity FINAL binding/prelaunch/exclusive Source sinks allowed')
    demand(args.context_manifest == CONTEXT / 'public-artifacts-manifest-sealed-recovery095.json',
           'Only actual identity Root-sealed context manifest allowed')
    demand(not OUTPUT.exists() and not OUTPUT.is_symlink(), 'Preserve every earlier FINAL Source packet')
    for value in (args.binding_sha256, args.prelaunch_sha256, args.context_manifest_sha256):
        demand(re.fullmatch('[0-9a-f]{64}', value) is not None, 'Actual Root supplied SHA required')
    binding, binding_ref = document(BINDING)
    prelaunch, pre_ref = document(PRELAUNCH)
    context_mf, context_mf_ref = document(args.context_manifest)
    demand(binding_ref['sha256'] == args.binding_sha256 and pre_ref['sha256'] == args.prelaunch_sha256
           and context_mf_ref['sha256'] == args.context_manifest_sha256, 'Actual Root supplied inputs differ')
    demand(binding['format_version'] == 3 and binding['status'] == 'SEALED_REAL95_SOURCE_NOT_RUNTIME_PASS'
           and binding['actual_ui_retry'] is binding['actual_ui_identity_retry'] is True
           and binding['root_spec_projection_from_ui_retry'] is True
           and binding['available_checks_passed'] is False, 'Only real SOURCE-only identity binding allowed')
    runner_ref = reference(CONTEXT / 'full095_context_ui_retry.py')
    context_payload = context_mf['payload_files']
    demand(type(context_payload) is list and binding_ref in context_payload and runner_ref in context_payload,
           'Actual Root-final binding/context must both belong to physical sealed Source manifest')
    for row in context_payload:
        reference(row['path'], row)
    demand(prelaunch['runner'] == binding['root_spec']['ui']['runner']
           and binding['recovery_spec']['root_ui_prelaunch'] == pre_ref, 'Actual third producer/prelaunch differs')
    guard = binding['root_spec']['completed_working_tree_chain'][-1]['source_guard']
    guard_value, _ = document(guard['path'], guard)
    demand(guard['path'] == '/workspace/rougezhushou/research/p2-section095-selected-module-source-report/root-source-095-v2.json'
           and guard['bytes'] == 84227
           and guard['sha256'] == '41b9f4662a31b0c8ade2cf51c019bda0a04f6569e92770249bcf2e7ebabe9eab'
           and guard_value['source_sha256_after'] == binding['actual_inputs']['source_sha256']
           and len(guard_value['source_sha256_after']) == 735, 'Actual archived Source guard differs')
    verified = {name: source_packet(packet) for name, packet in PACKETS.items()}
    sources, inverses = {}, {}
    for name, packet in PACKETS.items():
        folder = verified[name][0]
        original = (folder / packet['file']).read_bytes()
        data, ops = original, []
        if name == 'acceptance':
            data, op = replacement(data, '__ACTUAL_UI_IDENTITY_RETRY_BINDING_SHA256_PENDING__', binding_ref['sha256'])
            ops.append(op)
        elif name == 'reviewer':
            data, op = replacement(data, "'__ACTUAL_UI_IDENTITY_RETRY_BINDING_FULL_REF_PENDING__'", repr(binding_ref))
            ops.append(op)
            data, op = replacement(data, '__ACTUAL_UI_IDENTITY_RETRY_CONTEXT_RUNNER_SHA256_PENDING__', runner_ref['sha256'])
            ops.append(op)
        recovered = data
        for op in reversed(ops):
            a, n = op['pending_byte_start'], op['pending_byte_count']
            demand(sha(recovered[a:a+n]) == op['pending_sha256'], 'Exact Root seal inverse differs')
            recovered = recovered[:a] + base64.b64decode(op['before_base64'], validate=True) + recovered[a+n:]
        demand(recovered == original, 'Whole inverse to frozen Source differs')
        compile(data, str(OUTPUT / packet['file']), 'exec')  # Never executed.
        sources[packet['file']] = data
        inverses[name] = {'original': reference(folder / packet['file']), 'operations': ops,
                          'exact_whole_byte_inverse': True, 'target_executions': 0}
    archive_folder = verified['archive'][0]
    config, _ = document(archive_folder / 'source-inputs095.json')
    for key, value in (('recovery_binding', binding_ref), ('recovery_runner', runner_ref), ('ui_prelaunch', pre_ref)):
        old = config['pinned_source_inputs'][key]
        demand(old['path'] == value['path'] and old['bytes'] is old['sha256'] is None,
               'Only declared pending Source reference slots may be sealed')
        config['pinned_source_inputs'][key] = value
    config['status'] = 'ROOT_SEALED_IDENTITY_SOURCE_INPUTS_NOT_RUNTIME_PASS'
    config['actual_identity_final_refs_present'] = True
    config['public_packets'].append({'manifest_path': context_mf_ref['path'], 'manifest_sha256': context_mf_ref['sha256'],
        'payload_count': len(context_payload), 'style': 'payload_ref_rows', 'archive_prefix': 'source-preparation/identity-FINAL-context095',
        'numbered_section_completed': False, 'public': True, 'qualification': 'Actual Root-sealed SOURCE, not runtime or section completion.'})
    for i, info in enumerate(config.pop('source_identity_required_extra_packets')):
        mf, mf_ref = document(info['path'])
        if info['style'] == 'local_artifact_dict':
            for name, row in mf['artifacts'].items():
                reference(Path(info['path']).parent / name, {'path': str(Path(info['path']).parent / name), **row})
            config['public_packets'].append({'manifest_path': mf_ref['path'], 'manifest_sha256': mf_ref['sha256'],
                'payload_count': len(mf['artifacts']), 'style': 'local_artifact_dict', 'archive_prefix': info['archive_prefix'],
                'numbered_section_completed': False, 'public': True, 'qualification': 'Explicit frozen SOURCE, not runtime or numbered completion.'})
        else:
            demand(info['style'] == 'flat_file_meta_dict' and mf['STOPWRITE'] is True and mf['runtime_pass'] is False,
                   'Explicit flat Source packet qualification differs')
            for name, row in mf['files'].items():
                reference(row['path'], row)
                config['supplemental_public_inputs']['identity_Source_packet_%02d_%s' % (i, name.replace('.', '_'))] = row
            config['supplemental_public_inputs']['identity_Source_manifest_%02d' % i] = mf_ref
    for full in list(CHECKED.values()):
        reference(full['path'], full)
    OUTPUT.mkdir()
    for name, data in sources.items():
        write(OUTPUT / name, data)
    write(OUTPUT / 'source-inputs095.json', encoded(config))
    write(OUTPUT / 'archive-spec-template-ui-identity095.json', (archive_folder / 'archive-spec-template-ui-identity095.json').read_bytes())
    findings = {'status': 'ROOT_SEALED_SOURCE_ONLY_NOT_RUNTIME_PASS', 'source_binding': binding_ref,
                'context_runner': runner_ref, 'actual_Root_prelaunch': pre_ref, 'inverses': inverses,
                'target_executions': 0, 'runtime_pass': False, 'completed_sections_increment': 0,
                'actual_UI_primary_exit': None, 'actual_Saved_primary_exit': None,
                'actual_finished_context_PASS': None, 'actual_completed_archive_spec': None,
                'archive_commit_push_executed': False, 'all_checked_physical_inputs': list(CHECKED.values())}
    write(OUTPUT / 'source-findings095.json', encoded(findings))
    write(OUTPUT / 'README095.md', b'Root-sealed SOURCE-only helpers. No UI, Saved, finish, archive, commit or push is certified by this packet.\n')
    payload = [reference(p) for p in sorted(OUTPUT.iterdir()) if p.is_file()]
    mfpath = OUTPUT / 'public-artifacts-manifest-source-preparation095.json'
    write(mfpath, encoded({'format_version': 1, 'section': 95, 'status': 'ROOT_SEALED_IDENTITY_EVIDENCE_HELPERS_SOURCE_ONLY',
                          'STOPWRITE': True, 'runtime_calls': 0, 'runtime_pass': False, 'payload_files': payload}))
    handoff = {'status': 'STOPWRITE_SOURCE_ONLY_REQUIRES_ROOT_INDEPENDENT_SOURCE_REVIEW', 'manifest': reference(mfpath),
               'helpers': {name: reference(OUTPUT / name) for name in sources}, 'runtime_calls': 0,
               'actual_completed_archive_spec': None, 'archive_commit_push_executed': False}
    write(OUTPUT / 'handoff-source-preparation095.json', encoded(handoff))
    print(json.dumps(handoff, ensure_ascii=False))


if __name__ == '__main__':
    main()
