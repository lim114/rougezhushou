"""Reuse verified event/stage readers alongside the compact exploration map."""
REFERENCE_STYLE='''
QDialog#mapReferenceWindow {background:#262528;color:#ededed;border:1px solid #585858;border-radius:12px;}
QDialog#mapReferenceWindow QWidget {background:#262528;}
QDialog#mapReferenceWindow QLabel {color:#ededed;background:transparent;}
QDialog#mapReferenceWindow QCheckBox {color:#ededed;background:transparent;}
QDialog#mapReferenceWindow QTabWidget::pane {background:#262528;border:0;}
QDialog#mapReferenceWindow QTabBar::tab {color:#d7d7d7;background:#333333;border:0;border-radius:9px;padding:6px 12px;}
QDialog#mapReferenceWindow QTabBar::tab:selected {background:#484848;color:white;}
QDialog#mapReferenceWindow QPushButton,QDialog#mapReferenceWindow QComboBox {color:#ededed;background:#303030;border:1px solid #585858;border-radius:7px;padding:5px;}
QDialog#mapReferenceWindow QPushButton:disabled {color:#929999;}
QDialog#mapReferenceWindow QLineEdit {color:#ededed;background:#2a2a2a;border:1px solid #585858;border-radius:7px;padding:6px;selection-background-color:#c1c7cb;selection-color:#262528;}
QDialog#mapReferenceWindow QPlainTextEdit,QDialog#mapReferenceWindow QTextBrowser,QDialog#mapReferenceWindow QListWidget,QDialog#mapReferenceWindow QTreeWidget {color:#ededed;background:#262528;border:1px solid #585858;}
'''

def readable(dialog):
    if dialog is not None:
        from .player_theme import apply_theme
        dialog.setObjectName('mapReferenceWindow');apply_theme(dialog,'dark',extra=REFERENCE_STYLE)
    return dialog

def prepare_reference_window(dialog,width,height):
    from PySide6.QtWidgets import QPushButton
    readable(dialog)
    for button in dialog.findChildren(QPushButton):button.setAutoDefault(False)
    area=dialog.screen().availableGeometry()
    dialog.resize(min(width,area.width()-40),min(height,area.height()-40))


def make_reader(kind,record,parent,*,historical=False,config=None,page_owner=None):
    if not isinstance(record,dict)or not isinstance(record.get('id'),str)or not isinstance(record.get('title'),str):return None
    from .player_compact import ToolPopover
    if kind=='battle':
        identity=record.get('id')
        from .current_battle_view import CurrentBattlePanel,size_battle_window
        panel=CurrentBattlePanel(identity)
        if panel.result is None:panel.deleteLater();return None
        if config is not None and not historical:panel.set_context(config)
        title=panel.result['name']+' · 固定作战预览'
        if page_owner is None:
            dialog=ToolPopover(title,panel,parent)
        else:
            from .player_reference_window import ToolPage
            dialog=ToolPage(title,panel,page_owner,object_name='mapReferenceWindow',extra_style=REFERENCE_STYLE)
        dialog.panel=panel;size_battle_window(dialog)
        dialog.finished.connect(panel._close_readers)
        return readable(dialog)if page_owner is None else dialog
    if kind=='event':
        from .current_node_readers import binding_for
        from .current_node_readers_view import make_dialog
        binding=binding_for(record)
        return make_dialog(binding,parent,historical=historical,page_owner=page_owner)if binding else None
    return None
