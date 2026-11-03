"""Build narrow section-52 hunks from the frozen external pair."""
import difflib
from pathlib import Path

OUT = Path(__file__).resolve().parent


def patch(name, new=False):
    before = [] if new else (OUT / 'baseline' / name).read_bytes().decode().splitlines(keepends=True)
    after = (OUT / 'draft' / name).read_bytes().decode().splitlines(keepends=True)
    return ''.join(difflib.unified_diff(before, after,
                   fromfile='/dev/null' if new else 'a/' + name, tofile='b/' + name))


code = ''.join(patch(name) for name in ('rouge/operator_engine.py', 'rouge/reporting.py'))
code += patch('rouge/amiya_continuous_reference.py', new=True)
tests = patch('tests/test_amiya_continuous_lifetime.py', new=True)
for name, content in (('code.patch', code), ('tests.patch', tests), ('section52.patch', code + tests)):
    (OUT / name).write_bytes(content.encode())
