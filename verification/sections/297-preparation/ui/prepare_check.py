"""Syntax/contract inventory only; this does not import Qt or run the tests."""
import ast
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
FILES = ('rouge/expedition_results_view.py', 'tests/test_expedition_results_view_297.py')


def main():
    pins = {}
    test_methods = []
    for relative in FILES:
        path = HERE / relative
        blob = path.read_bytes()
        source = blob.decode('utf-8')
        tree = ast.parse(source, str(path))
        compile(tree, str(path), 'exec')
        pins[relative] = {'sha256': hashlib.sha256(blob).hexdigest(), 'bytes': len(blob)}
        if relative.startswith('tests/'):
            test_methods = [node.name for node in ast.walk(tree)
                            if isinstance(node, ast.FunctionDef) and node.name.startswith('test_')]
            assert len(test_methods) == 16
            assert 'from rouge.expedition_results_view import ExpeditionResultsPanel' in source
            assert '.cache' not in source
    result = {'kind': 'SECTION297_EXPEDITION_UI_PREPARATION_ONLY', 'syntax_compiled': True,
              'files': pins, 'test_methods': test_methods, 'test_methods_prepared': len(test_methods),
              'qt_imported_or_started': False, 'tests_executed': False, 'product_pass_claimed': False,
              'live_source_modified': False, 'game_or_chat_operations': False}
    (HERE / 'preparation-check.json').write_bytes((json.dumps(result, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
