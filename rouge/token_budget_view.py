from copy import deepcopy
from PySide6.QtWidgets import (QApplication, QDialog, QHBoxLayout, QLabel, QPlainTextEdit,
    QPushButton, QSpinBox, QTableWidget, QTableWidgetItem, QVBoxLayout)
from .token_budget import token_budget, format_token_budget
from .catalog import catalog


class TokenBudgetDialog(QDialog):
    def __init__(self, operator, training, parent=None):
        super().__init__(parent)
        self.operator = operator; self.training = deepcopy(training); self.result = None
        self.setWindowTitle('召唤物 · 局外配额测算'); self.resize(1050,650)
        layout = QVBoxLayout(self)
        label = QLabel('填写新增数量；在场与剩余库存可设为未知。使用打开时的培养与模组，费用不代表实际部署资格。')
        if operator=='char_2027_wang':
            label.setText(label.text()+' 望的声明在场只填写计入手动棋子限制的数量；不含自动额外棋子或技能期间数量修改。')
        label.setWordWrap(True); layout.addWidget(label)
        actions = QHBoxLayout(); actions.addWidget(QLabel('费用预算'))
        self.budget = QSpinBox(); self.budget.setRange(0,9999); actions.addWidget(self.budget)
        self.calculate_button = QPushButton('测算配额'); actions.addWidget(self.calculate_button)
        self.copy_button = QPushButton('复制配额与条件'); actions.addWidget(self.copy_button); layout.addLayout(actions)
        self.table = QTableWidget(0,8)
        self.table.setHorizontalHeaderLabels(['实体','新增','声明在场','剩余库存','单个费用参考','新增费用','库存参考上限','每类在场参考上限'])
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers); layout.addWidget(self.table)
        self.inputs = {}
        for index,(identity,token) in enumerate(catalog()['operators'][operator].get('tokens',{}).items()):
            self.table.insertRow(index); self.table.setItem(index,0,QTableWidgetItem(token['name']))
            controls = {}
            for column,key in enumerate(('additional','present','available_stock'),1):
                control = QSpinBox(); control.setRange(0 if key=='additional' else -1,100)
                if key != 'additional': control.setSpecialValueText('未知'); control.setValue(-1)
                control.valueChanged.connect(self.invalidate); self.table.setCellWidget(index,column,control)
                controls[key] = control
            self.inputs[identity] = controls
        self.notice = QPlainTextEdit(); self.notice.setReadOnly(True); layout.addWidget(self.notice)
        self.budget.valueChanged.connect(self.invalidate); self.calculate_button.clicked.connect(self.calculate)
        self.copy_button.clicked.connect(lambda: QApplication.clipboard().setText(format_token_budget(self.result)) if self.result else None)
        self.calculate()

    def invalidate(self, *_args):
        self.result = None; self.copy_button.setEnabled(False)
        for row in range(self.table.rowCount()):
            for col in range(4,8): self.table.setItem(row,col,QTableWidgetItem('待测算'))
        self.notice.setPlainText('条件已修改，请测算配额。')

    def calculate(self):
        self.invalidate()
        requests = {identity:{key:(None if control.value()<0 else control.value()) for key,control in controls.items()}
                    for identity,controls in self.inputs.items()}
        try: result = token_budget(self.operator,self.training,requests,self.budget.value())
        except (ValueError,KeyError,TypeError) as error: self.notice.setPlainText(str(error)); return
        self.result = result
        for index,row in enumerate(result['rows']):
            for column,key in enumerate(('cost_reference','requested_cost_reference','held_limit_reference','concurrent_limit_reference'),4):
                self.table.setItem(index,column,QTableWidgetItem('未知' if row[key] is None else str(row[key])))
        self.table.resizeColumnsToContents()
        warnings = []
        for row in result['rows']:
            if row['stock_sufficient_declared'] is False: warnings.append(row['name']+'：声明库存不足。')
            if row['concurrent_within_reference'] is False: warnings.append(row['name']+'：超出每类在场参考上限。')
            if row.get('stock_within_reference') is False: warnings.append(row['name']+'：声明库存超出默认培养参考；不据此否定未核验的技能库存修改。')
        self.notice.setPlainText(format_token_budget(result)+'\n'+'\n'.join(warnings))
        self.copy_button.setEnabled(True)
