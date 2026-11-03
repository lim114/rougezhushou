"""An isolated, explicit collision preview; recompute only on user action."""
from copy import deepcopy
import json

from PySide6.QtWidgets import (QApplication, QDialog, QHBoxLayout, QLabel,
    QPlainTextEdit, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout)

from .charge_timeline import compare_charge_windows, format_charge_windows
from .manual_scenario import parse_preview_object


class ChargeTimelineDialog(QDialog):
    def __init__(self, scenario, duration, parent=None):
        super().__init__(parent)
        self.scenario = deepcopy(scenario)
        self.comparison_result = None
        self.setWindowTitle('机械师S3 · 冲锋时刻与观察窗口对照')
        self.resize(1050, 720)
        layout = QVBoxLayout(self)
        label = QLabel('使用打开时的培养、目标、藏品和时序条件。填写命中当前目标的冲锋时刻；不会自动生成碰撞时间。')
        label.setWordWrap(True); layout.addWidget(label)
        self.editor = QPlainTextEdit()
        self.editor.setMaximumHeight(100)
        self.editor.setPlainText(json.dumps({'hit_times_seconds': [],
            'windows_seconds': [min(3.5, duration), min(10, duration), duration]}, indent=2))
        self.editor.setToolTip('hit_times_seconds：最多100次冲锋命中，例如[1,3.5,3.5]；windows_seconds：最多12个观察窗口。单位为秒，0为开启；窗口不超过当前技能参数持续时间。')
        layout.addWidget(self.editor)
        actions = QHBoxLayout()
        self.calculate_button = QPushButton('计算窗口对照')
        self.copy_button = QPushButton('复制对照与计算条件'); self.copy_button.setEnabled(False)
        actions.addWidget(self.calculate_button); actions.addWidget(self.copy_button)
        layout.addLayout(actions)
        self.window_table = QTableWidget(0, 6)
        self.window_table.setHorizontalHeaderLabels(['观察窗口/秒', '窗口内冲锋次数',
            '轰击已计伤害', '声明冲锋伤害', '条件伤害小计', '已计部分每秒伤害'])
        self.event_table = QTableWidget(0, 3)
        self.event_table.setHorizontalHeaderLabels(['声明命中时刻/秒', '单次条件伤害', '冲锋累计条件伤害'])
        for table in (self.window_table, self.event_table):
            table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            layout.addWidget(table, 1)
        self.notice = QPlainTextEdit(); self.notice.setReadOnly(True)
        self.notice.setMaximumHeight(160); layout.addWidget(self.notice)
        self.editor.textChanged.connect(self.invalidate)
        self.calculate_button.clicked.connect(self.calculate)
        self.copy_button.clicked.connect(self.copy_result)
        self.calculate()

    def invalidate(self):
        self.comparison_result = None
        self.copy_button.setEnabled(False)
        self.window_table.setRowCount(0); self.event_table.setRowCount(0)
        self.notice.setPlainText('条件已修改，请计算窗口对照。')

    def calculate(self):
        self.invalidate()
        try:
            preview = parse_preview_object(self.editor.toPlainText(), '冲锋时刻对照')
            if set(preview) != {'hit_times_seconds', 'windows_seconds'}:
                raise ValueError('请提供hit_times_seconds与windows_seconds两项。')
            result = compare_charge_windows(self.scenario, preview['hit_times_seconds'], preview['windows_seconds'])
        except (ValueError, KeyError, TypeError) as error:
            self.notice.setPlainText(str(error)); return
        self.comparison_result = result
        self.window_table.setRowCount(len(result['windows']))
        self.event_table.setRowCount(len(result['events']))
        def fill(table, rows, fields):
            for i, row in enumerate(rows):
                for j, field in enumerate(fields):
                    value = row[field]
                    table.setItem(i, j, QTableWidgetItem('未知' if value is None else format(value, '.8g')))
            table.resizeColumnsToContents()
        fill(self.window_table, result['windows'], ('window_seconds', 'charge_hits', 'bombard_damage',
            'charge_damage', 'conditional_damage_subtotal', 'conditional_dps'))
        fill(self.event_table, result['events'], ('at_seconds', 'damage_reference', 'cumulative_charge_damage_reference'))
        training=result['training']
        summary=f"精英{training['elite']} / 等级{training['level']}；技能等级{self.scenario.get('skill_rank',10)}；每次冲锋条件伤害{result['per_hit_damage_reference']:.8g}。完整施放和周期总伤仍未知。"
        warnings=list(dict.fromkeys(w for row in result['windows'] for w in row['warnings']))
        if self.scenario.get('unconfirmed_training'):
            warnings.append('当前培养预览尚未确认：'+'、'.join(self.scenario['unconfirmed_training'])+'。')
        self.notice.setPlainText('\n'.join([summary,*result['notes'],*warnings]))
        self.copy_button.setEnabled(True)

    def copy_result(self):
        if self.comparison_result is not None:
            QApplication.clipboard().setText(format_charge_windows(self.comparison_result))
