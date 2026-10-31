from pathlib import Path
from copy import deepcopy
from hashlib import sha256
from unittest.mock import patch
import json,sys
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')]
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QPlainTextEdit
from rouge import player_acceptance
from rouge.catalog import catalog,operator_profiles
from player_ui_verification import run
out=R/'verification/maintenance/calculation-context-review-20261031/native';out.mkdir(exist_ok=False);images=[]
def check(section,w,gui,require):
    w.select_operator('mechanist');w.show_compact();bar=w.compact_window;bar.open_operators();gui.processEvents()
    panels=[getattr(w,n)for n in('offline_tools','paired_calibration','timing_calibration','bounded_calibration','calibration_experiment')]
    drafts={p:[v.toPlainText()for v in p.findChildren(QPlainTextEdit)]for p in panels}
    def image(widget,name):
        gui.processEvents();file=out/(name+'.png');assert widget.grab().save(str(file));images.append({'path':file.relative_to(R).as_posix(),'sha256':sha256(file.read_bytes()).hexdigest()})
    require(w.damage_result is not None and all(p._scenario==w.damage_result['scenario']for p in panels),'valid_main_result_propagated_to_five_current_importers')
    require(len(w._scenario_receivers)==8,'eight_existing_context_receivers_registered_after_creation')
    image(w,'player-valid-calculation')
    w.timing_scenario.setPlainText('{');gui.processEvents()
    require(w.damage_result is None and all(p._scenario is None for p in panels),'actual_text_signal_clears_all_current_importers')
    require('战斗时序情景'in w.damage_text.toPlainText(),'player_error_explains_invalid_timing_input')
    require(not w.paired_calibration.before_import_button.isEnabled()and not w.paired_calibration.after_import_button.isEnabled(),'paired_both_current_import_buttons_disabled')
    require(all(not p.import_button.isEnabled()for p in panels[2:]),'timing_bounded_experiment_imports_disabled')
    require(all([v.toPlainText()for v in p.findChildren(QPlainTextEdit)]==drafts[p]for p in panels),'manual_diagnostic_drafts_preserved_after_failed_current_input')
    image(w,'player-invalid-calculation')
    w.centralWidget().developer_tools=True;w.centralWidget().setCurrentWidget(w.paired_calibration);gui.processEvents()
    image(w.centralWidget().developer_dialog,'paired-current-import-unavailable')
    w.centralWidget().developer_dialog.hide();w.timing_scenario.clear();gui.processEvents()
    require(w.damage_result is not None and all(p._scenario==w.damage_result['scenario']for p in panels),'corrected_input_restores_only_fresh_current_scenario')
    require(w.paired_calibration.before_import_button.isEnabled(),'corrected_current_import_enabled')
    image(w,'player-calculation-restored')
    w.skill.blockSignals(True);w.skill.setCurrentIndex(-1);w.skill.blockSignals(False);w.calculate()
    require(w.damage_result is None and all(p._scenario is None for p in panels),'no_skill_exit_clears_current_imports')
    w.select_operator(next(i for i in operator_profiles()if i not in catalog()['operators']));w.calculate()
    require(w.damage_result is None and all(p._scenario is None for p in panels),'unimplemented_operator_exit_clears_current_imports')
    w.select_operator('mechanist');w.calculate();gui.processEvents();require(w.damage_result is not None,'final_valid_player_result_available')
    w.player_validation_target=w
with patch.object(player_acceptance,'check',check):code=run(999,out/'receipt.json')
(out/'images.json').write_text(json.dumps({'images':images,'isolated_public_preview_only':True,'new_independent_mechanics_calibration_claimed':False},ensure_ascii=False,indent=2)+'\n','utf8')
raise SystemExit(code)
