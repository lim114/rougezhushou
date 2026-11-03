import sys, os, json, tempfile, copy
from pathlib import Path
ROOT = Path(__file__).resolve().parents[4]; sys.path.insert(0, str(ROOT))
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFontDatabase, QFont
from rouge import app as product
app = QApplication.instance() or QApplication([])
font = QFontDatabase.addApplicationFont(os.environ['ROUGE_TEST_CJK_FONT'])
app.setFont(QFont(QFontDatabase.applicationFontFamilies(font)[0], 10))
cases = []
with tempfile.TemporaryDirectory() as directory:
    base = Path(directory)
    product.RUN_STATE = base/'run.json'; product.OPERATOR_STATE = base/'operator.json'; product.SETTINGS = base/'settings.json'
    window = product.MainWindow(); window.show(); app.processEvents()
    try:
        original = copy.deepcopy((window.run.state, window.operator_observations, window.damage_result))
        panel = window.technology_reference; view = panel.squad_plan
        window.centralWidget().setCurrentIndex(5); panel.reference_tabs.setCurrentIndex(1); app.processEvents()
        assert view.table.rowCount() == 7 and not panel.account_state.path.exists()
        cases.append('actual main tab opens seven pinned conditions without a write')
        node = 'rogue_6_difficulty_3'
        panel.account_state.set_status(node, 'unlocked'); panel.populate(); view.grade.setCurrentIndex(9)
        row = next(i for i,r in enumerate(view.rows) if r['squad_id'] == 'rogue_6_band_7')
        view.table.selectRow(row); view.jump_button.click(); app.processEvents()
        assert panel.nodes.currentData() == node and panel.reference_tabs.currentIndex() == 0
        assert view.rows[row]['manual_status'] == 'unlocked' and view.rows[row]['actual_activation'] is None
        cases.append('manual reference and grade update; jump selects exact technology without activation')
        panel.new_profile_name.setText('公开另一档案'); panel.create_profile_button.click(); app.processEvents()
        assert all(r['manual_status'] == 'unknown' for r in view.rows)
        view.search.setText('特勤'); assert view.table.rowCount() == 1
        view.table.selectRow(0); assert not view.jump_button.isEnabled()
        view.search.setText('不存在'); assert view.table.rowCount() == 0 and not view.jump_button.isEnabled()
        view.search.clear(); panel.profiles.setCurrentIndex(panel.profiles.findData('default')); app.processEvents()
        view.copy_button.click(); assert '已解锁' in app.clipboard().text() and '实际激活仍未知' in app.clipboard().text()
        cases.append('profile isolation, filter boundaries and full copy')
        assert (window.run.state, window.operator_observations, window.damage_result) == original
        assert not window.auto.isChecked() and window.capture.target is None and window.desktop.process is None
        panel.reference_tabs.setCurrentIndex(1); app.processEvents()
        cases.append('run/account/calculation unchanged and capture/chat off')
    finally:
        window.close(); app.processEvents()
(Path(__file__).parent/'window.json').write_text(json.dumps({'passed':True,'cases':cases,'native_windows_game_chat_verified':False},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'passed': True, 'cases': len(cases)}))
