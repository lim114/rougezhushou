"""Reuse verified event/stage readers alongside the compact exploration map."""
REFERENCE_STYLE='''
QDialog#mapReferenceWindow {background:#f5f5f7;color:#25332f;border:1px solid #bbc1c5;border-radius:12px;}
QDialog#mapReferenceWindow QLabel {color:#25332f;background:transparent;}
QDialog#mapReferenceWindow QCheckBox {color:#263630;background:transparent;}
QDialog#mapReferenceWindow QTabWidget::pane {background:#f5f5f7;border:0;}
QDialog#mapReferenceWindow QTabBar::tab {color:#35403c;background:#e4e7e6;border:0;border-radius:9px;padding:6px 12px;}
QDialog#mapReferenceWindow QTabBar::tab:selected {background:#2c3533;color:white;}
QDialog#mapReferenceWindow QPushButton,QDialog#mapReferenceWindow QComboBox {color:#263630;background:#e8ebea;border:1px solid #bbc6c1;border-radius:7px;padding:5px;}
QDialog#mapReferenceWindow QPushButton:disabled {color:#92999a;}
QDialog#mapReferenceWindow QLineEdit {color:#28332e;background:white;border:1px solid #d2d9d5;border-radius:7px;padding:6px;selection-background-color:#cde5eb;selection-color:#25332f;}
QDialog#mapReferenceWindow QPlainTextEdit,QDialog#mapReferenceWindow QTextBrowser,QDialog#mapReferenceWindow QListWidget,QDialog#mapReferenceWindow QTreeWidget {color:#28332e;background:white;border:1px solid #d2d9d5;}
'''

def readable(dialog):
    if dialog is not None:dialog.setObjectName('mapReferenceWindow');dialog.setStyleSheet(REFERENCE_STYLE)
    return dialog

def make_reader(kind,record,parent,*,historical=False):
    if not isinstance(record,dict)or not isinstance(record.get('id'),str)or not isinstance(record.get('title'),str):return None
    from .player_compact import ToolPopover
    from . import current_battle_reference
    if kind=='battle':
        identity=record.get('id')
        if current_battle_reference.stage_reference(identity)is None:return None
        from .current_battle_view import CurrentBattlePanel
        panel=CurrentBattlePanel(identity)
        if panel.result is None:return None
        dialog=ToolPopover(panel.result['name']+' · 固定作战预览',panel,parent);dialog.panel=panel;dialog.resize(920,720)
        return readable(dialog)
    if kind=='event':
        from .current_node_readers import binding_for
        from .current_node_readers_view import make_dialog
        binding=binding_for(record)
        return readable(make_dialog(binding,parent,historical=historical))if binding else None
    return None
