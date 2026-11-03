from pathlib import Path
import argparse,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from player_ui_verification import run,source_hashes

def bound_files():return source_hashes()
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--receipt',type=Path,required=True);a=p.parse_args();raise SystemExit(run(420,a.receipt))
