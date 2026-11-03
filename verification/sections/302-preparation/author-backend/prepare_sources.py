"""Cache-only copy of exact existing public source files for candidate build."""
import ast
from hashlib import sha256
import json
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CANDIDATE = HERE / 'candidate'
builder = CANDIDATE / 'scripts/build_ritual_weakening_302.py'
tree = ast.parse(builder.read_text(encoding='utf8'))
sources = next(ast.literal_eval(n.value) for n in tree.body
               if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'SOURCE_FILES' for t in n.targets))
pins = {}
for name, expected in sources.items():
    source = ROOT / name
    raw = source.read_bytes()
    assert sha256(raw).hexdigest() == expected, name
    destination = CANDIDATE / name
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)
    pins[name] = {'sha256': expected, 'bytes': len(raw)}
config = {'schema': 'ritual_weakening_build_inputs_v1',
          'game_commit': 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add', 'sources': pins,
          'roles': {n: 'runtime' if n in ('rouge/data/node-catalog.json', 'rouge/node_catalog.py')
                    else 'build_only' for n in sources},
          'original_research_archive': 'verification/sections/301-preparation/future-notes-and-ritual-research',
          'enemy_tool_response_is_not_complete_HTML': True,
          'full_originals_reused_not_newly_acquired': True}
path = CANDIDATE / 'research/p3-ritual-weakening-302/fixed-build-inputs.json'
path.write_bytes((json.dumps(config, ensure_ascii=False, indent=2) + '\n').encode('utf8'))
print(json.dumps({'kind': 'CACHE_SOURCE_COPY_NOT_PRODUCT_ACCEPTANCE', 'files': pins,
                  'config_sha256': sha256(path.read_bytes()).hexdigest(),
                  'live_sources_modified': False}, ensure_ascii=False, indent=2))
