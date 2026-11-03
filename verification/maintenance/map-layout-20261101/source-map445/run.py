from pathlib import Path
import sys
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')]
from player_ui_verification import run
raise SystemExit(run(445,R/'verification/maintenance/map-layout-20261101/source-map445/window.json'))
