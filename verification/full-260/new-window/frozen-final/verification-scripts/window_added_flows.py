"""246/248–251/253/255–257 actual MainWindow workflows; no game activity."""
from copy import deepcopy
import json
import time


def run_added_flows(window, qt, mark, save_result, out):
    tabs = window.centralWidget()
    def show(panel):
        tabs.setCurrentWidget(panel); qt.processEvents()
        assert tabs.currentWidget() is panel and panel.isVisible()
    def choose(combo, value):
        index = combo.findData(value); assert index >= 0, value
        combo.setCurrentIndex(index)
    def worker(panel):
        emitted = []
        panel.resultChanged.connect(emitted.append)
        before = panel.editor.toPlainText()
        panel.run_button.click(); deadline = time.monotonic() + 30
        while panel._workers and time.monotonic() < deadline:
            qt.processEvents(); time.sleep(.01)
        qt.processEvents()
        assert not panel._workers, panel.status.text()
        assert panel.result_snapshot() is not None, panel.status.text()
        assert emitted and emitted[-1] == panel.result_snapshot()
        assert panel.editor.toPlainText() == before
        return panel.result_snapshot()

    panel = window.resident_route_review; show(panel)
    choose(panel.preset, 'victory'); panel.load_example.click()
    payload = json.loads(panel.editor.toPlainText()); payload['resident_post_victories'] = {}
    panel.editor.setPlainText(json.dumps(payload, ensure_ascii=False))
    assert panel.declare_victory.isEnabled()
    panel.declare_victory.click()
    assert json.loads(panel.editor.toPlainText())['resident_post_victories'] == {'post': [1]}
    result = worker(panel)
    assert result['routes'][0]['conditional_post_eviction_steps'] == [1]
    save_result('246-victory', result)
    choose(panel.preset, 'conservative'); panel.load_example.click(); result = worker(panel)
    assert result['policy_excluded_route_ids'] == ['a-route']
    assert '实际安全、失败概率' in panel.result_view.toPlainText()
    save_result(246, result); mark(246, 'actual resident tab, explicit victory and candidate-policy signals/results')

    panel = window.relic_order_precision; show(panel)
    ready = []; panel.resultReady.connect(ready.append)
    choose(panel.template, 'magic'); panel.load_template.click(); panel.calculate_button.click()
    assert panel.result_snapshot()['accepted_order_count'] == 6
    assert panel.result_snapshot()['source_available'] is True
    before = panel.editor.toPlainText(); panel.order_selector.setCurrentIndex(4)
    assert panel.editor.toPlainText() == before
    assert panel.result_snapshot()['declared_processing_order'] is None
    chosen = panel.order_selector.currentData(); panel.declare_viewed_order.click()
    assert json.loads(panel.editor.toPlainText())['declared_processing_order'] == chosen
    assert panel.result_snapshot() is None
    panel.calculate_button.click(); result = panel.result_snapshot()
    assert result['declared_order_trace']['order'] == chosen and len(ready) == 2
    assert '0x' in panel.order_detail.toPlainText()
    save_result(248, result); mark(248, 'actual precision tab, inspect order and explicitly declare source-supported trace')

    for owner in ('char_2023_ling', 'char_248_mgllan'):
        window.select_operator(owner); window.skill.setCurrentIndex(window.skill.findData(3))
        window.level.setValue(90); qt.processEvents()
        assert not window.supplemental_token_module_button.isHidden()
        window.supplemental_token_module_button.click(); qt.processEvents()
        dialog = window.supplemental_token_module_dialog
        assert dialog.isVisible() and dialog.operator == owner
        assert dialog.phase.currentData() is None and dialog.endpoint.currentData() is None
        choose(dialog.phase, 2); choose(dialog.endpoint, 'last'); dialog.calculate_button.click()
        result = deepcopy(dialog.result); assert result is not None
        assert len(result['variants']) == 3
        assert dialog.table.rowCount() == len(result['variants']) * 4
        assert '当前完整实体面板' in dialog.details.toPlainText()
        captured = deepcopy(dialog.training)
        window.select_operator('mechanist'); window.calculate(); qt.processEvents()
        assert dialog.training == captured and dialog.result == result
        choose(dialog.endpoint, 'first'); assert dialog.result is None
        dialog.calculate_button.click()
        assert all(row['token_level_endpoint'] == 1 for row in dialog.result['variants'])
        save_result('249-' + owner, dialog.result); dialog.close()
    mark(249, 'actual owner buttons open both token module dialogs; endpoints and captured training remain independent')

    panel = window.bounded_calibration; show(panel)
    ready = []; panel.resultReady.connect(ready.append)
    choose(panel.template, 'mechanist'); panel.load_template.click(); panel.run_button.click()
    assert panel.result_snapshot() is not None, panel.status.text()
    assert '所有可行值均相符' in panel.result_view.toPlainText()
    assert '调用方声明正常链录入协议' in panel.result_view.toPlainText()
    payload = json.loads(panel.panel_editor.toPlainText())
    bounds = payload['after']['observation']['values']['hp']
    payload['after']['observation']['values']['hp'] = [bounds[0] - 1, bounds[1] + 1]
    panel.panel_editor.setPlainText(json.dumps(payload, ensure_ascii=False))
    panel.run_button.click(); result = panel.result_snapshot()
    assert result is not None and len(ready) == 2
    assert '仅可能重叠' in panel.result_view.toPlainText()
    assert json.loads(panel.panel_editor.toPlainText()) == payload
    save_result(250, result); mark(250, 'actual bounded tab, explicit bounds produce possible overlap without automatic uncertainty')

    panel = window.route_resource_ledger; show(panel)
    choose(panel.preset, 'grants'); panel.load_example.click(); result = worker(panel)
    assert result['routes'][0]['known_source_grant_subtotal']['hope'] == 7
    assert '希望授予 7' in panel.result_view.toPlainText()
    save_result(251, result); mark(251, 'actual resource ledger tab and independent documented grants/terminal signal')

    panel = window.route_scenarios; show(panel)
    choose(panel.preset, 'compound'); panel.load_example.click(); result = worker(panel)
    assert len(result['cases']) == 7
    assert all(row['closed_quantity_envelope'] is None for row in result['route_summaries'])
    original = json.loads(panel.editor.toPlainText())
    choose(panel.scenario_select, 'ap2'); panel.scenario_ap.setText('未知'); panel.set_scenario_ap.click()
    changed = json.loads(panel.editor.toPlainText())
    assert changed['scenarios'][1]['action_points'] is None
    assert changed['scenarios'][0] == original['scenarios'][0]
    result = worker(panel)
    assert result['cases'][1]['scenario_input']['action_points'] is None
    assert '实际最优路线、完整收益和情景概率：未知' in panel.result_view.toPlainText()
    save_result(253, result); mark(253, 'actual scenario tab changes only selected declaration; unknown is retained and no complete envelope invented')

    panel = window.calibration_experiment; show(panel)
    ready = []; panel.resultReady.connect(ready.append)
    choose(panel.operator, 'mechanist'); choose(panel.channel, 'panel'); choose(panel.variant, 'compatible')
    panel.load_template.click(); panel.run_button.click(); result = panel.result_snapshot()
    assert result is not None and result['training_hypothesis_range']['lower'] == 5
    assert result['overall_state'] == 'compatible_on_declared_ranges'
    assert result['native_verified'] is False and result['engine_correction'] is None
    save_result('255-compatible', result)
    choose(panel.variant, 'held_out_conflict'); panel.load_template.click(); panel.run_button.click()
    result = panel.result_snapshot()
    assert result['overall_state'] == 'contradicted' and result['training_state'] == 'compatible'
    assert result['held_out_checks'][0]['state'] == 'no_overlap'
    witness = panel.witness_choice.currentData(); panel.locate_witness_button.click()
    assert panel.record_choice.currentData() == witness
    assert json.loads(panel.record_editor.toPlainText())['id'] == witness
    assert panel.tabs.currentIndex() == 1 and len(ready) == 2
    save_result(255, result); assert window.grab().save(str(out / 'main-experiment.png'))
    mark(255, 'actual experiment tab and result signal, independent held-out contradiction witness locator')

    panel = window.recipient_native_ratio; show(panel)
    ready = []; panel.resultReady.connect(ready.append)
    choose(panel.operator, 'char_196_sunbr'); panel.load_template.click()
    panel.label.setText('独立主窗口整数参考'); panel.hp.setText('50000'); panel.maximum.setText('100000')
    panel.evidence_source.setText('公开字面量整数算术，非游戏采集')
    panel.post_known.setChecked(False); panel.append_observation.click(); panel.calculate_button.click()
    result = panel.result_snapshot(); assert result is not None
    assert result['rows'][-1]['conditional_direct_healing_factor_from_declared_post_ratio'] is None
    panel.label.setText('独立主窗口后置比例参考')
    panel.post_known.setChecked(True); panel.post_raw.setText(str((1 << 32) // 2 - 42951))
    panel.append_observation.click(); panel.calculate_button.click(); result = panel.result_snapshot()
    assert result['rows'][-1]['conditional_direct_healing_factor_from_declared_post_ratio'] == 1.15
    assert len(result['rows']) == 5 and len(ready) == 2
    assert '实际get_hpRatio' in panel.result_view.toPlainText()
    save_result(256, result); mark(256, 'actual HP original-value tab preserves unknown post-value then evaluates explicitly declared strict threshold')

    panel = window.route_continuation; show(panel)
    choose(panel.preset, 'fresh'); panel.load_example.click(); result = worker(panel)
    assert '差值：-1' in panel.result_view.toPlainText()
    save_result('257-fresh', result)
    choose(panel.preset, 'edge'); panel.load_example.click(); result = worker(panel)
    assert '这一条步行连线' in panel.result_view.toPlainText()
    assert result['alternatives']['plans']
    assert '实际目标完成、收益和最优路线：未知' in panel.result_view.toPlainText()
    save_result(257, result); mark(257, 'actual continuation tab diagnoses changed edge and lists bounded replacement plans')


def check_global_preservation(window, qt, mark):
    names = ('resident_route_review', 'route_resource_ledger', 'route_scenarios', 'route_continuation',
             'calibration_experiment', 'relic_order_precision', 'recipient_native_ratio', 'inventory_capacity')
    before = {name: (getattr(window, name).editor.toPlainText(), getattr(window, name).result_snapshot()) for name in names}
    bounded = window.bounded_calibration
    interval_before = (bounded.panel_editor.toPlainText(), bounded.timing_editor.toPlainText(), bounded.result_snapshot())
    experiment_record_before = window.calibration_experiment.record_editor.toPlainText()
    window.select_operator('mechanist'); window.calculate(); window.render_map(); qt.processEvents()
    after = {name: (getattr(window, name).editor.toPlainText(), getattr(window, name).result_snapshot()) for name in names}
    assert before == after
    assert interval_before == (bounded.panel_editor.toPlainText(), bounded.timing_editor.toPlainText(), bounded.result_snapshot())
    assert experiment_record_before == window.calibration_experiment.record_editor.toPlainText()
    mark('246–260', 'actual calculator/map refresh preserves independent editor inputs, record draft and existing results')
