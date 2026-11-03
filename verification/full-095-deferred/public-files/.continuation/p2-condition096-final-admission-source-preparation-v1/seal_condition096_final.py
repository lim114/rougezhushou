"""Future Root metadata sealer: creates fresh sibling binding and exact Sources."""
import argparse
import json
from pathlib import Path
from condition096_metadata_source import LOCAL, V2, RUNNERS, canonical, ref, bound, doc, require, sha, source_inputs, final_source, write_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--spec', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    spec_ref = ref(str(args.spec))
    spec = doc(spec_ref)
    output = canonical(str(args.output_dir))
    require(output.is_relative_to(LOCAL) and not output.exists(), 'Fresh external FINAL package required')
    binding, helper_refs = source_inputs(spec, here)
    source_root = canonical(spec['source_root'])
    runtime_output = canonical(spec['fresh_output_directory'])
    require(output != runtime_output and not output.is_relative_to(runtime_output) and not runtime_output.is_relative_to(output) and not output.is_relative_to(source_root), 'FINAL package must be separate from runtime output/source roots')
    pending_sources = {}
    for name, row in RUNNERS.items():
        raw = bound({'path': str(V2 / row['pending']), 'bytes': row['bytes'], 'sha256': row['sha256']})
        pending_sources[name] = raw
    binding_raw = (json.dumps(binding, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode('utf-8')
    binding_sha = sha(binding_raw)
    finals = {name: final_source(raw, binding_sha) for name, raw in pending_sources.items()}
    require(ref(str(args.spec)) == spec_ref, 'Root actual spec changed before metadata seal')
    output.mkdir(exist_ok=False)
    with (output / 'condition096-binding-final.json').open('xb') as stream:
        stream.write(binding_raw)
    binding_ref = ref(str(output / 'condition096-binding-final.json'))
    rows = [binding_ref]
    inverse = {}
    for name, (raw, changes) in finals.items():
        path = output / RUNNERS[name]['final']
        with path.open('xb') as stream:
            stream.write(raw)
        candidate_ref = ref(str(path))
        rows.append(candidate_ref)
        inverse[name] = {'original': ref(str(V2 / RUNNERS[name]['pending'])), 'candidate': candidate_ref, 'changes': changes, 'whole_original_bytes_restored': True}
    inverse_ref = write_json(output / 'exact-final-source-inverse096.json', {'format_version': 1, 'section': 96, 'binding_sha256': binding_sha, 'runners': inverse, 'runtime_executed': False})
    rows.append(inverse_ref)
    manifest = write_json(output / 'public-artifacts-manifest-final096.json', {'format_version': 1, 'section': 96, 'status': 'ROOT_SEALED_FINAL_SOURCE_EXTERNAL_POSTSEAL_ADMISSION_PENDING', 'artifacts': {Path(row['path']).name: {'bytes': row['bytes'], 'sha256': row['sha256']} for row in rows}, 'root_input_spec': spec_ref, 'mode': spec['mode'], 'platform': spec['platform'], 'execution_target': spec['execution_target'], 'actual_published95_HEAD': spec['actual_published95_HEAD'], 'metadata_helpers': helper_refs, 'runtime_pass': False, 'runtime_executed': False, 'actual096_completed': False, 'completed_section_increment': 0})
    print(json.dumps({'metadata_source_seal_only': True, 'manifest': manifest, 'binding': binding_ref, 'runtime_executed': False, 'external_actual_FINAL_review_and_Root_launch_authorization_pending': True}))


if __name__ == '__main__':
    main()
