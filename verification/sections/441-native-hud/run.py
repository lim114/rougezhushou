from pathlib import Path
import sys
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')]
from player_ui_verification import run
raise SystemExit(run(441,R/'verification/sections/441-native-hud/window.json'))
