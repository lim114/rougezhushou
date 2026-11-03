import json
from copy import deepcopy
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QApplication,QComboBox,QDialog,QHBoxLayout,QLabel,QLineEdit,
    QListWidget,QListWidgetItem,QPlainTextEdit,QPushButton,QTableWidget,QTableWidgetItem,QVBoxLayout)
from .catalog import catalog,stage_previews
from .enemy_comparison import compare_enemies,format_enemy_comparison
from .manual_scenario import parse_preview_object


class EnemyComparisonDialog(QDialog):
    def __init__(self,scenario,parent=None):
        super().__init__(parent);self.scenario=deepcopy(scenario);self.result=None
        self.setWindowTitle('固定关卡敌人 · 难度对照');self.resize(1150,760)
        layout=QVBoxLayout(self)
        label=QLabel('选择固定关卡候选及最多6个保密等级。其他条件沿用打开时情景；敌人候选不保证出场，未核验脚本逐行保留。')
        label.setWordWrap(True);layout.addWidget(label)
        actions=QHBoxLayout();self.stage=QComboBox()
        for sid,stage in catalog()['stages'].items():
            if sid in stage_previews():self.stage.addItem(stage['name']+' · '+stage['difficulty'],sid)
        selected=(scenario.get('target_enemy') or {}).get('stage_id');index=self.stage.findData(selected)
        if index>=0:self.stage.setCurrentIndex(index)
        actions.addWidget(self.stage,1);actions.addWidget(QLabel('保密等级列表'))
        self.grades=QLineEdit('[0,5,11]');actions.addWidget(self.grades)
        self.orb_mode=QComboBox()
        for label,key in [('源阶方：未知模式','unknown'),('源阶方：行动同列','active_same_column'),('源阶方：行动异列','active_other_column')]:self.orb_mode.addItem(label,key)
        actions.addWidget(self.orb_mode);layout.addLayout(actions)
        self.enemies=QListWidget();self.enemies.setMaximumHeight(150);layout.addWidget(self.enemies)
        buttons=QHBoxLayout();self.calculate_button=QPushButton('计算目标对照');self.copy_button=QPushButton('复制对照与条件')
        buttons.addWidget(self.calculate_button);buttons.addWidget(self.copy_button);layout.addLayout(buttons)
        self.fields=('enemy_name','grade','status','max_hp','attack','defense','resistance','window_damage','window_healing')
        self.table=QTableWidget(0,len(self.fields));self.table.setHorizontalHeaderLabels(['敌人','保密等级','状态','生命参考','攻击参考','防御参考','法抗参考','窗口伤害','窗口治疗'])
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers);layout.addWidget(self.table,1)
        self.notice=QPlainTextEdit();self.notice.setReadOnly(True);layout.addWidget(self.notice,1)
        self.stage.currentIndexChanged.connect(self.populate);self.grades.textChanged.connect(self.invalidate)
        self.orb_mode.currentIndexChanged.connect(self.invalidate);self.enemies.itemChanged.connect(self.invalidate)
        self.calculate_button.clicked.connect(self.calculate)
        self.copy_button.clicked.connect(lambda:QApplication.clipboard().setText(format_enemy_comparison(self.result)) if self.result else None)
        self.populate();self.calculate()

    def populate(self,*_args):
        self.enemies.blockSignals(True);self.enemies.clear()
        original=self.scenario.get('target_enemy') or {}
        for index,record in enumerate(stage_previews()[self.stage.currentData()]['possible_enemies']):
            item=QListWidgetItem(record['name']+f" · 引用等级{record['level']}")
            item.setData(Qt.ItemDataRole.UserRole,{'enemy_id':record['id'],'level':record['level']})
            checked=original.get('stage_id')==self.stage.currentData() and original.get('enemy_id')==record['id'] and original.get('level')==record['level']
            item.setCheckState(Qt.CheckState.Checked if checked or (not original and index==0) else Qt.CheckState.Unchecked)
            self.enemies.addItem(item)
        self.enemies.blockSignals(False);self.invalidate()

    def invalidate(self,*_args):
        self.result=None;self.table.setRowCount(0);self.copy_button.setEnabled(False);self.notice.setPlainText('选择已修改，请计算目标对照。')

    def calculate(self):
        self.invalidate()
        try:
            grades=parse_preview_object('{"grades":'+self.grades.text()+'}','等级列表')['grades']
            enemies=[self.enemies.item(i).data(Qt.ItemDataRole.UserRole) for i in range(self.enemies.count()) if self.enemies.item(i).checkState()==Qt.CheckState.Checked]
            result=compare_enemies(self.scenario,{'stage_id':self.stage.currentData(),'enemies':enemies,'grades':grades,'orb_mode':self.orb_mode.currentData()})
        except (ValueError,KeyError,TypeError) as error:self.notice.setPlainText(str(error));return
        self.result=result;self.table.setRowCount(len(result['rows']))
        for i,row in enumerate(result['rows']):
            for j,key in enumerate(self.fields):
                value=row[key];text='未知' if value is None else format(value,'.8g') if type(value) in (int,float) else str(value)
                if row.get(key+'_applicable') is False:text='不适用'
                self.table.setItem(i,j,QTableWidgetItem(text))
        self.table.resizeColumnsToContents();self.notice.setPlainText(format_enemy_comparison(result));self.copy_button.setEnabled(True)
