from pathlib import Path
import sys
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')]
from player_ui_verification import run
raise SystemExit(run(442,R/'verification/sections/442-native-capacity/window.json'))
