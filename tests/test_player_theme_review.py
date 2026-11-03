"""Relocatable external theme assets and scoped, state-preserving Qt adoption."""
from pathlib import Path
from hashlib import sha256
import json,re,sys,tomllib,unittest
from PySide6.QtWidgets import QApplication,QWidget,QComboBox,QPlainTextEdit,QVBoxLayout
from PySide6.QtGui import QIcon,QPalette
from rouge.player_theme import DATA,assets,apply_theme
from rouge.player_compact import ToolPopover

class PlayerThemeReview(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
 def test_every_shipped_upstream_file_keeps_the_declared_bytes(self):
  manifest=json.loads((DATA/'source.json').read_bytes())
  self.assertEqual(manifest['generated_from_wheel_version'],'2.1.0');self.assertFalse(manifest['runtime_upstream_Python_required'])
  self.assertIn('Yunosuke Ohsugi',(DATA/'LICENSE-PyQtDarkTheme.txt').read_text('utf8'))
  for name,row in manifest['files'].items():
   raw=(DATA/name).read_bytes();self.assertEqual(sha256(raw).hexdigest(),row['sha256']);self.assertEqual(len(raw),row['bytes'])
 def test_both_styles_resolve_all_icons_in_the_current_chinese_workspace(self):
  for name in ('light','dark'):
   sheet,_=assets(name);self.assertNotIn('@ICONS@',sheet)
   paths=set(re.findall(r'url\("([^"]+)"\)',sheet));self.assertGreater(len(paths),20)
   for path in paths:self.assertTrue(Path(path).is_file(),path);self.assertFalse(QIcon(path).pixmap(18,18).isNull(),path)
 def test_static_styles_do_not_load_upstream_runtime_or_change_app_palette(self):
  before=self.qt.palette();widget=QWidget();self.addCleanup(widget.close);apply_theme(widget,'dark')
  self.assertEqual(self.qt.palette(),before)
  self.assertNotIn('qdarktheme',sys.modules);self.assertNotIn('darkdetect',sys.modules)
  self.assertEqual(widget.property('playerTheme'),'dark');self.assertEqual(widget.palette().color(QPalette.ColorRole.Accent).name(),'#9bd6c1')
 def test_light_and_dark_text_remain_distinct_and_readable_on_their_surfaces(self):
  for theme in ('light','dark'):
   _,p=assets(theme);text=p.color(QPalette.ColorGroup.Active,QPalette.ColorRole.Text);base=p.color(QPalette.ColorRole.Base)
   def luminance(c):
    values=[v/12.92 if v<=.04045 else((v+.055)/1.055)**2.4 for v in(c.redF(),c.greenF(),c.blueF())]
    return sum(a*b for a,b in zip(values,(.2126,.7152,.0722)))
   a,b=sorted((luminance(text),luminance(base)));self.assertGreater((b+.05)/(a+.05),4.5)
 def test_applying_shared_style_does_not_reset_selection_or_text_reading(self):
  w=QWidget();self.addCleanup(w.close);box=QVBoxLayout(w);combo=QComboBox();combo.addItems(['第一项','第二项']);box.addWidget(combo);text=QPlainTextEdit();box.addWidget(text)
  text.setPlainText('\n'.join(str(i)for i in range(80)));w.show();combo.setCurrentIndex(1);self.qt.processEvents();text.verticalScrollBar().setValue(15);cursor=text.textCursor();cursor.setPosition(4);text.setTextCursor(cursor)
  before=(combo.currentIndex(),text.toPlainText(),text.textCursor().position(),text.verticalScrollBar().value())
  apply_theme(w);self.qt.processEvents();self.assertEqual((combo.currentIndex(),text.toPlainText(),text.textCursor().position(),text.verticalScrollBar().value()),before)
 def test_owned_popover_keeps_callback_close_and_explicit_theme_contract(self):
  owner=QWidget();self.addCleanup(owner.close);called=[];dialog=ToolPopover('只读资料',QWidget(),owner,on_show=lambda:called.append(1),theme='light',object_name='themeTest')
  self.addCleanup(dialog.close);dialog.show();self.qt.processEvents();self.assertEqual(called,[1]);self.assertEqual(dialog.objectName(),'themeTest');self.assertEqual(dialog.property('playerTheme'),'light')
  dialog.hide();dialog.show();self.qt.processEvents();self.assertEqual(called,[1,1]);dialog.close();self.assertFalse(dialog.isVisible())
 def test_distribution_patterns_include_every_static_theme_file(self):
  root=Path(__file__).resolve().parents[1];config=tomllib.loads((root/'pyproject.toml').read_text('utf8'));patterns=config['tool']['setuptools']['package-data']['rouge']
  included={p.resolve()for pattern in patterns for p in(root/'rouge').glob(pattern)if p.is_file()}
  for p in DATA.rglob('*'):
   if p.is_file():self.assertIn(p.resolve(),included,p.name)
 def test_unknown_theme_cannot_select_an_arbitrary_asset_path(self):
  with self.assertRaises(KeyError):assets('../settings')

if __name__=='__main__':unittest.main()
