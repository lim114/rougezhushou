"""Root sequential invocation with exclusive raw stdout/stderr and real child exit preservation."""
import argparse, json, subprocess, sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--prefix',required=True)
p.add_argument('command',nargs=argparse.REMAINDER);a=p.parse_args()
argv=a.command[1:] if a.command[:1]==['--'] else a.command
assert argv
base=Path(a.prefix).resolve();assert base.is_relative_to('/workspace/.continuation')
log=Path(str(base)+'.primary.log');code=Path(str(base)+'.exit-code')
assert not log.exists() and not code.exists()
with log.open('xb') as stream:
    child=subprocess.run(argv,stdout=stream,stderr=subprocess.STDOUT)
with code.open('x') as stream:stream.write(str(child.returncode)+'\n')
print(json.dumps({'actual_child_exit':child.returncode,'log':str(log),'exit_file':str(code)}),flush=True)
tail=log.read_text(errors='replace').splitlines()[-10:]
if tail:print('\n'.join(tail),flush=True)
raise SystemExit(child.returncode if child.returncode>=0 else 128-child.returncode)
