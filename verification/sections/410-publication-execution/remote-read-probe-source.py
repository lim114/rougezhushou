from pathlib import Path
import subprocess,json
R=Path(__file__).resolve().parents[1]
local=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()
parent=subprocess.check_output(['git','rev-parse','HEAD^'],cwd=R,text=True).strip()
remote=subprocess.check_output(['git','ls-remote','origin','refs/heads/codex/p2-development'],cwd=R,text=True).split()[0]
assert remote in (local,parent),'Remote changed independently; do not overwrite or force push.'
print(json.dumps({'local_HEAD':local,'remote_HEAD':remote,'safe_for_ordinary_push':True,'read_only':True}))
