"""Current regressions, pinned assets and the limited fixed-map geometry scope."""
import hashlib,json,math,sys,time,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from rouge.battle_preview import battle_data,DATA,spawn_rows
from rouge.map_projection import projection_data,projection_for,grid_digest


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    started=time.perf_counter();base=ROOT/'.cache/projection-044'
    previous=json.loads((ROOT/'FINAL_0.43_VERIFICATION.json').read_text(encoding='utf-8'))
    changed={name for name,sha in previous['source_sha256'].items() if digest(ROOT/name)!=sha}
    assert changed=={'rouge/app.py','rouge/battle_view.py','pyproject.toml'},changed
    old=json.loads((ROOT/'RECOGNITION_0.43_VERIFICATION.json').read_text(encoding='utf-8'))
    modules=[*old['test_modules'],'tests.test_map_projection_044']
    with (base/'tests.log').open('x',encoding='utf-8') as stream:
        result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(modules))
    assert result.wasSuccessful(),(result.failures,result.errors)
    assert result.testsRun==491 and len(result.skipped)==70,(result.testsRun,len(result.skipped))
    data=projection_data();stages=battle_data()['stages'];image_count=total_bytes=0
    for stage in stages.values():
        path=DATA/stage['image']['file']
        assert digest(path)==stage['image']['sha256'];image_count+=1;total_bytes+=path.stat().st_size
    assert image_count==105 and total_bytes==34951925
    checks=[];rows=points=clickable=0
    for sid,binding in data['stages'].items():
        s=stages[sid];image=s['image'];p=projection_for(s,digest(DATA/image['file']),(image['width'],image['height']))
        assert p is not None,sid
        assert grid_digest(s)==data['calibrations'][binding['calibration']]['grid_sha256']
        for row in spawn_rows(sid):
            start=row['route']['start']
            if not start:continue
            pixel=p.project(start);assert pixel is not None,(sid,start)
            assert p.cell_at(*pixel)==start,(sid,start)
            assert row['absolute_time'] is None and row['probability'] is None
            rows+=1
            for point in row['route']['points']:
                assert p.project(point) is not None,(sid,point);points+=1
        for r,line in enumerate(s['map']):
            for c,_ in enumerate(line):
                cell={'row':r,'col':c};x,y=p.project(cell)
                if 0<=x<p.width and 0<=y<p.height:assert p.cell_at(x,y)==cell;clickable+=1
    for sid,c in data['calibrations'].items():
        s=stages[sid];p=projection_for(s,s['image']['sha256'],(c['width'],c['height']))
        for point in c['checks']:
            error=math.dist(p.project(point),point['observed_pixel']);assert error<=c['tolerance_px']
            checks.append({'stage':sid,'cue':point['cue'],'error_px':error})
    research=ROOT/'.cache/research/map-projection-044'
    sources=json.loads((research/'source-receipts.json').read_text(encoding='utf-8'))
    for source in sources:
        if 'error' in source:continue
        raw=(research/source['file']).read_bytes()
        assert hashlib.sha256(raw).hexdigest()==source['sha256']
        assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==source['blob']
    tree=json.loads((research/'resource-camera-tree.json').read_text(encoding='utf-8'))
    for entry in tree['tree']:
        source=next(r for r in sources if r['file']=='resource-'+entry['path'])
        assert entry['sha']==source['blob'] and entry['size']==source['bytes']
    inputs=json.loads((research/'calibration-input.json').read_text(encoding='utf-8'))
    assert digest(research/'calibration-input.json')==data['source']['landmarks_sha256']
    rejected=[c['id'] for c in inputs['calibrations'] if c.get('enabled') is False]
    assert rejected==['ro6_n_1_3'] and rejected[0] not in data['stages']
    tracked=['rouge/map_projection.py','rouge/battle_view.py','rouge/app.py','pyproject.toml',
        'rouge/data/battle-map-projections.json','tests/test_map_projection_044.py',
        'scripts/build_map_projections_044.py','scripts/verify_map_projection_044.py']
    receipt={'version':'0.44.0','verified_at':time.time(),'passed':True,
        'tests_run':result.testsRun,'current_tests_passed':result.testsRun-len(result.skipped),
        'new_unit_tests':18,'historical_combat_tests_skipped':len(result.skipped),
        'failures':len(result.failures),'errors':len(result.errors),'test_modules':modules,
        'test_log':str((base/'tests.log').relative_to(ROOT)),'test_log_sha256':digest(base/'tests.log'),
        'calibrated_original_bitmaps':len(data['calibrations']),'bound_stages':list(data['stages']),
        'uncalibrated_stage_count':len(stages)-len(data['stages']),
        'independent_bitmap_landmarks':checks,'max_independent_error_px':max(c['error_px'] for c in checks),
        'original_pixel_tolerance':4.0,'tolerance_is_not_whole_map_precision_proof':True,
        'calibrated_spawn_rows':rows,'calibrated_route_point_references':points,'tile_center_inverse_checks':clickable,
        'source_images_checked':image_count,'source_image_bytes':total_bytes,
        'source_images_and_battle_data_unchanged':True,'source_receipts_git_blob_verified':True,
        'rejected_calibrations':rejected,'initial_rejected_fit_log':'.cache/projection-044/build.log',
        'actual_pathfinding_claimed':False,'actual_absolute_spawn_timeline_claimed':False,
        'no_live_battle_capture_required':True,'runtime_external_camera_code_imported':False,
        'numeric_and_recognition_sources_unchanged_from':'FINAL_0.43_VERIFICATION.json',
        'inherited_numeric_public_cases':old['exact_public_output_cases'],'numeric_public_replay_rerun':False,
        'changed_existing_source_files':sorted(changed),'source_hashes':{n:digest(ROOT/n) for n in tracked},
        'game_commit':data['source']['game_commit'],'resource_commit':data['source']['resource_commit'],
        'game_actions':0,'chat_requests':0,'seconds':time.perf_counter()-started}
    (ROOT/'PROJECTION_0.44_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in receipt.items() if k not in ('test_modules','source_hashes','independent_bitmap_landmarks')},ensure_ascii=False))


if __name__=='__main__':main()
