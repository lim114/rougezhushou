"""Seal completed 0.59 receipts; never infer missing verification.

Required custom receipts:
  --feature-freeze: passed=True, source_sha256={project path: SHA256}.
    Preservation of all 20 original page-feature binaries is independently
    checked against batch-059-before, so an old manifest is never re-verified.
  --hybrid-freeze: passed=True, real_cases=23, strict_differences=0,
    public_source_sha256, owned_files_and_receipts_sha256.
  --popup-freeze: passed=True, current source_sha256 and the independent
    owned_files_and_receipts_sha256 closure of three popup recovery cases.

The current HYBRID_0.59_VERIFICATION.json must reference immutable_summary,
actual_animation_pixel_evidence and baseline_package_seal as {path, sha256}.
All other receipt schemas match the corresponding maintained 0.59 runners.
No OCR, capture, private settings or chat interfaces are imported or invoked.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import math
import statistics
import time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BEFORE=Path('.cache/batch-059-before')
ENGINE=Path('.cache/research/page-ocr-058/freeze-1791173910294123300.json')
PROFILE=Path('.cache/research/run-performance-059/profile-1791177145281855600/receipt.json')
THREADS=Path('.cache/research/run-performance-059/threads-1791179141499034400')
THREAD_RECEIPT=THREADS/'segment-1791179187294576000.json'
FIELDS=('page','run','operator','map','stage','nodes','node_content','viewport')
POPUP=Path('POPUP_RECOVERY_0.59_VERIFICATION.json')
POPUP_VERIFIER=Path('scripts/verify_popup_recovery_059_epoch4.py')
RECOVERED='myrtle_owned:half_client'
MYRTLE='char_151_myrtle'
PERSONAL_IDS=['rogue_6_from_relic_1','rogue_6_from_relic_13']
HELD_POLICY='Current confirmed icon IDs only; legacy99 stays ambiguous; no complete held inventory claim.'
HISTORICAL_OPAQUE={
    '.cache/research/hybrid-059/epoch3-current/current-description-probes-1791186365146221000/receipt.json':
    'f3ec48a3f4260a37cccbd2b9238d7c852444979843542f17c132ba931ce8c399'}
HISTORICAL_ALIASES={
    ('scripts/verify_final_059.py','008616c83b263cfdd0374d5a482137ff057962464e3794636626c08da6b3e616'):
    '.cache/final-059/external-metadata-mirror-correction-1791193828848879800/verify_final_059.py',
    ('scripts/verify_final_059.py','135c29122a76b3cfa5e27f92068c579e7fa66c4c85419d09bb3a1f47eaf0f0fd'):
    '.cache/final-059/profile-coordinate-correction-1791193272237697600/verify_final_059.py',
    ('.cache/batch-059-source-freeze.json','8bad54b5d40298edf0246c4a1733aa79e2fe841e7f07d3aa3917766e538e2bc9'):
    '.cache/research/hybrid-059/epoch-current/archive-before-asset-revision-1791182331359659000/batch-059-source-freeze.json',
    ('.cache/batch-059-source-freeze.json','e073f667f7c8c25e732ea4b776cc22b2e1548a1c98b9d6d11e1551284161b55a'):
    '.cache/research/hybrid-059/epoch2-current/superseded-source-archive-1791184894271631000/batch-059-source-freeze-epoch2.json',
    ('.cache/batch-059-source-freeze.json','ad29df4bb1918994d8b0752a2fbcb73cfaaac26cdfaf0340580cc19002fd38b1'):
    '.cache/research/hybrid-059/epoch3-current/epoch3-interrupted-archive-1791187575532156600/batch-059-source-freeze.json',
    ('HYBRID_0.59_VERIFICATION.json','c157cd28612876c00fcb41cbab8c1c6e329e8ed555267af656addb4126d92a7c'):
    '.cache/research/hybrid-059/epoch-current/archive-before-asset-revision-1791182331359659000/HYBRID_0.59_VERIFICATION.json'}
EXTERNAL_CAMERA_SOURCE='.cache/research/hybrid-059/epoch4-current/baseline-source/rouge/data/battle-map-projections.json'
ARCHIVED_DATA=Path(EXTERNAL_CAMERA_SOURCE).parent.as_posix()
DATA_REFERENCE_SCHEMAS={
    'battle-previews.json':('battle-maps',),'elite-icon-receipt.json':('ui-icons',),
    'emergency-icon-receipt.json':('ui-icons',),'profession-icons.json':('profession-icons',),
    'relic-icon-receipt.json':('relic-icons',),'run-badge-receipt.json':('run-badges',),
    'skill-icons.json':('skill-icons',),'tactical-icon-receipt.json':('relic-icons',),
    'ui-icon-receipt.json':('ui-icons',),'view-catalog.json':('portraits',)}
ALLOWED_EXISTING_PRODUCTION=('rouge/app.py','rouge/recognition.py','rouge/data/page-features/manifest.json',
    'rouge/recipient_recognition.py','rouge/run_recognition.py')


def public_path(path):
    resolved=(ROOT/path).resolve()
    assert resolved.is_relative_to(ROOT),('Outside project',str(path))
    assert '.local' not in resolved.relative_to(ROOT).parts,('Private state',str(path))
    return resolved


def relative(path):return public_path(path).relative_to(ROOT).as_posix()
def sha(path):return hashlib.sha256(public_path(path).read_bytes()).hexdigest()
def read(path):return json.loads(public_path(path).read_text(encoding='utf-8-sig'))
def canonical(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'))


def verify(mapping,evidence=None):
    for name,digest in mapping.items():
        assert sha(name)==digest,('Source/evidence drift',name)
        if evidence is not None:evidence[relative(name)]=digest


def referenced(record,keys,evidence):
    for key in keys:
        item=record[key]
        verify({item['path']:item['sha256']},evidence)


def strict(value):
    if isinstance(value,dict):return {k:strict(v) for k,v in value.items() if k!='elapsed_ms'}
    if isinstance(value,list):return [strict(v) for v in value]
    return value


def differences(a,b,path=''):
    """Match the frozen hybrid verifier's typed, complete JSON leaf diff."""
    if type(a) is not type(b):return [{'path':path,'before':a,'after':b,'reason':'type_or_value'}]
    if isinstance(a,dict):
        result=[]
        for key in sorted(set(a)|set(b)):
            if key not in a or key not in b:
                result.append({'path':path+'/'+key,'before':a.get(key),'after':b.get(key),
                    'reason':'missing_before' if key not in a else 'missing_after'})
            else:result.extend(differences(a[key],b[key],path+'/'+key))
        return result
    if isinstance(a,list):
        result=[]
        if len(a)!=len(b):result.append({'path':path+'/length','before':len(a),'after':len(b),'reason':'length'})
        for index,(old,new) in enumerate(zip(a,b)):result.extend(differences(old,new,path+'/'+str(index)))
        return result
    return [] if a==b else [{'path':path,'before':a,'after':b,'reason':'value'}]


def popup_recovery_evidence(production_sources,evidence,popup_freeze=None):
    """Verify sealed current observations with stdlib only; never rerun OCR.

    Qt uses the same mandatory public fixture closure. FINAL additionally
    requires an independent freeze covering that closure. Historical failed
    observations remain evidence, not sources of values for the current page.
    """
    closed={};walked=set();resolved_aliases={};external_source_metadata={};external_source_mirrors={};resolved_data_references={}

    def close(name,digest):
        name=relative(name);logical_name=name
        assert type(digest) is str and len(digest)==64 and all(c in '0123456789abcdef' for c in digest)
        alias=HISTORICAL_ALIASES.get((name,digest))
        if alias is not None:
            name=relative(alias)
            resolved_aliases[(logical_name,digest)]={'logical_path':logical_name,'sha256':digest,'archive_path':name}
        assert name not in closed or closed[name]==digest,('Conflicting recovery SHA',name)
        assert name not in evidence or evidence[name]==digest,('Conflicting receipt SHA',name)
        verify({name:digest},evidence);closed[name]=digest
        if name not in walked and Path(name).suffix=='.json':
            walked.add(name)
            if name in HISTORICAL_OPAQUE:
                # Preserve the exact bytes of one independently recorded
                # NumPy-intc serialization failure. No current, recovered
                # or arbitrary historical JSON may bypass parsing.
                assert digest==HISTORICAL_OPAQUE[name],('Changed historical opaque artifact',name)
            else:walk(read(name),name)
        return name

    def reference(item):
        assert isinstance(item,dict) and 'path' in item and 'sha256' in item,('Missing evidence reference',item)
        return close(item['path'],item['sha256'])

    def walk(value,artifact,pointer=''):
        if isinstance(value,dict):
            if 'path' in value and 'sha256' in value:reference(value)
            elif 'file' in value and 'sha256' in value:
                # An archived UI audit includes exact mirrors of the three
                # already pinned remote camera sources. They are provenance
                # records, not ROOT-relative current frame inputs.
                mirror_index=pointer.rsplit('/external_source_metadata/',1)
                mirror=(len(mirror_index)==2 and mirror_index[1].isdigit()
                    and set(value)=={'artifact','pointer','url','file','sha256'})
                if mirror:
                    source_artifact=value['artifact'];source_pointer=value['pointer']
                    assert source_artifact==EXTERNAL_CAMERA_SOURCE
                    assert source_artifact in closed and closed[source_artifact]==sha(source_artifact)
                    prefix='/source/camera_reference/'
                    assert source_pointer.startswith(prefix) and source_pointer.removeprefix(prefix).isdigit()
                    index=int(source_pointer.removeprefix(prefix))
                    original=read(source_artifact)['source']['camera_reference'][index]
                    assert set(original)=={'file','url','bytes','sha256','blob'}
                    assert all(value[key]==original[key] for key in ('file','url','sha256'))
                    external_source_mirrors[(artifact,pointer)]={'report_artifact':artifact,'report_pointer':pointer,
                        'source_artifact':source_artifact,'source_pointer':source_pointer,'sha256':value['sha256']}
                    return
                external=(artifact==EXTERNAL_CAMERA_SOURCE and pointer.startswith('/source/camera_reference/')
                    and pointer.removeprefix('/source/camera_reference/').isdigit())
                if external:
                    filename=value['file'];url=value['url'];digest=value['sha256']
                    assert type(filename) is str and '/' not in filename and '\\' not in filename
                    assert type(url) is str and url.startswith(('https://','http://'))
                    assert type(digest) is str and len(digest)==64 and all(c in '0123456789abcdef' for c in digest)
                    external_source_metadata[(artifact,pointer)]={'artifact':artifact,'pointer':pointer,
                        'url':url,'file':filename,'sha256':digest}
                else:
                    filename=relative(value['file'])
                    data_schema=DATA_REFERENCE_SCHEMAS.get(Path(artifact).name,()) if Path(artifact).parent.as_posix()==ARCHIVED_DATA else ()
                    if any(filename.startswith(folder+'/') for folder in data_schema):
                        local_name=close('rouge/data/'+filename,value['sha256'])
                        resolved_data_references[(artifact,pointer)]={'artifact':artifact,'pointer':pointer,
                            'file':filename,'local_path':local_name,'sha256':value['sha256']}
                    else:close(value['file'],value['sha256'])
            for key,item in value.items():
                # Source maps in old failures refer to old code. Their bytes
                # are preserved in explicit archives; never compare those
                # maps blindly with current production paths.
                if key in ('replay_receipts','owned_files_and_receipts_sha256','immutable_receipt_sha256'):
                    assert isinstance(item,dict)
                    for name,digest in item.items():close(name,digest)
                walk(item,artifact,pointer+'/'+key)
        elif isinstance(value,list):
            for index,item in enumerate(value):walk(item,artifact,pointer+'/'+str(index))

    def readonly(record):
        assert record['private_state_read'] is False and record['game_actions']==0 and record['chat_requests']==0

    def scope(record):
        assert record['personal_buff_complete_required'] is True
        assert record['held_inventory_complete_claimed'] is False
        assert record['held_inventory_policy']==HELD_POLICY
        assert record['all_fact_confidence_geometry_leaves_compared'] is True
        assert record['excluded_keys']==['elapsed_ms'];readonly(record)

    top=read(POPUP);close(POPUP,sha(POPUP));scope(top)
    assert top['passed'] is True and type(top['strict_equal_cases']) is int and top['strict_equal_cases']==2
    assert type(top['restored_cases']) is int and top['restored_cases']==1
    expected={'kaltsit_owned:half_client',RECOVERED,'myrtle_owned:padded_35_45'}
    assert set(top['expected_cases'])==expected and len(top['expected_cases'])==3
    assert not top['missing_cases'] and not top['failed_cases'] and top['formal_case_count_unchanged']==23
    assert len(production_sources)==136 and top['source_sha256']==production_sources
    verify(production_sources)
    close(POPUP_VERIFIER,top['verifier_sha256'])
    close('scripts/verify_hybrid_059.py',top['hybrid_verifier_sha256'])
    for key in ('inventory','oracle','same_frame_probe','baseline_package_seal','preserved_failure',
                'preserved_epoch2_archive','preserved_epoch3_full_failure','existing_description_probe','immutable_summary'):
        reference(top[key])
    current_freeze=top['production_freeze']
    assert current_freeze['path']=='.cache/batch-059-source-freeze.json'
    assert current_freeze['sha256']==sha(current_freeze['path']),'Current production freeze may not resolve to a historical alias'
    current_freeze_record=read(current_freeze['path'])
    assert current_freeze_record['source_hashes']==production_sources and current_freeze_record['version']=='0.59.0'
    immutable=read(top['immutable_summary']['path'])
    assert immutable['passed'] is True and immutable['source_sha256']==production_sources
    assert immutable['verifier_sha256']==top['verifier_sha256']
    assert immutable['replay_receipts']==top['replay_receipts']
    inventory=read(top['inventory']['path']);readonly(inventory)
    assert inventory['source_sha256']==production_sources and inventory['verifier_sha256']==top['verifier_sha256']
    assert inventory['hybrid_verifier_sha256']==top['hybrid_verifier_sha256']
    close('scripts/verify_popup_boundaries_059.py',inventory['boundary_verifier_sha256'])
    assert inventory['personal_buff_complete_required'] is True and inventory['held_inventory_complete_claimed'] is False
    assert inventory['formal_case_count_unchanged']==23 and inventory['additional_derived_cases']==3
    assert inventory['strict_preservation_cases']==2 and inventory['explicit_recovery_cases']==1
    assert len(inventory['cases'])==3 and {c['id'] for c in inventory['cases']}==expected
    for key in ('oracle','baseline_package_seal','preserved_failure','preserved_epoch2_archive',
                'preserved_epoch3_full_failure','existing_description_probe'):
        assert inventory[key]==top[key]
    reference(inventory['derived_inventory'])
    baseline=read(top['baseline_package_seal']['path'])
    assert baseline['before_manifest_sha256']==sha(BEFORE/'manifest.json')
    close(BEFORE/'manifest.json',baseline['before_manifest_sha256'])
    epoch=Path(relative(top['inventory']['path'])).parent.parent
    for key in ('frozen_original_sources','supplemented_current_public_media'):
        for name,digest in baseline[key].items():close((epoch/'baseline-source'/name).as_posix(),digest)
    failure=read(top['preserved_failure']['path']);assert failure['passed'] is False and RECOVERED in failure['failed_cases']
    old_full=read(top['preserved_epoch3_full_failure']['path'])
    assert old_full['passed'] is False and RECOVERED in old_full['failed_cases']
    assert old_full['failed_checks'][RECOVERED] and any(c['passed'] is False for c in old_full['failed_checks'][RECOVERED])
    description=read(top['existing_description_probe']['path'])
    assert description['existing_strategy_only'] is True and description['canonical_equal'] is False
    assert description['rejection_is_correct_current_evidence'] is True
    assert description['total_actual_rec_calls_for_three_existing_line_inputs']==3
    assert len(description['lines'])==3;readonly(description)
    rows={};restored=None
    assert len(top['replay_receipts'])==3
    for name,digest in top['replay_receipts'].items():
        row=read(close(name,digest));scope(row)
        assert row['passed'] is True and row['source_sha256']==production_sources
        assert row['verifier_sha256']==top['verifier_sha256'] and row['hybrid_verifier_sha256']==top['hybrid_verifier_sha256']
        assert row['case'] not in rows;rows[row['case']]=row
        case=read(reference(row['case_receipt']));assert case['id']==row['case']
        planned=next(c for c in inventory['cases'] if c['id']==row['case'])
        assert canonical(case)==canonical(planned) and len(case['frames'])==1
        assert set(row['worker_receipts'])==set(row['outputs'])=={'baseline','current'}
        for label,item in row['worker_receipts'].items():
            worker=read(reference(item))
            assert worker['case']==row['case'] and worker['actual_rapidocr_engine'] is True
            assert canonical(worker)==canonical(row['outputs'][label]),('Worker/output mismatch',row['case'],label)
            assert len(worker['frames'])==1 and set(worker['frames'][0]['observation'])==set(FIELDS)
        old=row['outputs']['baseline']['frames'][0]['observation']
        current_frame=row['outputs']['current']['frames'][0];new=current_frame['observation']
        delta=differences(strict(old),strict(new),'/frames/0')
        assert canonical(delta)==canonical(row['strict_semantic_differences']),('Unrecorded leaf difference',row['case'])
        route=current_frame['performance']['routing']
        assert row['route_verified'] is True and new['page']=='run_roster'
        assert route['strategy']=='visual_region_ocr' and route['candidates']==['run_owned_popup'] and route['semantic_verified'] is True
        if row['case']==RECOVERED:
            assert row['validation_kind']=='current_evidence_restoration'
            assert sorted(d['path'] for d in delta)==['/frames/0/page','/frames/0/run']
            assert old['page']=='unknown' and old['run'] is None
            for key in FIELDS:
                if key not in ('page','run'):assert not differences(old[key],new[key],'/'+key)
            assert row['oracle_checks'] and all(c['passed'] is True for c in row['oracle_checks'])
            for check in row['oracle_checks']:
                if 'actual' in check or 'expected' in check:
                    assert 'actual' in check and 'expected' in check and not differences(check['actual'],check['expected'],check['path'])
            assert row['same_frame_probe']==top['same_frame_probe']
            reference(row['same_frame_full_run_reconstruction'])
            restored=(relative(name),row,case,current_frame)
        else:
            assert row['validation_kind']=='strict_preservation' and delta==[]
            assert row['same_frame_probe'] is None and row['same_frame_full_run_reconstruction'] is None
    assert set(rows)==expected and restored is not None
    row_path,row,case,frame=restored;sample=case['frames'][0];observation=frame['observation']
    assert sample['client_rect'] is None and sample['variant']=='half_client'
    run=observation['run'];assert run['selected_operator']==MYRTLE and len(run['operators'])==1
    member=run['operators'][0];buffs=member['recipient_buffs']
    assert member['id']==MYRTLE and member['scope']=='run' and member['fields']=={} and member['skill_ranks']=={}
    assert member['missing_fields']==['level','elite','potential','trust','module_id','module_level','selected_skill']
    assert member['char_buff_ids']==PERSONAL_IDS and member['char_buffs_complete'] is True
    assert buffs['operator_id']==MYRTLE and buffs['ids']==PERSONAL_IDS and type(buffs['count']) is int and buffs['count']==2
    assert buffs['complete'] is True and buffs['status']=='complete' and buffs['issues']==[]
    assert buffs['source']=='owned_operator_buff_popup' and len(buffs['entries'])==2
    assert sorted(e['id'] for e in buffs['entries'])==PERSONAL_IDS
    oracle=read(top['oracle']['path']);mechanisms=read(reference(oracle['mechanism_file']))['char_buffs']
    assert set(oracle['expected_mechanisms'])==set(PERSONAL_IDS)
    for key in PERSONAL_IDS:assert canonical(oracle['expected_mechanisms'][key])==canonical(mechanisms[key])
    native_row=read(reference(oracle['native_receipt']))
    assert native_row['case']=='myrtle_owned:native' and native_row['passed'] is True
    assert canonical(oracle['native_observation'])==canonical(native_row['outputs']['current']['frames'][0]['observation'])
    for entry in buffs['entries']:
        mechanism=mechanisms[entry['id']];raw=mechanism['raw']
        assert entry['name']==raw['outerName'] and entry['description']==raw['desc'] and entry['icon']['id']==raw['iconId']
        assert entry['source']=='owned_operator_buff_popup' and entry['mechanism_source']==mechanism['source']
        score=entry['icon']['score'];assert type(score) in (int,float) and math.isfinite(score) and .94<=score<=1
        assert len(entry['icon']['box'])==len(entry['name_evidence']['box'])==4 and entry['description_evidence']
    held=run['relics'];confirmed=sorted({i['id'] for i in held['icons'] if i.get('confirmed')})
    assert held['ids']==confirmed and 'rogue_6_relic_legacy_99' not in held['ids']
    ambiguous=[i for i in held['icons'] if i.get('id')=='rogue_6_relic_legacy_99'];assert len(ambiguous)==1
    assert ambiguous[0]['confirmed'] is False and ambiguous[0]['candidates']==['rogue_6_relic_final_1','rogue_6_relic_legacy_99']
    probe=read(top['same_frame_probe']['path']);readonly(probe)
    assert probe['source_sha256']==production_sources and probe['source_frame']==sample
    assert probe['kwargs']=={'use_det':False,'use_cls':False} and probe['recognition_calls']==1
    assert probe['no_higher_resolution_input'] is True and len(probe['raw_output'])==1
    assert probe['raw_output'][0][0]=='收藏品' and .95<=probe['raw_output'][0][1]<=1
    context=member['sources']['owned_popup_context'];recheck=context['footer']['收藏品']['footer_recheck']
    assert canonical(recheck)==canonical(probe['current_reported_footer_recheck'])
    assert recheck['source']=='current_owned_popup_footer_rect_recognizer'
    assert recheck['confidence']==probe['raw_output'][0][1] and recheck['original_confidence']==probe['same_frame_baseline_raw_footer'][2]
    assert .9<=recheck['original_confidence']<.95 and len(recheck['box'])==4
    reconstruction=read(row['same_frame_full_run_reconstruction']['path'])
    assert reconstruction['source_sha256']==production_sources and reconstruction['same_frame_source']==sample
    assert reconstruction['actual_same_frame_full_ocr_worker']==row['outputs']['baseline']['frames'][0]
    assert reconstruction['description_probe']==top['existing_description_probe'] and reconstruction['footer_probe']==top['same_frame_probe']
    assert description['source_frame']['sha256']==sample['sha256']
    description_worker=read(reference(description['source_worker']))
    assert description_worker['frames'][0]['actual_raw_ocr']==row['outputs']['baseline']['frames'][0]['actual_raw_ocr']
    assert canonical(reconstruction['full_current_run'])==canonical(run)
    rebuilt_diff=differences(strict(run),strict(reconstruction['independently_rebuilt_current_run']),'/current_run_reconstruction')
    assert rebuilt_diff==reconstruction['strict_differences']==[]
    assert reconstruction['no_new_ocr_calls'] is reconstruction['no_native_values_injected'] is reconstruction['no_history_read'] is True
    assert reconstruction['all_fact_confidence_geometry_leaves_compared'] is True and reconstruction['excluded_keys']==['elapsed_ms']
    calls=reconstruction['recorded_engine_calls'];assert len(calls)==4 and len({c['pixels_sha256'] for c in calls})==4
    assert all(c['kwargs']=={'use_det':False,'use_cls':False} for c in calls)
    footer_calls=[c for c in calls if c['provenance']=='epoch4_same_frame_footer_probe'];assert len(footer_calls)==1
    assert footer_calls[0]['actual_raw']==probe['raw_output'] and footer_calls[0]['shape']==probe['crop_shape'] and footer_calls[0]['dtype']=='uint8'
    local_calls=[c for c in calls if c['provenance']=='sealed_epoch3_exact_same_frame_description_probe'];assert len(local_calls)==3
    assert {c['pixels_sha256'] for c in local_calls}=={l['crop_pixels_sha256'] for l in description['lines']}
    for line in description['lines']:
        call=next(c for c in local_calls if c['pixels_sha256']==line['crop_pixels_sha256'])
        assert call['actual_raw']==line['raw'] and call['shape']==line['crop_shape'] and call['dtype']=='uint8'
    training=next(e for e in buffs['entries'] if e['id']=='rogue_6_from_relic_1')['description_verification']
    assert training['source']=='owned_popup_current_and_local_otsu_reconfirm' and training['local_ocr_calls']==3
    choices=[{'index':i,'source':'current_full_ocr' if i==0 else 'current_local_otsu_rec',
        'original_confidence':line['original']['confidence'],'reconfirm_confidence':line['raw'][0][1],
        'selected_confidence':line['original']['confidence'] if i==0 else line['raw'][0][1]}
        for i,line in enumerate(description['lines'])]
    assert training['line_choices']==choices and all(.95<=c['selected_confidence']<=1 for c in choices)
    if popup_freeze is not None:
        freeze_path=relative(popup_freeze);frozen=read(freeze_path)
        assert frozen['passed'] is True and frozen['source_sha256']==production_sources;readonly(frozen)
        assert frozen['strict_equal_cases']==2 and frozen['restored_cases']==1 and frozen['real_cases']==3
        assert frozen['popup_receipt']=={'path':POPUP.as_posix(),'sha256':sha(POPUP)}
        assert frozen['immutable_summary']==top['immutable_summary']
        assert frozen['verifier_sha256']==top['verifier_sha256'] and frozen['hybrid_verifier_sha256']==top['hybrid_verifier_sha256']
        owned=frozen['owned_files_and_receipts_sha256'];verify(owned,evidence)
        required={k:v for k,v in closed.items() if k not in production_sources}
        assert all(owned.get(k)==v for k,v in required.items()),('Popup freeze does not cover recursive closure',sorted(k for k,v in required.items() if owned.get(k)!=v))
        for name,digest in owned.items():close(name,digest)
        close(freeze_path,sha(freeze_path))
        required={k:v for k,v in closed.items() if k not in production_sources and k!=freeze_path}
        assert all(owned.get(k)==v for k,v in required.items()),('Popup freeze misses transitive evidence',sorted(k for k,v in required.items() if owned.get(k)!=v))
    return {'top':POPUP.as_posix(),'top_sha256':sha(POPUP),'row':row_path,'row_sha256':sha(row_path),
        'current_worker':row['worker_receipts']['current']['path'],'current_worker_sha256':row['worker_receipts']['current']['sha256'],
        'image':sample['file'],'image_sha256':sample['sha256'],'recovery_verifier':POPUP_VERIFIER.as_posix(),
        'fixture_sha256':closed,'source':'sealed_actual_current_rapidocr_worker','new_ocr_calls':0,
        'char_buff_ids':PERSONAL_IDS[:],'count':2,'personal_buff_complete_required':True,
        'held_inventory_complete_claimed':False,'held_inventory_policy':HELD_POLICY,
        'current_confirmed_held_ids':confirmed,'held_legacy_99_ambiguous_not_injected':True,
        'strict_equal_cases':2,'restored_cases':1,'formal_case_count_unchanged':23,
        'same_frame_full_run_reconstruction':row['same_frame_full_run_reconstruction'],
        'opaque_historical_serialization_failure':{k:v for k,v in HISTORICAL_OPAQUE.items() if k in closed},
        'opaque_scope':'One pinned historical serialization-failure byte artifact; no current receipt parsing exemption.',
        'resolved_aliases':[resolved_aliases[k] for k in sorted(resolved_aliases)],
        'historical_alias_scope':'Only enumerated logical-path/old-SHA pairs use byte-identical saved archives; current top/source checks are direct.',
        'external_source_metadata':[external_source_metadata[k] for k in sorted(external_source_metadata)],
        'external_source_mirrors':[external_source_mirrors[k] for k in sorted(external_source_mirrors)],
        'external_metadata_scope':'Only pinned camera_reference records and exact audit mirrors verified against that source; local frame/evidence references remain mandatory.',
        'data_reference_resolution':{'count':len(resolved_data_references),'schemas':DATA_REFERENCE_SCHEMAS,
            'scope':'Known archived data asset schemas resolve their declared DATA-relative files to current public rouge/data assets, with exact SHA verification.'},
        'all_fact_confidence_geometry_leaves_compared':True,'excluded_keys':['elapsed_ms']}


def research_evidence(before,evidence):
    """Old profile source belongs to the archived 0.58 baseline, not 0.59."""
    profile=read(PROFILE)
    assert profile['passed'] and profile['strict_run_differences']==[] and profile['source_drift']==[]
    assert profile['source_sha256']==profile['source_sha256_after']
    assert profile['excluded_keys']==['elapsed_ms'] and profile['provider_or_global_patches']==0
    for name,value in profile['source_sha256'].items():
        if name.startswith('rouge/'):
            assert before['source_hashes'][name]==value,('Profile baseline source',name)
            verify({(BEFORE/name).as_posix():value},evidence)
        else:verify({name:value},evidence)
    verify({profile['profile_pstats']:profile['profile_pstats_sha256'],
        profile['baseline_receipt']:profile['baseline_sha256'],profile['row']:profile['row_sha256'],
        profile['sample']['file']:profile['sample_sha256']},evidence)
    # The profile stores analysis-client coordinates before map_evidence;
    # its pinned row stores public source-frame coordinates after mapping.
    # Execute only the original pure-stdlib map function from the verified
    # archived source, without importing viewport/OCR/capture modules.
    profile_row=read(profile['row'])
    assert profile_row['case']==profile['case']
    source_frame=profile_row['outputs']['current']['frames'][0]
    assert differences(strict(profile['expected_source_run']),strict(source_frame['observation']['run']))==[]
    viewport_source=BEFORE/'rouge/viewport.py'
    assert sha(viewport_source)==profile['source_sha256']['rouge/viewport.py']
    tree=ast.parse(public_path(viewport_source).read_text(encoding='utf-8'))
    functions=[node for node in tree.body if isinstance(node,ast.FunctionDef) and node.name=='map_evidence']
    assert len(functions)==1
    mapping_scope={}
    exec(compile(ast.Module(body=functions,type_ignores=[]),str(viewport_source),'exec'),mapping_scope)
    mapped={'run':json.loads(json.dumps(profile['actual_run'],ensure_ascii=False))}
    mapping_scope['map_evidence'](mapped,source_frame['observation']['viewport'])
    assert differences(strict(profile['expected_source_run']),strict(mapped['run']))==[]
    evidence[PROFILE.as_posix()]=sha(PROFILE)

    receipt=read(THREAD_RECEIPT);fixture_path=THREADS/'fixtures.json';fixtures=read(fixture_path)
    analysis_path=THREADS/'analysis.json';analysis=read(analysis_path)
    assert receipt['passed'] and receipt['completed_workers']==receipt['expected_workers']==8
    assert receipt['source_stable'] and receipt['source_sha256']==receipt['source_sha256_after']==fixtures['source_sha256']
    assert len(receipt['comparisons'])==16 and all(c['strict_same_result'] for c in receipt['comparisons'])
    verify(receipt['source_sha256'],evidence)
    assert analysis['passed'] and analysis['all_16_results_identical'] and analysis['production_code_modified'] is False
    assert sha(THREAD_RECEIPT)==analysis['receipt_sha256']
    assert sha('.cache/research/run-performance-059/thread_probe.py')==analysis['script_sha256']
    assert fixtures['baseline_sha256']==sha('HYBRID_0.58_VERIFICATION.json')
    evidence['HYBRID_0.58_VERIFICATION.json']=fixtures['baseline_sha256']
    assert {c['case'] for c in fixtures['cases']}=={'kaltsit_owned:native','run-mechanist-selected:native'}
    frozen={c['case']:c for c in fixtures['cases']}
    for case in fixtures['cases']:
        verify({case['file']:case['sha256'],case['source_row']:case['source_row_sha256'],
            case['source_sample']['file']:case['source_sample']['sha256']},evidence)
    order=('default','1','2','4','4','2','1','default');workers=[]
    for index,threads in enumerate(order):
        path=THREADS/f'worker-{index:02d}-{threads}.json';record=read(path);workers.append(record)
        assert record['passed'] and record['source_stable'] and record['cv_threads_request']==threads
        assert record['source_sha256']==record['source_sha256_after']==receipt['source_sha256']
        assert record['fixture_inventory_sha256']==sha(fixture_path)
        assert record['production_code_modified'] is False
        assert record['cv_threads_actual']==(18 if threads=='default' else int(threads))
        assert {c['case'] for c in record['cases']}==set(frozen)
        for case in record['cases']:
            assert case['fixture_sha256']==frozen[case['case']]['sha256']
            assert case['pixel_input_sha256']==frozen[case['case']]['roi_pixels_sha256']
        for key in ('private_state_read','game_actions','chat_requests'):assert not record[key]
    baseline={c['case']:c['original_result'] for c in workers[0]['cases']}
    for worker in workers:
        for case in worker['cases']:assert canonical(case['original_result'])==canonical(baseline[case['case']])
    for row in analysis['means']:
        values=[c['elapsed_ms'] for worker in workers if worker['cv_threads_request']==row['threads']
            for c in worker['cases'] if c['case']==row['case']]
        assert values==row['measurements_ms'] and statistics.mean(values)==row['mean_ms']
    # Every artifact in this fixed, public experiment is part of the closure.
    for path in public_path(THREADS).iterdir():
        if path.is_file():evidence[relative(path)]=sha(path)
    for name in ('scripts/profile_run_059.py','.cache/research/run-performance-059/thread_probe.py',
        '.cache/research/run-performance-059/REPORT.md'):
        evidence[name]=sha(name)
    return {'profile_receipt':PROFILE.as_posix(),'thread_receipt':THREAD_RECEIPT.as_posix(),
        'thread_results_exact':16,'thread_default_changed':False,
        'thread_conclusion':'No stable significant benefit demonstrated; original default retained.',
        'limits':['Two existing development bars; two repeats per setting.',
                  'Existing GUI/sampling process remained running; timing includes background workload.']}


def thread_calls(path):
    tree=ast.parse(public_path(path).read_text(encoding='utf-8-sig'))
    return sorted(ast.dump(node,include_attributes=False) for node in ast.walk(tree)
        if isinstance(node,ast.Call) and
        ((isinstance(node.func,ast.Attribute) and node.func.attr=='setNumThreads') or
         (isinstance(node.func,ast.Name) and node.func.id=='setNumThreads')))


def main(options):
    started=time.perf_counter()
    paths=[Path(f'{name}_0.59_VERIFICATION.json') for name in
        ('CORE','NUMERIC_REPLAY','NATIVE_UI','RECOGNITION_UI','PACKAGE')]
    paths += [Path('APP_0.59_LAUNCH_VERIFICATION.json'),Path('HYBRID_0.59_VERIFICATION.json')]
    core,numeric,native,ui,package,app,hybrid=[read(p) for p in paths]
    for record in (core,numeric,native,ui,package):
        assert record['passed'] is True and record['version']=='0.59.0'
    feature_path=Path(relative(options.feature_freeze));hybrid_freeze_path=Path(relative(options.hybrid_freeze))
    popup_freeze_path=Path(relative(options.popup_freeze))
    source_freeze_path=Path(relative(options.source_freeze));engine_path=Path(relative(options.engine_freeze))
    paths += [feature_path,hybrid_freeze_path,source_freeze_path,engine_path,BEFORE/'manifest.json']
    feature,hybrid_freeze,freeze,engine,before=[read(p) for p in paths[-5:]]
    paths.append(popup_freeze_path)
    assert feature['passed'] and hybrid_freeze['passed'] and engine['passed']
    assert before['baseline']=='0.58.0' and before['private_state_copied'] is False
    assert freeze['version']=='0.59.0' and freeze['private_state_copied'] is False
    assert hybrid_freeze['real_cases']==23 and hybrid_freeze['strict_differences']==0
    assert hybrid['passed'] and hybrid['strict_equal_cases']==23
    assert len(hybrid['expected_cases'])==23 and not hybrid['missing_cases'] and not hybrid['failed_cases']
    assert hybrid['all_fact_confidence_geometry_leaves_compared'] and hybrid['excluded_keys']==['elapsed_ms']
    assert not (Path.home()/'.codex/automations/1-3/automation.toml').exists()
    assert not core['failures'] and not core['errors'] and not core['source_drift_during_tests']
    assert core['maintained_test_files_sealed'] and core['runner_sealed']
    old_core=read('CORE_0.58_VERIFICATION.json');paths.append(Path('CORE_0.58_VERIFICATION.json'))
    assert old_core['passed'] and len(old_core['test_modules'])==85
    assert core['test_modules'][:85]==old_core['test_modules'] and len(core['test_modules'])==87
    assert set(core['test_modules'][85:])=={'tests.test_page_features_059','tests.test_recognition_059'}
    assert numeric['cases']==numeric['exact_structured_unchanged']==732
    assert numeric['baseline_version']=='0.58.0' and not numeric['unexpected_changes'] and numeric['allowances']==[]
    assert not numeric['source_drift'] and numeric['source_stable']
    assert native['private_data_isolated'] and ui['private_state_isolated']
    assert package['offline_build'] and package['private_runtime_packaged'] is False
    assert app['version']=='0.59.0' and app['window_title']=='黑流树海助手 0.59 · 识别与计算测试版'
    for key in ('same_run_preserved','history_preserved','settings_and_bindings_unchanged',
        'window_visible_and_restored','only_one_project_window','foreground_verified','run_cmd_startup_verified'):
        assert app[key],('Application launch verification',key)
    assert len(app['stability_checks'])>=2 and all(c['visible_and_responsive'] for c in app['stability_checks'])
    assert app['run_state_writes_by_upgrade_script']==0 and app['launcher_stderr_bytes']==0
    assert sha('run.cmd')==app['launcher_sha256']
    for record in (core,numeric,native,ui,package,hybrid):verify(record['source_sha256'])
    verify(numeric['full_formal_source_sha256'])
    for record in (native,ui,package):
        assert record['source_sha256']==record['source_sha256_after'] and not record['source_drift']
    verify(engine['files']);verify(feature['source_sha256']);verify(freeze['source_hashes'])
    verify(hybrid_freeze['public_source_sha256']);verify(hybrid_freeze['owned_files_and_receipts_sha256'])
    paths.extend(Path(name) for name in hybrid_freeze['owned_files_and_receipts_sha256'])
    production_sources={name:value for name,value in core['source_sha256'].items() if name.startswith('rouge/')}
    assert freeze['source_hashes']==production_sources==hybrid['source_sha256']==hybrid_freeze['public_source_sha256']

    evidence={**engine['files'],**feature['source_sha256'],
        **hybrid_freeze['owned_files_and_receipts_sha256'],
        core['test_log']:core['test_log_sha256'],package['wheel']:package['wheel_sha256'],
        numeric['worker_receipt']:numeric['worker_receipt_sha256'],numeric['current_output']:numeric['current_output_sha256'],
        numeric['baseline_output']:numeric['baseline_sha256']}
    evidence.update(hybrid['replay_receipts']);verify(evidence)
    assert canonical(read(numeric['current_output']))==canonical(read(numeric['baseline_output']))
    assert len(read(numeric['current_output']))==732
    referenced(hybrid,('immutable_summary','actual_animation_pixel_evidence','baseline_package_seal'),evidence)
    referenced(feature,('core_receipt','test_log','original_legacy_test','experiment_evidence'),evidence)
    assert sha('scripts/verify_hybrid_059.py')==hybrid['verifier_sha256']
    epoch=public_path(hybrid['immutable_summary']['path']).parent.relative_to(ROOT)
    inventory_path=epoch/'inventory.json';inventory=read(inventory_path);paths.append(inventory_path)
    baseline=read(hybrid['baseline_package_seal']['path'])
    assert inventory['source_sha256']==production_sources and inventory['verifier_sha256']==hybrid['verifier_sha256']
    assert sha(BEFORE/'manifest.json')==baseline['before_manifest_sha256']
    assert len(inventory['cases'])==23 and {c['id'] for c in inventory['cases']}==set(hybrid['expected_cases'])
    animations={c['id'] for c in inventory['cases'] if c['group']=='continuous'}
    assert animations=={'operator-kaltsit:animation','myrtle_owned:animation'}
    for mapping in (baseline['frozen_original_sources'],baseline['supplemented_current_public_media']):
        verify({(epoch/'baseline-source'/name).as_posix():value for name,value in mapping.items()},evidence)
    rows={}
    for path,digest in hybrid['replay_receipts'].items():
        row=read(path);assert row['passed'] and not row['strict_semantic_differences']
        assert row['source_sha256']==production_sources and row['verifier_sha256']==hybrid['verifier_sha256']
        assert row['case'] not in rows;rows[row['case']]=row
        old,new=row['outputs']['baseline']['frames'],row['outputs']['current']['frames']
        assert len(old)==len(new)
        for first,second in zip(old,new):
            assert set(first['observation'])==set(second['observation'])==set(FIELDS)
            assert canonical(strict(first['observation']))==canonical(strict(second['observation']))
    assert set(rows)==set(hybrid['expected_cases'])
    for case in inventory['cases']:
        for sample in case['frames']:verify({sample['file']:sample['sha256']},evidence)
    popup=popup_recovery_evidence(production_sources,evidence,popup_freeze_path)
    assert ui['original_actual_reader_checks']==6 and ui['sealed_current_worker_recovery_checks']==4 and len(ui['checks'])==10
    assert ui['recovery_new_ocr_calls']==0 and ui['personal_buff_complete_required'] is True
    assert ui['held_inventory_complete_claimed'] is False and ui['held_legacy_99_ambiguous_not_injected'] is True
    assert ui['source_sha256'][relative(__file__)]==sha(__file__)
    ui_popup=ui['recovery_evidence'];verify(ui_popup['fixture_sha256'],evidence)
    for key in popup:
        if key!='fixture_sha256':assert canonical(ui_popup[key])==canonical(popup[key]),('UI recovery evidence differs',key)
    assert all(ui['source_sha256'].get(name)==digest for name,digest in ui_popup['fixture_sha256'].items())

    # Compare the original 20 binary assets with the actual 0.58 snapshot.
    # The old manifest hash is intentionally not checked against current 0.59.
    original_binary={name:value for name,value in before['source_hashes'].items()
        if name.startswith('rouge/data/page-features/') and Path(name).suffix in ('.png','.npz')}
    assert len(original_binary)==20;verify(original_binary,evidence)
    if 'original_twenty_binary_assets_sha256' in feature:
        assert feature['original_twenty_binary_assets_sha256']==original_binary
    pages=read('rouge/data/page-features/manifest.json');visual=read('rouge/data/visual-anchors/manifest.json')
    assert pages['facts_from_features'] is False and len(pages['pages'])==5 and len(visual['entries'])==7
    for page in pages['pages']:
        verify({page['source']:page['source_sha256']},evidence)
        verify({'rouge/data/page-features/'+page['features']:page['features_sha256']},evidence)
        verify({'rouge/data/page-features/'+a['patch']:a['patch_sha256'] for a in page['anchors']},evidence)
    assets=[p for group in ('page-features','visual-anchors')
        for p in public_path('rouge/data/'+group).iterdir() if p.is_file()]
    assert len(assets)==package['assets_checked']==34
    assert package['isolated_import']['page_feature_pages']==5 and package['isolated_import']['visual_references']==7
    changed=sorted(name for name,value in before['source_hashes'].items() if sha(name)!=value)
    production=[name for name in changed if name.startswith('rouge/')]
    assert production==sorted(ALLOWED_EXISTING_PRODUCTION),production
    added=sorted(set(production_sources)-set(before['source_hashes']))
    assert len(added)==5 and all(name.startswith('rouge/data/page-features/') and
        Path(name).suffix in ('.png','.npz') for name in added),added
    for name in before['source_hashes']:
        if name.startswith('rouge/') and Path(name).suffix=='.py':
            assert thread_calls(name)==thread_calls(BEFORE/name),('Thread runtime change',name)
    research=research_evidence(before,evidence)
    for record in (native,ui,package,hybrid,app):
        assert record['game_actions']==0 and record['chat_requests']==0
    verify(evidence);paths.extend(Path(name) for name in evidence)
    paths.append(Path('.cache/research/run-performance-059/REPORT.md'))
    public=set(core['source_sha256'])
    public.update(('README.md','PROJECT_PROGRESS.md','PROJECT_COMPLETED.md','WORK_IN_PROGRESS.md',
        'BATCH_0.59.md','pyproject.toml','run.cmd',relative(__file__)))
    public.update(p.relative_to(ROOT).as_posix() for p in (ROOT/'scripts').glob('*059*.py'))
    receipt={'version':'0.59.0','passed':True,'verified_at':time.time(),
        'tests_run':core['tests_run'],'current_tests_passed':core['current_tests_passed'],
        'historical_tests_skipped':core['historical_tests_skipped'],'failures':0,'errors':0,
        'numeric_defaults_exact':732,'numeric_allowances':[],'strict_hybrid_cases':23,
        'strict_public_fields':list(FIELDS),'excluded_semantic_keys':['elapsed_ms'],
        'packaged_reference_assets':34,'page_templates':5,'visual_references':7,
        'original_twenty_binary_assets_unchanged':True,
        'changed_existing_sources':changed,'changed_existing_production_files':production,
        'added_production_assets':added,'performance_research':research,
        'popup_recovery':popup,'popup_freeze':popup_freeze_path.as_posix(),
        'popup_strict_preservation_cases':2,'popup_current_evidence_restoration_cases':1,
        'personal_buff_complete_required':True,'held_inventory_complete_claimed':False,
        'held_legacy_99_ambiguous_not_injected':True,
        'receipt_sha256':{relative(p):sha(p) for p in sorted(set(paths))},
        'source_sha256':{name:sha(name) for name in sorted(public)},
        'test_source_monitoring':'Production, maintained test sources and CORE runner monitored at both ends.',
        'all_priority_1_completed':False,'all_priority_1_3_completed':False,
        'automation_1_3_deleted':True,'game_actions':0,'chat_requests':0,
        'scope':'Pure visual page controls select OCR priority; complete current detector boxes and exact batch reuse retained.',
        'elapsed_seconds':time.perf_counter()-started,
        'limits':['Cold reads retain all REC; no general first-frame speed claim.',
            'Two actual animation pairs are operator-kaltsit detail and myrtle_owned popup; kaltsit_owned is cold.',
            'Existing development/training samples and scale/padding derivatives do not establish independent accuracy.',
            'Text completeness refers to current detector boxes, not every small text on any layout.',
            'Three extra derived popup cases preserve two observations and recover one page/run; they are separate from the 23 strict cases.',
            'Recovered Myrtle personal buffs are complete; low-resolution held legacy99 stays ambiguous and is not injected from the native oracle.',
            'Thread probe showed no stable significant benefit and retained the original default.',
            'Remaining mechanisms and recognition coverage stay in PROJECT_PROGRESS.md.']}
    output=public_path(options.output)
    with output.open('x',encoding='utf-8') as handle:json.dump(receipt,handle,ensure_ascii=False,indent=2)
    print(json.dumps({key:receipt[key] for key in ('passed','tests_run','current_tests_passed','strict_hybrid_cases')},ensure_ascii=False))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--feature-freeze',required=True)
    parser.add_argument('--hybrid-freeze',required=True)
    parser.add_argument('--popup-freeze',required=True)
    parser.add_argument('--source-freeze',default='.cache/batch-059-source-freeze.json')
    parser.add_argument('--engine-freeze',default=ENGINE.as_posix())
    parser.add_argument('--output',default='FINAL_0.59_VERIFICATION.json')
    main(parser.parse_args())
