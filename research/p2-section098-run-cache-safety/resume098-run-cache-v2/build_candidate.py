"""Source transport only. No project imports, Git or test execution."""
import ast
import hashlib
import json
from pathlib import Path

ROOT = Path('/workspace/rougezhushou')
PACKET = Path('/workspace/.continuation/resume098-run-cache-v2')
OLD = Path('/workspace/.continuation/p2-runstate-reliability098-candidate-source-v1')

baseline = (ROOT / 'rouge/run_state.py').read_bytes()
assert hashlib.sha256(baseline).hexdigest() == '20c6a00a72744017ebbc0fcb3b1009dddf8a6702aa01bf273b4b51c344692fd9'
source = baseline.decode('utf-8')
assert source.count('            self.state.update(saved)\r\n') == 1
source = source.replace('            self.state.update(saved)\r\n',
                        '            _validate_saved_containers(saved)\r\n            self.state.update(saved)\r\n')
assert source.count('                    if event[\'kind\']') == 2
source = source.replace("                    if event['kind']", "                    if event.get('kind')")
needle = "        state=self.state;relics=dict(observed.get('relics',{'ids':[],'icons':[],'count':None,'source':'unread'}));count=relics.get('count')\r\n"
assert source.count(needle) == 1
source = source.replace(needle, needle + "        if isinstance(count,bool):\r\n            count=None;relics['count']=None\r\n")
guard = (PACKET / 'container_guard.py.txt').read_text(encoding='utf-8').replace('\n', '\r\n')
source = source.replace('class RunState:\r\n', guard + 'class RunState:\r\n')
ast.parse(source)
(PACKET / 'baseline/rouge/run_state.py').write_bytes(baseline)
(PACKET / 'candidate/rouge/run_state.py').write_bytes(source.encode('utf-8'))

old_test = (OLD / 'tests/test_run_state_reliability.py').read_bytes()
addition = (PACKET / 'additional_tests.py.txt').read_text(encoding='utf-8')
tests = old_test.decode('utf-8')
assert tests.count("if __name__ == '__main__':") == 1
tests = tests.replace("if __name__ == '__main__':", addition + "if __name__ == '__main__':")
ast.parse(tests)
(PACKET / 'baseline/tests/test_run_state_reliability.py').write_bytes(old_test)
(PACKET / 'candidate/tests/test_run_state_reliability.py').write_bytes(tests.encode('utf-8'))

app = (Path('/workspace/.continuation/resume098-run-cache-v1') / 'baseline/rouge/app.py').read_bytes()
old_line = b"        current={key:value for key,value in member['fields'].items() if key not in member.get('invalid_fields',[])}\r\n"
new_line = b"        current={key:value for key,value in member.get('fields',{}).items() if key not in member.get('invalid_fields',[])}\r\n"
assert app.count(old_line) == 1
(PACKET / 'baseline/rouge/app.py').write_bytes(app)
candidate_app = app.replace(old_line, new_line)
ast.parse(candidate_app.decode('utf-8'))
(PACKET / 'candidate/rouge/app.py').write_bytes(candidate_app)

files = []
for path in sorted(PACKET.rglob('*')):
    if path.is_file() and path.name not in ('source-manifest.json',):
        raw = path.read_bytes()
        files.append({'path': str(path.relative_to(PACKET)), 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()})
tree = ast.parse(tests)
methods = [node.name for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith('test_')]
manifest = {'status': 'SOURCE_ONLY_NOT_EXECUTED_OR_APPLIED', 'runtime_executed': False,
            'test_methods_source_count': len(methods), 'test_methods_source': methods, 'files': files,
            'registry_instruction': 'Root insert test_run_state_reliability into actual current REGRESSION_MODULES; do not copy old future097 registry.',
            'app_apply_instruction': 'Apply only exact single-line old/new replacement to the current app after completed097. Do not replace the full app from this Source snapshot.'}
(PACKET / 'source-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'status': manifest['status'], 'test_methods_source_count': len(methods), 'files': files}, ensure_ascii=False))
