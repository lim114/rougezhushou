"""Generate pinned, local-only PyQtDarkTheme assets; no theme package at runtime."""
from pathlib import Path
from hashlib import sha256
from unittest.mock import patch
import argparse,sys,json,re,os
parser=argparse.ArgumentParser();parser.add_argument('--runtime',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);parser.add_argument('--baseline-light',type=Path,required=True);args=parser.parse_args()
runtime=args.runtime.resolve();out=args.output.resolve();out.mkdir(parents=True,exist_ok=False);icons=out/'icons';icons.mkdir()
sys.path.insert(0,str(runtime));os.environ['QT_API']='pyside6'
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette,QColor
from PySide6.QtCore import qVersion
app=QApplication([])
import qdarktheme
from qdarktheme import _style_loader
from qdarktheme._template import filter as filters
assert qdarktheme.__version__=='2.1.0'
colors={'dark': {'background': '#111213', 'foreground': '#e7e9e9', 'primary': '#9bd6c1', 'background>list': '#111213', 'background>popup': '#202224', 'input.background': '#202224', 'border': '#505354', 'scrollbar.background': '#111213', 'scrollbarSlider.background': '#7e8384'}, 'light': {'background': '#f5f5f7', 'foreground': '#303139', 'primary': '#567e72', 'background>list': '#ffffff', 'background>popup': '#ffffff', 'input.background': '#e6e6eb', 'border': '#dedee5', 'scrollbar.background': '#f5f5f7', 'scrollbarSlider.background': '#b3b5bf'}, 'reference': {'background': '#262528', 'foreground': '#ededed', 'primary': '#c1c7cb', 'background>list': '#262528', 'background>popup': '#303030', 'input.background': '#2a2a2a', 'border': '#585858', 'scrollbar.background': '#262528', 'scrollbarSlider.background': '#89888a'}}
palettes={}
with patch.object(_style_loader,'get_cash_root_path',return_value=icons),patch.object(filters,'get_cash_root_path',return_value=icons):
 for theme,custom in colors.items():
  base_theme='dark'if theme=='reference'else theme
  sheet=qdarktheme.load_stylesheet(base_theme,custom_colors=custom)
  sheet=sheet.replace(icons.as_posix(),'@ICONS@')
  sheet=re.sub(r'url\((@ICONS@/[^)]+)\)',r'url("\1")',sheet)
  assert not re.search(r'[A-Za-z]:[/\\]',sheet),'No machine paths in packaged styles'
  (out/(theme+'.qss')).write_text(sheet+'\n','utf8')
  palette=qdarktheme.load_palette(base_theme,custom_colors=custom,for_stylesheet=False)
  palette.setColor(QPalette.ColorRole.Accent,QColor(custom['primary']))
  palette.setColor(QPalette.ColorRole.BrightText,QColor(custom['foreground']))
  palettes[theme]={group.name:{role.name:palette.color(group,role).name(QColor.NameFormat.HexArgb)for role in QPalette.ColorRole if role not in(QPalette.ColorRole.NoRole,QPalette.ColorRole.NColorRoles)}for group in(QPalette.ColorGroup.Active,QPalette.ColorGroup.Inactive,QPalette.ColorGroup.Disabled)}
palettes['light']=json.loads(args.baseline_light.read_bytes())
(out/'palettes.json').write_text(json.dumps(palettes,ensure_ascii=False,indent=2)+'\n','utf8')
(out/'LICENSE-PyQtDarkTheme.txt').write_bytes((runtime/'pyqtdarktheme-2.1.0.dist-info/LICENSE.txt').read_bytes())
manifest={'upstream':'https://github.com/5yutan5/PyQtDarkTheme','reviewed_commit':'96eb7e368039ab446952573bafc17d54b7ef5123','generated_from_wheel_version':'2.1.0','upstream_python_requires':'>=3.7,<3.12','build_exercised_python':sys.version.split()[0],'generated_Qt':qVersion(),'runtime_upstream_Python_required':False,'only_static_qss_palette_svg_shipped':True,'system_theme_detection_or_listener_enabled':False,'local_changes':'Fixed light/dark reference colors; quote relocatable SVG paths; export current Qt Accent role. Theme layout and state rules generated from upstream.','colors':colors,'files':{p.relative_to(out).as_posix():{'sha256':sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}for p in sorted(out.rglob('*'))if p.is_file()}}
(out/'source.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n','utf8')
print(json.dumps({'generated':True,'svg_icons':len(list(icons.glob('*.svg'))),'qss_bytes':{n:(out/(n+'.qss')).stat().st_size for n in colors},'runtime_package_required':False}))
