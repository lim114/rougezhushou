"""Current regressions and append-only geometry/presentation source guards."""
import hashlib,json,math,sys,time,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from rouge.battle_preview import battle_data,DATA,spawn_rows
from rouge.map_projection import projection_data,projection_for,grid_digest


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    started=time.perf_counter();base=ROOT/'.cache/refresh-045'
    previous=json.loads((ROOT/'FINAL_0.44_VERIFICATION.json').read_text(encoding='utf-8'))
    changed={n for n,h in previous['source_sha256'].items() if digest(ROOT/n)!=h}
    expected={'rouge/app.py','rouge/battle_view.py','rouge/reporting.py','rouge/estimate.py',
              'rouge/battle_preview.py','rouge/data/battle-map-projections.json','pyproject.toml',
              'tests/test_map_projection_044.py','tests/test_spawn_reference_040.py','tests/test_battle_preview_039.py'}
    assert changed==expected,changed
    before=ROOT/'.cache/batch-045-before'
    for n in ('rouge/estimate.py','rouge/reporting.py'):
        a=(before/n).read_text(encoding='utf-8');b=(ROOT/n).read_text(encoding='utf-8')
        assert b==a.replace('预计基础数值：','预计属性（含已支持的天赋和藏品）：'),n
    a=(before/'rouge/battle_preview.py').read_text(encoding='utf-8')
    b=(ROOT/'rouge/battle_preview.py').read_text(encoding='utf-8')
    assert a.split('def enemy_text(entry):')[0]==b.split('def enemy_text(entry):')[0]
    assert a.split('def spawn_text(row,stage_id):')[1]==b.split('def spawn_text(row,stage_id):')[1]
    old=json.loads((ROOT/'PROJECTION_0.44_VERIFICATION.json').read_text(encoding='utf-8'))
    modules=[*old['test_modules'],'tests.test_ui_refresh_045','tests.test_view_catalog_045']
    with (base/'all-tests.log').open('x',encoding='utf-8') as stream:
        result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(modules))
    assert result.wasSuccessful(),(result.failures,result.errors)
    assert result.testsRun==524 and len(result.skipped)==70,(result.testsRun,len(result.skipped))
    data=projection_data();prior=json.loads((before/'rouge/data/battle-map-projections.json').read_text(encoding='utf-8'))
    assert len(data['calibrations'])==4 and len(data['stages'])==8
    assert all(data['calibrations'][k]==v for k,v in prior['calibrations'].items())
    assert all(data['stages'][k]==v for k,v in prior['stages'].items())
    original=json.loads((ROOT/'.cache/research/map-projection-044/calibration-input.json').read_text(encoding='utf-8'))
    rejected=next(e for e in original['calibrations'] if e['id']=='ro6_n_1_3')
    accepted=data['calibrations']['ro6_n_1_3']
    assert rejected['enabled'] is False and len(accepted['anchors'])==6
    assert [[p['row'],p['col'],*p['observed_pixel'],p['cue']] for p in accepted['checks']]==rejected['checks']
    assert digest(ROOT/data['source']['added_landmarks_045']['file'])==data['source']['added_landmarks_045']['sha256']
    images=total=rows=points=inverse_checks=0;checks=[]
    stages=battle_data()['stages']
    for s in stages.values():
        path=DATA/s['image']['file'];assert digest(path)==s['image']['sha256']
        images+=1;total+=path.stat().st_size
    assert images==105 and total==34951925
    for sid in data['stages']:
        s=stages[sid];p=projection_for(s,s['image']['sha256'],(s['image']['width'],s['image']['height']))
        assert p is not None
        for row in spawn_rows(sid):
            start=row['route']['start']
            if not start:continue
            pixel=p.project(start);assert p.cell_at(*pixel)==start
            assert row['absolute_time'] is None and row['probability'] is None;rows+=1
            for point in row['route']['points']:assert p.project(point) is not None;points+=1
        for r,line in enumerate(s['map']):
            for c,_ in enumerate(line):
                cell={'row':r,'col':c};x,y=p.project(cell)
                if 0<=x<p.width and 0<=y<p.height:assert p.cell_at(x,y)==cell;inverse_checks+=1
    for sid,calibration in data['calibrations'].items():
        s=stages[sid];p=projection_for(s,s['image']['sha256'],(s['image']['width'],s['image']['height']))
        assert grid_digest(s)==calibration['grid_sha256']
        for point in calibration['checks']:
            error=math.dist(p.project(point),point['observed_pixel']);assert error<=4
            checks.append({'stage':sid,'cue':point['cue'],'error_px':error})
    unbound=[s for sid,s in stages.items() if sid not in data['stages']]
    tracked=sorted(set(previous['source_sha256'])|{'rouge/ui_state.py','rouge/view_catalog.py',
        'rouge/operator_summary.py','rouge/data/view-catalog.json','tests/test_ui_refresh_045.py',
        'tests/test_view_catalog_045.py','scripts/build_view_catalog_045.py','scripts/build_map_projections_045.py',
        'scripts/verify_refresh_045.py'})
    receipt={'version':'0.45.0','passed':True,'verified_at':time.time(),'tests_run':result.testsRun,
        'current_tests_passed':result.testsRun-len(result.skipped),'new_unit_tests':33,
        'historical_combat_tests_skipped':len(result.skipped),'failures':len(result.failures),'errors':len(result.errors),
        'test_modules':modules,'test_log':str((base/'all-tests.log').relative_to(ROOT)),
        'test_log_sha256':digest(base/'all-tests.log'),'changed_existing_tracked_files':sorted(changed),
        'calculation_functions_unchanged':True,'estimate_and_report_only_heading_changed':True,
        'enemy_preview_numerical_reference_unchanged':True,'recognition_and_run_state_sources_unchanged':True,
        'source_sha256':{n:digest(ROOT/n) for n in tracked},'all_105_map_bytes_unchanged':True,
        'source_map_bytes':total,'calibrated_bitmaps':4,'bound_stages':list(data['stages']),
        'remaining_stages':len(unbound),'remaining_bitmap_identities':len({s['image']['sha256'] for s in unbound}),
        'prior_calibration_records_unchanged':True,'acute_independent_checks_unchanged_from_rejected_044':True,
        'independent_landmarks':checks,'max_error_px':max(c['error_px'] for c in checks),'tolerance_px':4,
        'not_a_whole_map_precision_guarantee':True,'calibrated_spawn_rows':rows,
        'calibrated_route_point_references':points,'visible_tile_center_inverse_checks':inverse_checks,
        'synthetic_refresh_tests_only':True,'game_actions':0,'chat_requests':0,
        'actual_absolute_timeline_claimed':False,'actual_pathfinding_claimed':False,
        'numeric_public_cases_inherited_from':'RECOGNITION_0.43_VERIFICATION.json',
        'inherited_numeric_cases':732,'numeric_public_replay_rerun':False,
        'new_recognition_speed_claim':False,'seconds':time.perf_counter()-started}
    (ROOT/'REFRESH_0.45_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in receipt.items() if k not in ('test_modules','source_sha256','independent_landmarks')},ensure_ascii=False))


if __name__=='__main__':main()
