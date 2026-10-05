"""Temporary Qt state only: finite speed, native fees and two-book counts."""
import os
os.environ['QT_QPA_PLATFORM']='offscreen'
import hashlib,json,sys,tempfile,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from verify_relic_ui_025 import OfflineWindow,module,QApplication,Qt
from rouge.reporting import format_report


def source_hashes():
    files=[*(ROOT/'rouge').rglob('*.py'),*(ROOT/'rouge/data').rglob('*.json'),
           Path(__file__),ROOT/'scripts/verify_relic_ui_025.py']
    return {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(set(files))}


def main():
    started=time.perf_counter();checks=[];before=source_hashes()
    with tempfile.TemporaryDirectory() as folder:
        p=Path(folder);module.RUN_STATE=p/'run.json';module.OPERATOR_STATE=p/'operators.json';module.SETTINGS=p/'settings.json'
        backend=module.DesktopBackend;module.DesktopBackend=lambda path,callback:backend(p/'chat',callback)
        app=QApplication([]);window=OfflineWindow()
        def select(op,skill,ids,context=None):
            window.select_operator(op);window.skill.setCurrentIndex(window.skill.findData(skill))
            window.relic_list.blockSignals(True)
            for i in range(window.relic_list.count()):
                item=window.relic_list.item(i)
                item.setCheckState(Qt.CheckState.Checked if item.data(Qt.ItemDataRole.UserRole) in ids else Qt.CheckState.Unchecked)
            window.relic_list.blockSignals(False)
            window.relic_context.setPlainText(json.dumps(context or {}));window.calculate()
            assert window.damage_result,window.damage_text.toPlainText()
            return window.damage_result['result'],window.damage_text.toPlainText()
        try:
            window.auto_relics.setChecked(False)
            assert window.windowTitle()=='黑流树海助手 0.61 · 识别与计算测试版'
            r,text=select('mechanist',3,{'rogue_6_relic_legacy_16'})
            assert abs(r['attack']-2720.8)<1e-7,r['attack']
            checks.append({'scope':'rune_before_skill_and_integer_writer','attack':r['attack']})
            r,text=select('kaltsit',2,{'rogue_6_relic_legacy_90','rogue_6_relic_legacy_14'})
            stats=r['estimate']['base_stats']
            assert stats['hp']==3975 and abs(stats['defense']-573.75)<1e-7,stats
            checks.append({'scope':'hp_defense_rune_before_talent','hp':stats['hp'],'defense':stats['defense']})
            for ids,cost in (({'rogue_6_relic_fight_11'},12),({'rogue_6_relic_book_3'},5),
                ({'rogue_6_relic_fight_11','rogue_6_relic_book_3'},3)):
                r,text=select('mechanist',3,ids)
                assert r['deployment_cost']==cost,(ids,r.get('deployment_reference'))
                assert not any('实际部署扣费' in m['label'] for s in r['report']['sections'] for m in s['metrics'])
                assert '实际部署扣费：未知' not in text
                checks.append({'scope':'fee','items':sorted(ids),'cost':cost})
            for ids,bonus in (({'rogue_6_relic_legacy_105'},40),({'rogue_6_relic_legacy_106'},70),
                ({'rogue_6_relic_legacy_105','rogue_6_relic_legacy_106'},110)):
                r,text=select('mechanist',1,ids)
                ref=r['deployment_buff_reference']
                assert sum(s['attack_speed_addition'] for s in ref['spans'])==bonus
                assert r['estimate']['base_stats']['attack_speed']==ref['permanent_attack_speed']+bonus
                assert '部署限时攻速' in text
                assert ref['live_state_verified'] is False
                checks.append({'scope':'finite_speed','bonus':bonus})
            r,text=select('char_1041_angel2',3,{'rogue_6_relic_legacy_139','rogue_6_relic_legacy_140'})
            assert r['estimate']['skill']['hit_counts']['技能攻击']==95
            assert r['ammo_refill_reference']['count_order_invariant']
            assert not r['ammo_refill_reference']['order_verified']
            proof=r['relic_resolution']['rules'][0]['ammo_parameters']['native_parameter_proof_sha256']
            assert proof not in text and proof in format_report(r,technical=True)
            checks.append({'scope':'two_books','full_cast_hits':95})
            r,text=select('mechanist',1,set())
            assert '部署限时攻速' not in text and '藏品补弹参考' not in text
            checks.append({'scope':'absent_sections'})
            bed='rogue_6_relic_cargo_3'
            for ids,context,expected in (({bed},{'empty_slots':4},17),
                ({bed,'rogue_6_relic_fight_11'},{'empty_slots':4},6),
                ({bed,'rogue_6_relic_book_3'},{'empty_slots':4},0),
                ({bed,'rogue_6_relic_fight_11','rogue_6_relic_book_3'},{'empty_slots':4},0),
                ({bed,'rogue_6_relic_fight_11'},{'empty_slots':3},12),
                ({bed},{},None),
                ({bed,'rogue_6_relic_fight_11'},{},None)):
                r,text=select('mechanist',3,ids,context)
                assert r['deployment_cost']==expected,(ids,context,r['deployment_cost'])
                assert r['deployment_reference']['cost']['actual_cost'] is None
                if expected is None:assert '未知' in text
                checks.append({'scope':'empty_bed_offline_cost','items':sorted(ids),
                    'condition':context,'expected_cost':expected,'actual_deployment_asserted':False})
            r,text=select('mechanist',3,{'rogue_6_relic_fight_22'})
            for name in ('凋亡','灼燃','神经','侵蚀'):
                assert '河谷祭祈 · '+name+'机制资料' in text
            assert '实际追加跳数与完整总伤仍未知' in text
            checks.append({'scope':'held_river_four_element_reference','actual_extra_damage_added':False})
            r,text=select('mechanist',3,set())
            assert '河谷祭祈' not in text
            checks.append({'scope':'unheld_river_reference_absent'})
            assert not window.auto.isChecked() and window.capture.target is None and not window.desktop.process
            assert window.run.state['history']==[] and window.run.state['config']=={}
            after=source_hashes()
            changed=[n for n in sorted(set(before)|set(after)) if before.get(n)!=after.get(n)]
            assert not changed,changed
            receipt={'version':'0.61.0','passed':True,'checks':checks,'game_actions':0,'chat_requests':0,
                'private_data_isolated':True,'elapsed_seconds':time.perf_counter()-started,
                'source_sha256':before,'source_sha256_after':after,'source_drift':changed,'runner_sealed':True}
            with (ROOT/'NATIVE_UI_0.61_VERIFICATION.json').open('x',encoding='utf-8') as stream:
                json.dump(receipt,stream,ensure_ascii=False,indent=2)
            print(json.dumps({'passed':True,'checks':len(checks),'elapsed_seconds':receipt['elapsed_seconds']}),flush=True)
        finally:window.close();app.processEvents()


if __name__=='__main__':main()
