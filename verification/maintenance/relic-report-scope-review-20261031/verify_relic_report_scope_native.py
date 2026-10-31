from pathlib import Path
from copy import deepcopy
from hashlib import sha256
from unittest.mock import patch
import json,sys
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')]
from PySide6.QtCore import Qt
from rouge import player_acceptance,damage
from player_ui_verification import run
out=R/'verification/maintenance/relic-report-scope-review-20261031/native-final'
out.mkdir(exist_ok=False);images=[]

def check(section,w,gui,require):
    w.select_operator('mechanist');w.centralWidget().show_group('干员计算')
    w.skill.setCurrentIndex(w.skill.findData(3));w.auto_relics.setChecked(False)
    for i in range(w.relic_list.count()):
        item=w.relic_list.item(i)
        item.setCheckState(Qt.CheckState.Checked if item.data(Qt.ItemDataRole.UserRole)=='rogue_6_relic_legacy_60' else Qt.CheckState.Unchecked)
    w.relic_filter.setText('金酒之杯')
    w.resize(1250,1000);gui.processEvents()
    require(w.damage_text.isVisible(),'actual_calculation_report_visible')
    require(w.damage_text.isReadOnly(),'report_stays_read_only')
    scenario={'operator':'mechanist','skill':3,'relic_ids':['rogue_6_relic_legacy_60']}
    def show(context):
        w.relic_context.setPlainText(json.dumps(context));w.calculate();gui.processEvents()
        require(w.damage_result is not None,'actual_controls_produce_calculation')
        require(w.damage_result['scenario']['skill']==3,'actual_skill_control_matches_report')
        require(w.damage_result['scenario']['relic_ids']==scenario['relic_ids'],'actual_relic_control_matches_report')
        return w.damage_result['result']
    def image(name):
        p=out/(name+'.png');assert w.damage_text.grab().save(str(p))
        images.append({'path':p.relative_to(R).as_posix(),'sha256':sha256(p.read_bytes()).hexdigest()})
    value=show({});original=deepcopy(value)
    require('完整结果未知' in w.damage_text.toPlainText(),'default_view_warns_before_attributes')
    require(w.damage_text.toPlainText().index('完整结果未知')<w.damage_text.toPlainText().index('生命值：'),'warning_precedes_numeric_panel')
    w.damage_text.verticalScrollBar().setValue(0);gui.processEvents();image('missing-gold-top')
    require('已计效果参考' in w.damage_text.toPlainText(),'default_view_qualifies_output')
    w.damage_text.find('包含全部所选藏品的完整结果');gui.processEvents();image('missing-gold-coverage')
    bar=w.damage_text.verticalScrollBar();bar.setValue(min(12,bar.maximum()));gui.processEvents();position=bar.value()
    require(position>0,'actual_nonzero_reading_position')
    w.render_damage();gui.processEvents()
    require(bar.value()==position,'same_report_refresh_preserves_reading')
    w.damage_technical.setChecked(True);gui.processEvents()
    require('完整结果未知' in w.damage_text.toPlainText(),'technical_view_keeps_scope')
    w.raw_damage.setChecked(True);gui.processEvents()
    require('confirmed_effects_reference' in w.damage_text.toPlainText(),'structured_view_keeps_scope_metadata')
    require('"complete_result": null' in w.damage_text.toPlainText(),'structured_full_result_is_unknown')
    w.raw_damage.setChecked(False);w.damage_technical.setChecked(False)
    require(value==original,'view_toggles_do_not_mutate_calculation')
    show({'gold':25});w.damage_text.verticalScrollBar().setValue(0);gui.processEvents();image('confirmed-gold-top')
    require('藏品尚未计全' not in w.damage_text.toPlainText(),'confirmed_context_clears_obsolete_warning')
    require('【预计属性】' in w.damage_text.toPlainText(),'confirmed_context_restores_existing_panel')
    require('攻速：135' in w.damage_text.toPlainText(),'confirmed_gold_retains_source_based_value')
    show({});require('完整结果未知' in w.damage_text.toPlainText(),'unknown_refresh_does_not_reuse_old_gold')
    w.player_validation_target=w

with patch.object(player_acceptance,'check',check):code=run(999,out/'receipt.json')
data=json.loads((out/'receipt.json').read_bytes());data['report_images']=images
(out/'report-images.json').write_text(json.dumps({'images':images,'not_game_samples':True},ensure_ascii=False,indent=2)+'\n','utf8')
raise SystemExit(code)
