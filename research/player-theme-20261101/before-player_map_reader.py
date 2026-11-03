"""Reuse verified event/stage readers alongside the compact exploration map."""
REFERENCE_STYLE='''
QDialog#mapReferenceWindow {background:#262528;color:#ededed;border:1px solid #585858;border-radius:12px;}
QDialog#mapReferenceWindow QLabel {color:#ededed;background:transparent;}
QDialog#mapReferenceWindow QCheckBox {color:#ededed;background:transparent;}
QDialog#mapReferenceWindow QTabWidget::pane {background:#262528;border:0;}
QDialog#mapReferenceWindow QTabBar::tab {color:#d7d7d7;background:#333333;border:0;border-radius:9px;padding:6px 12px;}
QDialog#mapReferenceWindow QTabBar::tab:selected {background:#484848;color:white;}
QDialog#mapReferenceWindow QPushButton,QDialog#mapReferenceWindow QComboBox {color:#ededed;background:#303030;border:1px solid #585858;border-radius:7px;padding:5px;}
QDialog#mapReferenceWindow QPushButton:disabled {color:#929999;}
QDialog#mapReferenceWindow QLineEdit {color:#ededed;background:#2a2a2a;border:1px solid #585858;border-radius:7px;padding:6px;selection-background-color:#9bd6c1;selection-color:#152621;}
QDialog#mapReferenceWindow QPlainTextEdit,QDialog#mapReferenceWindow QTextBrowser,QDialog#mapReferenceWindow QListWidget,QDialog#mapReferenceWindow QTreeWidget {color:#ededed;background:#262528;border:1px solid #585858;}
'''

def readable(dialog):
    if dialog is not None:dialog.setObjectName('mapReferenceWindow');dialog.setStyleSheet(REFERENCE_STYLE)
    return dialog

def make_reader(kind,record,parent,*,historical=False,config=None):
    if not isinstance(record,dict)or not isinstance(record.get('id'),str)or not isinstance(record.get('title'),str):return None
    from .player_compact import ToolPopover
    if kind=='battle':
        identity=record.get('id')
        from .current_battle_view import CurrentBattlePanel
        panel=CurrentBattlePanel(identity)
        if panel.result is None:panel.deleteLater();return None
        if config is not None and not historical:panel.set_context(config)
        dialog=ToolPopover(panel.result['name']+' · 固定作战预览',panel,parent);dialog.panel=panel;dialog.resize(920,720)
        dialog.finished.connect(panel._close_readers)
        return readable(dialog)
    if kind=='event':
        from .current_node_readers import binding_for
        from .current_node_readers_view import make_dialog
        binding=binding_for(record)
        return readable(make_dialog(binding,parent,historical=historical))if binding else None
    return None
