"""Loss-persistent uncertainty, with isolated run memory and public calculation.

Pinned PRTS item-catalog revision 433329 establishes retained friendly growth
on loss; it does not establish its accumulated amount or reacquisition order.
These observations test memory boundaries, not an invented growth counter.
"""
import copy
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import tempfile
import unittest
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch

from rouge.damage import calculate_damage
from rouge.run_state import RunState
from rouge.reporting import format_report
import rouge.app as app_module

HYDRA='rogue_6_start_4'


def observation(ids):
    return {'relics':{'ids':ids,'icons':[{'id':rid,'candidates':[rid],
        'confirmed':True,'source':'held_icon','score':.99} for rid in ids],
        'count':len(ids),'source':'held_bar'}}


def scenario(run):
    return {'operator':'mechanist','skill':3,'timing_mode':'continuous','relic_ids':run.held_relic_ids(),
        'inventory_status':run.inventory_status(),
        'relic_history_context':run.relic_history_context(),
        'run_config':{'difficulty':{'value':0,'source':'explicit_test'}},
        'target_enemy':{'stage_id':'ro6_n_1_2','enemy_id':'enemy_2137_shsdgo','level':0}}


class HydraHistory060Tests(unittest.TestCase):
    def test_complete_loss_reload_keeps_unknown_without_current_item_or_enemy_penalty(self):
        with tempfile.TemporaryDirectory() as folder:
            file=Path(folder)/'run.json';run=RunState(file);start=run.state['started_at']
            self.assertTrue(run.apply(observation([HYDRA]),start+1))
            self.assertTrue(run.apply(observation([]),start+2))
            restored=RunState(file)
            self.assertEqual(restored.held_relic_ids(),[])
            self.assertTrue(restored.inventory_status()['complete'])
            context=restored.relic_history_context()
            record=context['persistent_growth_unknowns'][0]
            self.assertEqual(record['id'],HYDRA)
            self.assertIs(record['currently_held'],False)
            self.assertIsNone(record['attack_pct']);self.assertIsNone(record['hp_pct'])
            args=scenario(restored);result=calculate_damage(args)
            reference=copy.deepcopy(result)
            self.assertTrue(reference['estimate']['complete'])
            app_module.apply_relic_history_notice(args,result)
            self.assertFalse(result['estimate']['complete'])
            self.assertFalse(result['relic_resolution']['complete'])
            self.assertEqual(result['estimate']['base_stats'],reference['estimate']['base_stats'])
            self.assertEqual(result['run_resolution']['enemy'],reference['run_resolution']['enemy'])
            self.assertEqual(result['total_damage'],reference['total_damage'])
            self.assertNotIn(HYDRA,[r['id'] for r in result['relic_resolution']['records']])
            text=format_report(result)
            self.assertIn('计算状态：不完整',text)
            self.assertIn('襁褓九头蛇',text)
            self.assertIn('攻击与生命',text)
            self.assertIn('未包含',text)

    def test_current_possession_keeps_verified_enemy_factors_and_partial_is_not_loss(self):
        with tempfile.TemporaryDirectory() as folder:
            run=RunState(Path(folder)/'run.json');start=run.state['started_at']
            run.apply(observation([HYDRA]),start+1)
            run.apply({'relics':{'ids':[],'icons':[],'count':None,'source':'unread'}},start+2)
            self.assertEqual(run.held_relic_ids(),[HYDRA])
            self.assertIs(run.relic_history_context()['persistent_growth_unknowns'][0]['currently_held'],True)
            args=scenario(run);actual=calculate_damage(args)
            plain=calculate_damage({**args,'relic_ids':[]})
            for key in ('atk','maxHp'):
                self.assertAlmostEqual(actual['run_resolution']['enemy']['stats'][key],
                    plain['run_resolution']['enemy']['stats'][key]*1.3)
            reference=copy.deepcopy(actual)
            app_module.apply_relic_history_notice(args,actual)
            self.assertEqual(actual['run_resolution']['enemy'],reference['run_resolution']['enemy'])
            self.assertEqual(actual['estimate']['base_stats'],reference['estimate']['base_stats'])
            self.assertIsNone(actual['relic_history_context']['persistent_growth_unknowns'][0]['attack_pct'])

    def test_same_run_reacquisition_retains_unknown_without_deriving_a_growth_count(self):
        with tempfile.TemporaryDirectory() as folder:
            run=RunState(Path(folder)/'run.json');start=run.state['started_at']
            for offset,ids in ((1,[HYDRA]),(2,[]),(3,[HYDRA])):
                self.assertTrue(run.apply(observation(ids),start+offset))
            before=copy.deepcopy(run.state);context=run.relic_history_context()
            record=context['persistent_growth_unknowns'][0]
            self.assertEqual(record['first_confirmed_at'],start+1)
            self.assertEqual(record['last_confirmed_at'],start+3)
            self.assertEqual(record['last_loss_confirmed_at'],start+2)
            self.assertIs(record['currently_held'],True)
            self.assertIsNone(record['attack_pct']);self.assertIsNone(record['hp_pct'])
            self.assertFalse(any('count' in key or 'stack' in key for key in record))
            context['persistent_growth_unknowns'].clear()
            self.assertEqual(run.state,before)
            self.assertEqual(len(run.relic_history_context()['persistent_growth_unknowns']),1)

    def test_manual_preview_cross_run_and_manual_new_run_do_not_inherit_uncertainty(self):
        with tempfile.TemporaryDirectory() as folder:
            file=Path(folder)/'run.json';run=RunState(file);start=run.state['started_at']
            run.apply(observation([HYDRA]),start+1);run.apply(observation([]),start+2)
            args=scenario(run)
            for replacement in ({'source':'manual_test','complete':True},
                                {**run.inventory_status(),'run_id':'another-run'}):
                altered={**args,'inventory_status':replacement};result=calculate_damage(altered)
                reference=copy.deepcopy(result)
                app_module.apply_relic_history_notice(altered,result)
                self.assertEqual(result,reference)
            old_id=run.state['id'];run.reset()
            self.assertNotEqual(run.state['id'],old_id)
            self.assertEqual(run.relic_history_context()['persistent_growth_unknowns'],[])
            restored=RunState(file)
            self.assertEqual(restored.relic_history_context()['persistent_growth_unknowns'],[])
            # A fresh run still needs a fresh complete inventory observation.
            restored.apply(observation([]),restored.state['started_at']+1)
            args=scenario(restored);actual=calculate_damage(args);reference=copy.deepcopy(actual)
            app_module.apply_relic_history_notice(args,actual)
            self.assertEqual(actual,reference)
            self.assertTrue(actual['estimate']['complete'])

    def test_old_missing_or_invalid_confirmation_history_does_not_invent_a_source(self):
        with tempfile.TemporaryDirectory() as folder:
            run=RunState(Path(folder)/'run.json');start=run.state['started_at']
            run.apply(observation([HYDRA]),start+1)
            for events in ([],[{'kind':'relic_confirmed','id':HYDRA,'at':start-1}],
                           [{'kind':'relic_confirmed','id':HYDRA,'at':float('nan')}],
                           [{'kind':'relic_confirmed','id':HYDRA,'at':start+2}]):
                run.state['history']=events
                self.assertEqual(run.relic_history_context()['persistent_growth_unknowns'],[])

    def test_notice_is_idempotent_and_keeps_raw_unknown_as_null(self):
        with tempfile.TemporaryDirectory() as folder:
            run=RunState(Path(folder)/'run.json');start=run.state['started_at']
            run.apply(observation([HYDRA]),start+1);run.apply(observation([]),start+2)
            args=scenario(run);actual=calculate_damage(args)
            app_module.apply_relic_history_notice(args,actual);once=copy.deepcopy(actual)
            app_module.apply_relic_history_notice(args,actual)
            self.assertEqual(actual,once)
            actual['relic_history_context']['persistent_growth_unknowns'][0]['attack_pct']=99
            self.assertIsNone(run.relic_history_context()['persistent_growth_unknowns'][0]['attack_pct'])


class HydraApp060Tests(unittest.TestCase):
    def test_real_qt_auto_history_notice_and_manual_preview_isolation(self):
        from PySide6.QtWidgets import QApplication
        app=QApplication.instance() or QApplication([])
        with ExitStack() as stack:
            folder=Path(stack.enter_context(tempfile.TemporaryDirectory()))
            for key,name in (('RUN_STATE','run.json'),('OPERATOR_STATE','operators.json'),('SETTINGS','settings.json')):
                stack.enter_context(patch.object(app_module,key,folder/name))
            backend=app_module.DesktopBackend
            stack.enter_context(patch.object(app_module,'DesktopBackend',
                lambda _path,callback:backend(folder/'chat',callback)))
            class IsolatedWindow(app_module.MainWindow):
                def refresh_windows(self):self.windows.clear()
            window=IsolatedWindow()
            try:
                start=window.run.state['started_at']
                window.run.apply(observation([HYDRA]),start+1)
                window.run.apply(observation([]),start+2)
                window.select_operator('mechanist')
                window.skill.setCurrentIndex(window.skill.findData(3))
                window.frame_timing.setChecked(False)
                window.sync_run_relics();window.auto_relics.setChecked(True);window.calculate()
                app.processEvents()
                self.assertIsNotNone(window.damage_result,window.damage_text.toPlainText())
                self.assertFalse(window.damage_result['result']['estimate']['complete'])
                self.assertFalse(window.damage_result['result']['relic_resolution']['complete'])
                self.assertIn('计算状态：不完整',window.damage_text.toPlainText())
                self.assertIn('襁褓九头蛇',window.damage_text.toPlainText())
                self.assertEqual(window.damage_result['scenario']['relic_ids'],[])
                self.assertEqual(window.damage_result['scenario']['relic_history_context']['run_id'],window.run.state['id'])
                window.auto_relics.setChecked(False);window.calculate();app.processEvents()
                self.assertNotIn('relic_history_context',window.damage_result['scenario'])
                self.assertNotIn('relic_history_context',window.damage_result['result'])
                self.assertNotIn('襁褓九头蛇',window.damage_text.toPlainText())
                self.assertFalse(window.auto.isChecked());self.assertIsNone(window.capture.target)
                self.assertIsNone(window.desktop.process)
                self.assertFalse((folder/'chat').exists())
                self.assertFalse((folder/'settings.json').exists())
            finally:
                window.close();app.processEvents()


if __name__=='__main__':unittest.main()
