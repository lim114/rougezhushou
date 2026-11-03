import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parent
SOURCE=Path('/workspace/.continuation/p2-gummy-back-parser-source087')
INDEPENDENT=Path('/workspace/.continuation/p2-gummy-back-animation-reference-087-independent')
MANIFEST=ROOT/'final-public-artifacts-manifest087.json'
HANDOFF=ROOT/'final-handoff087.json'
if MANIFEST.exists() or HANDOFF.exists():raise RuntimeError('Final seal must not be overwritten')
formal=INDEPENDENT/'formal-review'
formal_manifest=formal/'final-public-artifacts-manifest087.json'
formal_handoff=formal/'final-handoff087.json'
if not formal_manifest.exists() or not formal_handoff.exists():raise RuntimeError('Wait for explicit formal FINAL seal')
files=[];seen=set()
def add(path,archive):
    path=Path(path);raw=path.read_bytes()
    assert archive not in seen,archive
    seen.add(archive)
    files.append({'source_path':str(path),'archive_path':archive,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
for path in sorted(ROOT.iterdir()):
    if not path.is_file() or path in (MANIFEST,HANDOFF):continue
    if path.name in ('matrix-baseline-results.json','matrix-draft-results.json'):continue
    add(path,path.name)
for rel in ('rouge/data/original-animation-references.json','tests/test_original_animation_048.py','tests/test_gummy_back_animation_reference.py'):
    add(ROOT/'draft'/rel,'product/'+rel)
add(ROOT/'baseline/scripts/verify_cloud.py','baseline/scripts/verify_cloud.py')
def include_packet(manifest_path,handoff_path,prefix,archive_base):
    manifest=json.loads(manifest_path.read_text())
    assert manifest.get('format_version',manifest.get('version'))==1
    for item in manifest['files']:
        path=Path(item['source_path']);raw=path.read_bytes()
        assert len(raw)==item['bytes'] and hashlib.sha256(raw).hexdigest()==item['sha256'],path
        add(path,prefix+item['archive_path'])
    manifest_archive=prefix+manifest_path.relative_to(archive_base).as_posix()
    handoff_archive=prefix+handoff_path.relative_to(archive_base).as_posix()
    if manifest_archive not in seen:add(manifest_path,manifest_archive)
    if handoff_archive not in seen:add(handoff_path,handoff_archive)
include_packet(SOURCE/'public-artifacts-manifest087.json',SOURCE/'final-handoff087.json','source-packet087/',SOURCE)
# The formal149 manifest already contains the whole immutable source preparation
# packet and its two seals; include that packet once under its existing paths.
include_packet(formal_manifest,formal_handoff,'independent/',INDEPENDENT)
freeze=json.loads((ROOT/'author-freeze087.json').read_text())
formal_data=json.loads(formal_handoff.read_text())
manifest={'format_version':1,'status':'FINAL_STABLE externally frozen product proposal; root owns apply/commit',
    'files':files,'bytes':sum(x['bytes'] for x in files),'numbered_section_proposal':87,
    'source_packet_original_manifest_sha256':'db2679793321d9d4a0f817757c53d93f88a16c4d4261f65f54223f69fb8b5265',
    'source_packet_original102_files_included':True,
    'compressed_author_saved_matrices':'lossless-compression-map087.json preserves original/compressed/decompressed bytes and SHA256; original frozen files were not changed',
    'excluded_working_trees':'baseline/ and draft/ Git working checkout interiors except the declared three product files and baseline registry; public source Git work pack is excluded in its immutable source manifest',
    'product_stage_source_parses_downloads_root_tracked_edits_Qt_Wine':0}
MANIFEST.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
handoff={'version':1,'status':'FINAL_STABLE author and independent formal product validation passed','sealed_at':datetime.now(timezone.utc).isoformat(),
    'manifest':{'source_path':str(MANIFEST),'archive_path':MANIFEST.name,'bytes':MANIFEST.stat().st_size,'sha256':digest(MANIFEST)},
    'artifact_count':len(files),'artifact_bytes':manifest['bytes'],
    'author_freeze_sha256':digest(ROOT/'author-freeze087.json'),
    'patch':freeze['patch'],'source_files':freeze['source_files'],
    'author_baseline_commit':freeze['author_baseline_commit'],'root_transport_receipt':'root86-transport-receipt.json','root86_commit':'0f27027e7e1f49c08f298706b599e310e299238b',
    'root_current_source_checker':{'source_path':str(ROOT/'root_current_source087.py'),'archive_path':'root_current_source087.py','bytes':(ROOT/'root_current_source087.py').stat().st_size,'sha256':digest(ROOT/'root_current_source087.py'),'author_preflight':'root-checker-author-preflight.json'},
    'registry_proposal':{'source_path':str(ROOT/'registered-verify_cloud087.py'),'archive_path':'registered-verify_cloud087.py','bytes':(ROOT/'registered-verify_cloud087.py').stat().st_size,'sha256':digest(ROOT/'registered-verify_cloud087.py'),'one_entry':'tests.test_gummy_back_animation_reference','inverse_exact_to_root86':True,'applied_by_author':False},
    'validation_scope':'validation-scope-sidecar087.json',
    'author_API_ledger':{'initial_inspection':4,'matrix_fresh':67,'matrix_initial_reuse_not_fresh':3,'new_tests_by_explicit_sites':11,'instrumented_related':56,'total_fresh':138},
    'author_matrix_scope':{'pairs':35,'unchanged_whole_decoded_JSON_type_value_and3texts':16,'exact_old_errors':9,'new_explicit_Back_successes':10,'native_before_JSON_saved':False},
    'author_formatter_scope':{'explicit_matrix3text_requests':126,'instrumented_entries':False,'overall_including_test_and_internal_delegation_total':None},
    'tests':freeze['tests'],'independent_formal':{'source_path':str(formal_handoff),'archive_path':'independent/formal-review/'+formal_handoff.name,'bytes':formal_handoff.stat().st_size,'sha256':digest(formal_handoff)},
    'independent_fresh_expected_verified_ledger':{'pairs':12,'pair_API_calls':24,'new_tests':7,'new_test_API_calls':11,'total_fresh':35,'native_complete_control_pairs':6,'old_exact_errors':2,'new_Back_successes':4,'explicit3text_requests':48,'instrumented_formatter_entries':64,'new_test_formatter_entries':0,'cached_catalog_profiles_references_calls_verified':24,'caller_calls_verified':35},
    'immutable_prior_source_stage':{'source_packet_manifest_sha256':'db2679793321d9d4a0f817757c53d93f88a16c4d4261f65f54223f69fb8b5265','source_packet_handoff_sha256':'c0d718050a376bac2a4fee314e8629aa01e65518f5e467501f5ef21a0aed04af','original_source_parser_calls':2,'source_parser_failures':0,'new_product_stage_source_parser_or_download_calls':0},
    'product_stage_root_tracked_changes':0,'product_stage_Qt_Wine_calls':0,
    'unknowns_preserved':['native normal/skill/skin binding and lifecycle/collision clocks','friendly acquisition/threshold/end','atlas/render/geometry and exact EOF','historical reader identity/error root cause/attempt total'],
    'restart':'Root applies the exact three-file patch to its verified86 baseline, registers the new module once while preserving86, runs root_current_source087.py against the applied tree and its appropriate related/selected checks, then archives and commits. Do not rerun original2 source parses or the passed author138/35decoded matrix.'}
HANDOFF.write_text(json.dumps(handoff,ensure_ascii=False,indent=2)+'\n')
for item in files:
    raw=Path(item['source_path']).read_bytes()
    assert len(raw)==item['bytes'] and hashlib.sha256(raw).hexdigest()==item['sha256'],item['source_path']
print(json.dumps({'files':len(files),'bytes':manifest['bytes'],'manifest_sha256':digest(MANIFEST),'handoff_sha256':digest(HANDOFF)},indent=2))
