"""Build exact initial-configuration/group references from current public sources."""
from pathlib import Path
from hashlib import sha256
import argparse
import importlib.util
import json
import sys

BASE = Path(__file__).resolve().parents[1]
SOURCE_ROOT = BASE if (BASE / 'rouge/expansion_reference.py').is_file() else BASE.parents[1]


def enc(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf8')


def build(source_root, output_root):
    sys.path.insert(0, str(source_root))
    spec = importlib.util.spec_from_file_location('rouge.current_initial_recruit', BASE / 'rouge/current_initial_recruit.py')
    model = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(model)
    inputs = {}
    for name in (model.TOPIC, model.TOPIC_HTML, model.TOPIC_DOWNLOAD, model.GENERAL_HTML, model.GENERAL_DOWNLOAD):
        path = output_root / name if name in (model.GENERAL_HTML, model.GENERAL_DOWNLOAD) else source_root / name
        inputs[name] = path.read_bytes()
    for html, download in ((model.TOPIC_HTML, model.TOPIC_DOWNLOAD), (model.GENERAL_HTML, model.GENERAL_DOWNLOAD)):
        meta = json.loads(inputs[download])
        if meta['http_status'] != 200 or meta['bytes'] != len(inputs[html]) or meta['sha256'] != sha256(inputs[html]).hexdigest():
            raise ValueError('Actual original document and source receipt required')
    documents = model.document_fragments(inputs[model.TOPIC_HTML].decode('utf8'), inputs[model.GENERAL_HTML].decode('utf8'))
    current = json.loads(inputs[model.TOPIC])
    baseline = json.loads((source_root / 'research/p3-expansion-313/baseline-topic.json').read_bytes())
    data = model.derive_data(current, baseline, documents)
    notes = {'section_candidate': 364, 'new_download_performed': False,
             'generic_original_copy_origin': '.cache/section360-prepared/research/p3-current-upgrade-tickets-360/general-w-page.html',
             'generic_original_receipt_retained_without_rewriting': True,
             'duplicate_audit': {'current_startup350': 'action support, not recruitment combinations',
                                 'ordinary_initial_page313_352': 'already displayed initial resources, not the forward/reverse recruitment associations',
                                 'old_raw_group_definitions_unchanged': data['raw_group_definitions_equal_previous_baseline'],
                                 'initial_recruit_python_consumer_found': False},
             'new_player_capability': 'exact initial-to-group and group-to-initial navigation, current guarantee and unlock-description scope',
             'counts': {'group_records': 14, 'initial_records': 21, 'explicit_links': 106, 'linked_group_records': 10, 'unlinked_group_records': 4},
             'source_keys': ['details.recruitGrps', 'details.init[*].initialRecruitGroup', 'details.monthSquad'],
             'five_star_basis': 'Current theme native description plus specific-theme442954 original paragraph; no generic four-star substitution',
             'first_ticket_full_profession_pool_known': False, 'probabilities_known': False,
             'account_unlock_verified': False, 'actual_initial_recruits_verified': False,
             'limits': ['Four unreferenced support groups are not guessed future months',
                        'All21 initial configurations retain mode/grade/predefinedId/predefinedStyle identity',
                        'No random candidates, current account unlock, technology or actual server menu inferred',
                        'No current initial resources calculated beyond the existing source fields'],
             'license': 'PRTS community CC BY-NC-SA4.0, original game material remains original rights'}
    output = {model.DATA: enc(data), model.EXCERPTS: enc(documents), model.NOTES: enc(notes)}
    files = {}
    for name, body in {**inputs, **output}.items():
        files[name] = {'bytes': len(body), 'sha256': sha256(body).hexdigest()}
    output[model.MANIFEST] = enc({'schema': 'current_initial_recruit_364_manifest_v1', 'files': dict(sorted(files.items()))})
    return model, output


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-root', type=Path, default=SOURCE_ROOT)
    parser.add_argument('--output-root', type=Path, default=BASE)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    model, outputs = build(args.source_root.resolve(), args.output_root.resolve())
    for name, body in outputs.items():
        path = args.output_root / name
        if args.check:
            if path.read_bytes() != body:
                raise ValueError('Build differs: ' + name)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(body)
    print(json.dumps({'groups': 14, 'initial_configs': 21, 'explicit_links': 106, 'unlinked_groups': 4,
                      'manifest_sha256': sha256(outputs[model.MANIFEST]).hexdigest()}))
