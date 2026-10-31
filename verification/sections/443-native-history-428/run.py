from pathlib import Path
import sys
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')]
from player_ui_verification import run
raise SystemExit(run(428,R/'verification/sections/443-native-history-428/window.json'))
