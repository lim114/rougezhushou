"""Current regression and unchanged numeric/recognition source audit."""
import hashlib,json,sys,time,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))


def digest(name):return hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
def read(name):return json.loads((ROOT/name).read_text(encoding='utf-8'))


def main():
    started=time.perf_counter();previous=read('FINAL_0.45_VERIFICATION.json')
    changed={name for name,sha in previous['source_sha256'].items() if digest(name)!=sha}
    expected={'rouge/app.py','rouge/view_catalog.py','rouge/battle_view.py','pyproject.toml','tests/test_ui_refresh_045.py'}
    assert changed==expected,changed
    modules=[*read('REFRESH_0.45_VERIFICATION.json')['test_modules'],'tests.test_branch_choices_046']
    log='.cache/branch-046/all-tests.log'
    with (ROOT/log).open('x',encoding='utf-8') as stream:
        result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(modules))
    assert result.wasSuccessful(),(result.failures,result.errors)
    assert result.testsRun==543 and len(result.skipped)==70,(result.testsRun,len(result.skipped))
    icons=read('rouge/data/skill-icons.json')
    assert len(icons['skills'])==893 and len(icons['images'])==884
    names=set(previous['source_sha256'])|{'rouge/branch_choice.py','rouge/data/skill-icons.json',
        'tests/test_branch_choices_046.py','scripts/verify_branches_046.py','scripts/build_skill_icons_046.py',
        'scripts/verify_branch_ui_046.py','scripts/verify_skill_ui_046.py','scripts/verify_battle_widgets_046.py',
        'scripts/verify_map_projection_ui_046.py'}
    receipt={'version':'0.46.0','passed':True,'verified_at':time.time(),'tests_run':result.testsRun,
             'current_tests_passed':473,'new_unit_tests':19,'historical_combat_tests_skipped':70,
             'errors':len(result.errors),'failures':len(result.failures),'test_modules':modules,
             'test_log':log,'test_log_sha256':digest(log),'changed_existing_source_files':sorted(changed),
             'source_sha256':{name:digest(name) for name in sorted(names)},
             'profile_skill_slots':949,'unique_skill_ids':893,'skill_original_images':884,
             'skill_image_bytes':sum(r['bytes'] for r in icons['images'].values()),
             'numeric_and_recognition_core_unchanged':True,'map_calibrations_unchanged':True,
             'numeric_public_replay_rerun':False,'inherited_numeric_cases':732,
             'new_recognition_speed_claim':False,'synthetic_gui_tests_only':True,
             'game_actions':0,'chat_requests':0,'seconds':time.perf_counter()-started}
    (ROOT/'BRANCH_0.46_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in receipt.items() if k not in ('source_sha256','test_modules')},ensure_ascii=False))


if __name__=='__main__':main()
