"""Static provenance sealing only. Never imports or executes the Spine bundle."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parent
PARENT = ROOT.parent / 'p2-gummy-back-parser-source087'
COMMIT = '8b4844bd4b193ba9e54487ed397a777993cbad56'
RESOURCE_COMMIT = 'd0b5af0b004b044d322397ce5ae79632b6d9fcdd'
BUNDLE_SHA = 'f1e0a31b9906e4d4daf2733857d21381ddbbe75adec7f4d83e1cc9b2b070dfc1'
FACTORY_SHA = '9da74dbfaa1434e99e94a28f9d949c746877b1a4efe76041c702cb98b97dbe58'

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def dump(name, value):
    (ROOT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def describe(path, source_path=None):
    raw = path.read_bytes()
    return {'source_path': source_path or str(path), 'archive_path': str(path.relative_to(ROOT)),
            'bytes': len(raw), 'sha256': sha(raw)}

snapshots = ROOT / 'parent-source-snapshots'
snapshots.mkdir(exist_ok=True)
parent_files = ['read_official_source.js', 'git-acquisition-receipt.json',
                'header-only-receipt.json', 'visible-history-receipt.json',
                'history/gummy-visible-production-record.json']
parent_bindings = []
for relative in parent_files:
    src = PARENT / relative
    dst = snapshots / relative
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    assert src.read_bytes() == dst.read_bytes()
    parent_bindings.append(describe(dst, str(src)))

acquisitions = [json.loads((ROOT / name).read_text()) for name in [
    'official-minimal-acquisition087.json', 'official-dependency-acquisition087.json',
    'official-core-bundle-acquisition087.json', 'official-loader-contract-acquisition087.json']]
requests = []
for acquisition in acquisitions:
    requests.extend(acquisition.get('files', [acquisition['file']] if 'file' in acquisition else []))
assert len(requests) == 13
successful = [item for item in requests if item['success']]
assert len(successful) == 12
timed = []
for item in successful:
    p = ROOT / item['archive_path']
    assert len(p.read_bytes()) == item['bytes'] and sha(p.read_bytes()) == item['sha256']
    timed.append({**item,
        'local_saved_file_mtime_utc': datetime.fromtimestamp(p.stat().st_mtime, timezone.utc).isoformat(),
        'timestamp_scope': 'Actual local saved-file mtime; not server Date or exact HTTP request time',
        'exact_HTTP_request_time': None, 'server_Date': None})
dump('official-local-save-times087.json', {'version': 1, 'network_requests_added': 0,
    'official_commit': COMMIT, 'files': timed,
    'failed_requests_have_no_saved_source_file_mtime': [item for item in requests if not item['success']]})

reader_path = ROOT / 'official-source/spine-ts/core/src/SkeletonBinary.ts'
reader = reader_path.read_text()
bundle_path = ROOT / 'official-source/spine-ts/build/spine-core.js'
bundle = bundle_path.read_text()
factory_path = ROOT / 'research_attachment_factory087.js'
factory = factory_path.read_text()
runner_path = snapshots / 'read_official_source.js'
runner = runner_path.read_text()
assert sha(bundle_path.read_bytes()) == BUNDLE_SHA
assert sha(factory_path.read_bytes()) == FACTORY_SHA
assert "const createLoader = require(factoryPath).createLoader;" in runner
assert "exports.createLoader = createLoader;" in factory
constructors = ['RegionAttachment', 'MeshAttachment', 'BoundingBoxAttachment',
                'PathAttachment', 'PointAttachment', 'ClippingAttachment']
for name in constructors:
    assert factory.count('new spine.' + name + '(name)') == 1
assert factory.count('new spine.TextureRegion()') == 2
assert 'return null' not in factory and 'BoneData' not in factory and 'SlotData' not in factory
animation = reader.split('private readAnimation', 1)[1].split('private readCurve', 1)[0]
assert 'attachment.bones' in animation and 'attachment.vertices' in animation
assert not any(field in animation for field in ['.region', '.uvs', '.offset'])
assert 'let event = new Event(time, eventData);' in animation
assert 'return new Animation(name, timelines, duration);' in animation
assert 'Headless' not in bundle

header = json.loads((snapshots / 'header-only-receipt.json').read_text())
history = json.loads((snapshots / 'visible-history-receipt.json').read_text())
acquisition = json.loads((snapshots / 'git-acquisition-receipt.json').read_text())
assert acquisition['commit'] == RESOURCE_COMMIT
assert header['official_commit'] == COMMIT
assert {item['spine_version_string'] for item in header['resources']} == {'3.8.99'}
assert history['visible_historical_parse_failure_lower_bound'] == 1
assert history['historical_attempt_total'] is None
assert history['historical_reader_identity'] is None
assert len(acquisition['resources']) == 2
for item in acquisition['resources']:
    matching = next(row for row in header['resources'] if row['orientation'] == item['orientation'])
    assert item['sha256'] == matching['resource_sha256'] and item['bytes'] == matching['resource_bytes']
    # Read metadata, not resource binary, and do not execute the reader.
    assert item['git_blob_sha1'] in ['cc171af6926392621c192c1dc5ba4f036d1b9b00',
                                   '473df5c69d7e3552f6937f749bd42dd9e974ca01']

def source_quote(path, exact):
    content = (ROOT / path).read_text()
    assert exact in content
    return {'source_path': path, 'line': content[:content.index(exact)].count('\n') + 1, 'quote': exact}

contracts = [
    source_quote('official-source/spine-ts/README.md', 'spine-ts works with data exported from Spine 3.8.xx.'),
    source_quote('official-source/spine-ts/README.md', 'To use only the core library without rendering support, include the `build/spine-core.js` file in your project.'),
    source_quote('official-source/spine-ts/README.md', 'All `*.js` files are self-contained and include both the core and respective backend classes.'),
    source_quote('official-source/spine-ts/core/src/SlotData.ts', 'if (boneData == null) throw new Error("boneData cannot be null.");'),
    source_quote('official-source/spine-ts/core/src/SkeletonBinary.ts', 'let boneData = skeletonData.bones[input.readInt(true)];'),
    source_quote('official-source/spine-ts/core/src/SkeletonBinary.ts', 'private buffer = new DataView(data.buffer)'),
    source_quote('official-source/spine-ts/core/src/SkeletonBinary.ts', 'let event = new Event(time, eventData);'),
    source_quote('official-source/spine-ts/core/src/SkeletonBinary.ts', 'return new Animation(name, timelines, duration);'),
    source_quote('official-source/spine-ts/core/src/Texture.ts', 'originalWidth = 0; originalHeight = 0;')
]
receipt = {
    'version': 1, 'status': 'SOURCE_ONLY_PASS_READER_NOT_EXECUTED_BY_REVIEWER',
    'reviewed_at_utc': datetime.now(timezone.utc).isoformat(),
    'scope': 'Official fixed 3.8 source, custom research attachment interface, parent runner static audit only',
    'official_repository': 'https://github.com/EsotericSoftware/spine-runtimes',
    'official_reference': 'refs/heads/3.8', 'official_commit': COMMIT,
    'resource_commit': RESOURCE_COMMIT, 'official_source_files': timed,
    'official_bundle': describe(bundle_path), 'research_attachment_factory': describe(factory_path),
    'factory_export': 'exports.createLoader = createLoader',
    'official_attachment_constructors': constructors,
    'factory_payload_scope': 'All six official attachment object classes returned; official reader reads and assigns genuine attachment payload. LinkedMesh uses official MeshAttachment and official linked-parent handling.',
    'official_TextureRegion_only': {'region_and_mesh_instances': 2, 'altered_default_fields': [],
        'default_fields': 'u/v/u2/v2/width/height/offsetX/offsetY/originalWidth/originalHeight=0; rotate=false',
        'purpose': 'Permit official attachment calls without falsely inventing atlas dimensions/image',
        'derived_region_offset_may_be_nonfinite': True,
        'render_UVs_offsets_geometry_verified': False},
    'event_duration_source_contract': 'readAnimation consumes real timeline frames; deform uses real attachment bones/vertices; no .region/.uvs/.offset field dependency in that method; event payload uses official EventTimeline.',
    'Headless_named_symbol_in_fixed_core_bundle': False,
    'official_reader_modified': False, 'fake_bones_or_slots': False, 'null_attachment_skip': False,
    'compiled_bundle_needed': False, 'third_party_bundle_or_dependencies': False,
    'parent_source_bindings': parent_bindings,
    'parent_runner_static': {
        'status': 'PASS', 'source': describe(runner_path, str(PARENT / 'read_official_source.js')),
        'interface': 'require(factoryPath).createLoader; precise mismatch found before any attempted execution',
        'interface_prevention_actual_failures': 0,
        'bundle_gate': 'Hardcoded approved exact bundle SHA',
        'factory_gate': 'CLI expected SHA checked against actual source bytes, then selected export type checked',
        'resource_gate': 'Frozen acquisition receipt selected by orientation, length/SHA256/actual Git blob SHA1 recomputed from actual file',
        'resource_receipt_identity': describe(snapshots / 'git-acquisition-receipt.json', str(PARENT / 'git-acquisition-receipt.json')),
        'source_copy': 'Uint8Array.from(raw), zero byteOffset/full backing length explicitly asserted',
        'resource_invariance': 'Both exact in-memory copied bytes and on-disk bytes SHA checked after reader return or error',
        'extracted_fields': 'Skeleton source metadata, actual bone parent/index and slot bone index, animation duration, EventTimeline real event values',
        'no_EOF_position_exposed': True,
        'no_native_clock_skin_skill_binding_claim': True},
    'header_evidence': {'scope': 'Read saved parent header receipt only; no independent parsing',
        'both_resource_versions': '3.8.99', 'resources': header['resources']},
    'history': {'visible_parse_failure_lower_bound': 1, 'historical_total_attempts': None,
        'historical_reader_identity': None, 'old_cache_recreated': False,
        'scope': 'Saved evidence lower bound; never inferred absent migrated logs as zero attempts'},
    'source_version_family_match': True, 'Back_payload_reader_return_known_by_this_source_receipt': False,
    'license': {'type': 'Spine Runtimes License Agreement; not MIT',
        'root_LICENSE_date': '2019-05-01', 'reader_source_header_date': '2020-01-01',
        'full_original_notices_retained': True, 'product_integration_performed': False,
        'user_license_qualification_inferred': False},
    'source_contract_quotes': contracts,
    'preparation_accounting': {'official_fixed_raw_GET_attempts': 13, 'successful_official_sources': 12,
        'wrong_AttachmentLoader_root_path_HTTP404': 1, 'API_metadata_host_HTTP403': 1,
        'git_ls_remote_invocations': 1, 'acquisition_script_patch_hunk_format_failure': 1,
        'all_preparations_distinct_from_Back_parse_failures': True,
        'standard_TLS_and_inherited_proxy': True, 'TLS_or_proxy_bypass': False,
        'wire_level_HTTP_request_count_claimed': False},
    'reviewer_execution_counts': {'bundle_execution': 0, 'compile': 0, 'full_skeleton_parse': 0,
        'application_API': 0, 'production_helper': 0, 'formatter': 0, 'tests': 0,
        'Qt': 0, 'Wine': 0, 'tracked_mutations': 0},
    'next_operation_owner': 'Parent only: Front once and exact old nine-duration/event control, Back once only if Front control passes; maintain bounded common attempt accounting.',
    'unknowns': ['Back full payload parse outcome at this source-only stage',
        'Historical total parse attempts and historical reader identity', 'EOF/full byte consumption',
        'Atlas/texture/derived visual geometry or rendering correctness',
        'Native game timing, lifecycle, normal/skill/skin bindings or probability']
}
dump('source-contract-receipt087.json', receipt)
print(json.dumps({'status': receipt['status'], 'source_receipt': describe(ROOT / 'source-contract-receipt087.json'),
                  'factory': describe(factory_path), 'runner_snapshot': describe(runner_path),
                  'reviewer_full_parses': 0}, ensure_ascii=False))
