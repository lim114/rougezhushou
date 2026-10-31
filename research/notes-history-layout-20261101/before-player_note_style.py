"""Shared existing note palette, independent of note storage and follow logic."""
NOTE_STYLE='''
QWidget#noteCard{background:white;border:1px solid #dedee5;border-radius:9px;}
QLabel#noteCardTitle{background:transparent;color:#303139;padding:7px 10px;border-bottom:1px solid #ededf1;}
QWidget#sceneNotesSurface QWidget#noteCard QTextBrowser,QWidget#sceneNotesSurface QWidget#noteCard QPlainTextEdit{border:0;border-radius:0;padding:8px;}
QWidget#sceneNotesSurface QToolButton{background:#e6e6eb;color:#303139;border:0;border-radius:8px;padding:4px 9px;}
QWidget#sceneNotesSurface QComboBox{background:#e6e6eb;color:#303139;border:1px solid #cdcdd5;border-radius:9px;padding:5px;}
QWidget#sceneNotesSurface QComboBox QAbstractItemView{background:white;color:#303139;selection-background-color:#cde5eb;selection-color:#25262b;}
QWidget#sceneNotesSurface QScrollArea,QWidget#noteAncestors,QWidget#noteAncestorsViewport{background:#f5f5f7;border:0;}
QScrollArea#noteAncestorScroll QScrollBar:vertical{background:#ededf1;width:10px;}
QScrollArea#noteAncestorScroll QScrollBar::handle:vertical{background:#b3b5bf;border-radius:4px;min-height:24px;}
QWidget#sceneNotesSurface,QDialog#sceneNotesEditor,QDialog#sceneNotesWindow,QDialog#sceneNotesLibrary{background:#f5f5f7;color:#25262b;}
QDialog#sceneNotesWindow{border:1px solid #dedee5;border-radius:12px;}
QDialog#sceneNotesWindow QPushButton#popoverCloseButton{padding:0;border:0;background:transparent;color:#303139;}
QDialog#sceneNotesWindow QPushButton#popoverCloseButton:hover{background:#e6e6eb;}
QWidget#sceneNotesSurface QLabel,QDialog#sceneNotesEditor QLabel,QDialog#sceneNotesWindow QLabel,QDialog#sceneNotesLibrary QLabel{color:#303139;background:transparent;}
QWidget#sceneNotesSurface QCheckBox,QDialog#sceneNotesEditor QCheckBox,QDialog#sceneNotesEditor QTabWidget{color:#40414a;}
QWidget#sceneNotesSurface QTextBrowser,QDialog#sceneNotesEditor QPlainTextEdit,QDialog#sceneNotesEditor QTextBrowser,QDialog#sceneNotesLibrary QPlainTextEdit,QDialog#sceneNotesLibrary QListWidget,QDialog#sceneNotesLibrary QLineEdit{
 background:white;color:#25262b;border:1px solid #dedee5;border-radius:12px;padding:12px;selection-background-color:#cde5eb;selection-color:#25262b;}
QWidget#sceneNotesSurface QPushButton,QDialog#sceneNotesEditor QPushButton,QDialog#sceneNotesLibrary QPushButton{
 background:#e6e6eb;color:#303139;border:0;border-radius:13px;padding:7px 14px;}
QWidget#sceneNotesSurface QPushButton:hover,QDialog#sceneNotesEditor QPushButton:hover,QDialog#sceneNotesLibrary QPushButton:hover{background:#d6e5e9;}
QWidget#sceneNotesSurface QPushButton:disabled,QDialog#sceneNotesEditor QPushButton:disabled,QDialog#sceneNotesLibrary QPushButton:disabled{color:#92929b;}
QDialog#sceneNotesEditor QTabBar::tab{background:#e6e6eb;color:#484952;border:0;border-radius:12px;padding:6px 16px;margin:2px;}
QDialog#sceneNotesEditor QTabBar::tab:selected{background:#303438;color:white;}
QDialog#sceneNotesEditor QTabWidget::pane{border:0;}
'''
