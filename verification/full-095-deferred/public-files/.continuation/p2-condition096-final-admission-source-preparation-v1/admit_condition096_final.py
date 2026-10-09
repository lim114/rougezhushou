"""Future Root metadata gate. Never launches any admitted target."""
import argparse
from pathlib import Path
from condition096_metadata_source import LOCAL, V2, RUNNERS, canonical, ref, doc, bound, require, sha, named_gates, runtime_path, source_inputs, final_source, write_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--spec', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    spec_ref = ref(str(args.spec))
    spec = doc(spec_ref)
    require(spec['format_version'] == 1 and spec['section'] == 96 and spec['status'] == 'ROOT_ACTUAL_CONDITION096_POSTSEAL_ADMISSION_INPUTS', 'Actual external admission inputs required')
    manifest_ref = spec['actual_final_manifest']
    manifest = doc(manifest_ref)
    require(manifest['status'] == 'ROOT_SEALED_FINAL_SOURCE_EXTERNAL_POSTSEAL_ADMISSION_PENDING' and manifest['runtime_executed'] is manifest['runtime_pass'] is False, 'Actual physical FINAL manifest required')
    directory = canonical(manifest_ref['path']).parent
    require(directory.is_relative_to(LOCAL), 'Actual external FINAL directory required')
    require(set(manifest['artifacts']) == {'condition096-binding-final.json', 'exact-final-source-inverse096.json', *[row['final'] for row in RUNNERS.values()]}, 'Exact five sealed artifact roles required')
    require({path.name for path in directory.iterdir()} == {*manifest['artifacts'], 'public-artifacts-manifest-final096.json'} and all(path.is_file() and not path.is_symlink() for path in directory.iterdir()), 'Exact six regular FINAL package files required')
    for name, row in manifest['artifacts'].items():
        require(Path(name).name == name, 'Flat exact Source artifact name required')
        bound({'path': str(directory / name), 'bytes': row['bytes'], 'sha256': row['sha256']})
    binding_ref = ref(str(directory / 'condition096-binding-final.json'))
    actual_input = doc(manifest['root_input_spec'])
    expected_binding, helper_refs = source_inputs(actual_input, Path(__file__).resolve().parent)
    require(doc(binding_ref) == expected_binding and manifest['metadata_helpers'] == helper_refs, 'Actual sealed binding or metadata-helper Source differs')
    for row in RUNNERS.values():
        pending = bound({'path': str(V2 / row['pending']), 'bytes': row['bytes'], 'sha256': row['sha256']})
        expected_source, _ = final_source(pending, binding_ref['sha256'])
        require((directory / row['final']).read_bytes() == expected_source, 'Whole original runner logic or exact binding substitutions differ')
    target = manifest['execution_target']
    runner_ref = ref(str(directory / RUNNERS[target]['final']))
    named_gates(spec['actual_external_postseal_FINAL_source_review'], spec['postseal_review_pointers'], {'source_pass': True, 'runtime_pass': False, 'binding_sha256': binding_ref['sha256'], 'runner_sha256': runner_ref['sha256'], 'manifest_sha256': manifest_ref['sha256'], 'published_HEAD': manifest['actual_published95_HEAD']})
    binding = doc(binding_ref)
    require(binding['root_runtime_authorized'] is True and binding['embedded_admission_scope'] == 'PENDING_TEMPLATE_PRESEAL_SOURCE_ADMISSION_ONLY' and binding['external_actual_postseal_FINAL_review_required_before_launch'] is True, 'One-way preseal/external-postseal contract differs')
    argv = spec['actual_execution_argv']
    if target == 'wine_window':
        wrapper = actual_input['wine_path_mapping']['wrapper']
        bound(wrapper)
        require(argv == [wrapper['path'], runtime_path(runner_ref['path'], 'wine')], 'Exact actual Wine wrapper/Z-mapped FINAL argv required')
    else:
        require(type(argv) is list and len(argv) == (5 if target == 'linux_comparator' else 2) and argv[1] == runner_ref['path'], 'Exact actual Linux FINAL argv required')
        interpreter = spec['actual_Linux_python']
        entry = Path(argv[0])
        require(entry.is_absolute() and entry.is_file() and interpreter['path'] == argv[0] and len(entry.read_bytes()) == interpreter['bytes'] and sha(entry.read_bytes()) == interpreter['sha256'], 'Actual Linux interpreter entry bytes/SHA differ')
        if target == 'linux_comparator':
            for path in argv[2:4]:
                receipt = doc(ref(path))
                require(receipt['passed'] is receipt['workflow_complete'] is True and receipt['source_drift'] == [], 'Actual comparator data not successful')
            require(not canonical(argv[4]).exists(), 'Fresh absent comparison receipt required')
    cwd = str(canonical(spec['actual_execution_cwd']))
    require(Path(cwd).is_dir(), 'Actual existing execution cwd required')
    named_gates(spec['actual_Root_launch_authorization'], spec['Root_launch_authorization_pointers'], {'Root_authorized': True, 'argv': argv, 'cwd': cwd, 'binding_sha256': binding_ref['sha256'], 'runner_sha256': runner_ref['sha256'], 'manifest_sha256': manifest_ref['sha256']})
    output = canonical(str(args.output))
    require(output.is_relative_to(LOCAL) and not output.exists(), 'Fresh external admission receipt required')
    require(ref(str(args.spec)) == spec_ref and ref(manifest_ref['path']) == manifest_ref and ref(runner_ref['path']) == runner_ref and ref(binding_ref['path']) == binding_ref, 'Actual postseal inputs changed during gate')
    receipt = write_json(output, {'format_version': 1, 'section': 96, 'status': 'ACTUAL_FINAL_SOURCE_ADMITTED_ROOT_AUTHORIZED_TARGET_NOT_EXECUTED', 'source_gate_passed': True, 'runtime_pass': False, 'runtime_executed': False, 'actual_final_manifest': manifest_ref, 'actual_final_binding': binding_ref, 'actual_final_runner': runner_ref, 'actual_external_FINAL_source_review': spec['actual_external_postseal_FINAL_source_review'], 'actual_Root_launch_authorization': spec['actual_Root_launch_authorization'], 'actual_execution_argv': argv, 'actual_execution_cwd': cwd, 'actual_primary_exit_code': None, 'actual096_completed': False, 'completed_section_increment': 0, 'target_helper_executions': 0})
    print({'metadata_admission_only': True, 'receipt': receipt, 'runtime_executed': False})


if __name__ == '__main__':
    main()
