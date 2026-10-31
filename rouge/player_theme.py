"""Player surfaces use pinned PyQtDarkTheme styles without its Python runtime.

Upstream MIT attribution and exact generated files: data/player-theme/source.json.
Only owned opaque readers use this; the transparent toolbar/game overlay does not.
"""
from functools import lru_cache
from pathlib import Path
import json
from PySide6.QtGui import QPalette,QColor,QFont

DATA=Path(__file__).with_name('data')/'player-theme'

@lru_cache(maxsize=2)
def assets(theme):
    filename={'light':'light.qss','dark':'dark.qss'}[theme]
    sheet=(DATA/filename).read_text('utf8').replace('@ICONS@',(DATA/'icons').as_posix())
    palette=QPalette()
    for group,roles in json.loads((DATA/'palettes.json').read_bytes())[theme].items():
        for role,color in roles.items():palette.setColor(QPalette.ColorGroup[group],QPalette.ColorRole[role],QColor(color))
    background,foreground,control,border=('#f5f5f7','#303139','#e6e6eb','#dedee5')if theme=='light'else('#1b2928','#e7f5f0','#30433f','#56655f')
    sheet+=f'''
QDialog{{border:1px solid {border};border-radius:12px;}}
QPushButton{{background:{control};color:{foreground};border:0;border-radius:10px;padding:5px 10px;}}
QTabWidget::pane{{border:0;}}
QTabBar::tab{{background:{control};color:{foreground};border:0;border-radius:12px;padding:6px 13px;margin:2px;}}
QTabBar::tab:selected{{background:{foreground};color:{background};}}
QPushButton#popoverCloseButton{{border:0;background:transparent;padding:0;border-radius:8px;}}
QPushButton#popoverCloseButton:hover{{background:{control};}}
QLabel#popoverTitle{{background:transparent;font-weight:500;}}
'''
    return sheet,palette

def apply_theme(widget,theme='light',*,extra=''):
    sheet,palette=assets(theme)
    widget.setProperty('playerTheme',theme);widget.setPalette(QPalette(palette));widget.setFont(QFont('Microsoft YaHei UI',9));widget.setStyleSheet(sheet+extra)
