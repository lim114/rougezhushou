"""Build cache-only fixed-dependency adapter; never rewrite prior product files."""
import hashlib
import json
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sha = lambda raw: hashlib.sha256(raw).hexdigest()
cores = {'skill_data_cost_reference.py': '7cd8eee14c217c46419b5ac70bbcfe14f63e67a5687b7974d8718ae60618077a',
         'skill_cost_rounding_consensus.py': '86853e05e770e17d8cdbaabe14d4fb9f13e576efea378333b5470a39ec78aa77'}
target = HERE / 'rouge'
target.mkdir(exist_ok=True)
for filename, expected in cores.items():
    original = ROOT / 'rouge' / filename
    assert sha(original.read_bytes()) == expected
    shutil.copyfile(original, target / filename)
for directory in ('p2-skill-data-cost-278', 'p2-cost-rounding-consensus-280'):
    source = ROOT / 'research' / directory
    destination = HERE / 'research' / directory
    destination.mkdir(parents=True, exist_ok=True)
    for path in source.iterdir():
        assert path.is_file(), 'only reviewed public source packet files are copied'
        shutil.copyfile(path, destination / path.name)
        assert sha(path.read_bytes()) == sha((destination / path.name).read_bytes())
old = (target / 'skill_data_cost_reference.py').read_text(encoding='utf8')
constants = old[old.index('UNKNOWNS ='):old.index('\n\ndef source_data():')]
validators = old[old.index('def _keys('):old.index('\n\ndef _power2(')]
template = (HERE / 'adapter_template.py').read_text(encoding='utf8')
assert '__LEGACY_CONSTANTS__' in template and '__LEGACY_VALIDATORS__' in template
module_text = template.replace('__LEGACY_CONSTANTS__', constants).replace('__LEGACY_VALIDATORS__', validators)
module = target / 'skill_data_cost_consensus_reference.py'
assert not module.exists(), 'preserve a previous actual prototype'
module.write_text(module_text, encoding='utf8')
print(json.dumps({'core_path': str(module), 'draft_unbound_sha256': sha(module.read_bytes()),
                  'copied_dependency_core_sha256': cores, 'public_packet_copy_only': True}, ensure_ascii=False))
