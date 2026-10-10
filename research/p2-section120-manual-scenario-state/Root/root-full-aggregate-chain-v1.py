"""Root actual aggregate after separate real four-PNG tool inspection."""
import argparse,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--section',type=int,choices=(120,125),required=True);p.add_argument('--linux-version',type=int,required=True);a=p.parse_args()
n=a.section;B=Path('/workspace/.continuation');P=B/f'full120-125-gates-source-v1/section{n}'
files={'guard':B/f'full{n}-root-actual-guard-v1.json','adapters':P/'adapters','capability':B/f'full{n}-capability-actual-v1.json','capability-primary':B/f'full{n}-capability-actual-v1.exit-code','linux':B/f'full{n}-linux-actual-v{a.linux_version}.json','linux-primary':B/f'full{n}-linux-actual-v{a.linux_version}.exit-code','wine':B/f'full{n}-wine-actual-v1.json','wine-primary':B/f'full{n}-wine-actual-v1.exit-code','selected':B/f'full{n}-selected-actual-v1.json','selected-primary':B/f'full{n}-selected-actual-v1.exit-code','linux-pip-log':B/f'full{n}-linux-pip-actual-v1.primary.log','linux-pip-primary':B/f'full{n}-linux-pip-actual-v1.exit-code','wine-pip-log':B/f'full{n}-wine-pip-actual-v1.primary.log','wine-pip-primary':B/f'full{n}-wine-pip-actual-v1.exit-code','window-supervisor':B/f'full{n}-window-supervisor-actual-v1.json','window-supervisor-primary':B/f'full{n}-window-supervisor-actual-v1.exit-code','window-child-primary':B/f'full{n}-window-child-actual-v1.exit-code','window-out':B/f'full{n}-window-actual-v1','saved':B/f'full{n}-saved-actual-v1.json','saved-primary':B/f'full{n}-saved-actual-v1.exit-code','saved-auditor':P/f'saved-audit/audit_full{n}.py','visual':B/f'full{n}-visual-actual-v1.json','out':B/f'full{n}-aggregate-actual-v1.json'}
for k,f in files.items():
 if k!='out':assert f.exists(),k
command=['python3',str(B/'full120-125-gates-independent-source-v1/candidate/aggregate_full_scope.py'),'--section',str(n),'--root','/workspace/rougezhushou']
for k,f in files.items():command+=['--'+k,str(f)]
subprocess.run(['python3',str(B/'root-run-primary-v1.py'),'--prefix',str(B/f'full{n}-aggregate-actual-v1'),'--',*command],check=True)
