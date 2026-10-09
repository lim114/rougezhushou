"""Root-only original Qt font prerequisite probe; no project/test imports.
Compiled for Source review only. A missing original font is failure evidence,
never an executed test PASS. Additional fonts retain their real path/name.
"""
import argparse
import hashlib
import json
import os
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--additional-font', type=Path, action='append', default=[])
    args = parser.parse_args()
    os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
    from PySide6.QtWidgets import QApplication
    from PySide6.QtGui import QFontDatabase
    app = QApplication.instance() or QApplication([])
    original = Path(os.environ.get('WINDIR', 'C:/Windows')) / 'Fonts/msyh.ttc'
    records = []
    for role, path in [('original_test_font', original)] + [('additional_real_font', p) for p in args.additional_font]:
        record = {'role': role, 'requested_path': str(path), 'resolved_path': str(path.resolve()),
                  'is_file': path.is_file(), 'bytes': None, 'sha256': None,
                  'font_id': None, 'families': None, 'error': None}
        try:
            if path.is_file():
                data = path.read_bytes()
                record['bytes'] = len(data)
                record['sha256'] = hashlib.sha256(data).hexdigest()
            font_id = QFontDatabase.addApplicationFont(str(path))
            record['font_id'] = font_id
            record['families'] = QFontDatabase.applicationFontFamilies(font_id)
        except Exception as exc:
            record['error'] = type(exc).__name__ + ': ' + str(exc)
        records.append(record)
    receipt = {'status': 'ACTUAL_FONT_PREREQUISITE_PROBE_ONLY',
               'WINDIR': os.environ.get('WINDIR'), 'QT_QPA_PLATFORM': os.environ.get('QT_QPA_PLATFORM'),
               'fonts': records, 'original_font_usable': bool(records[0]['families']),
               'project_tests_run': 0, 'native_windows_integration_verified': False}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x', encoding='utf-8') as output:
        json.dump(receipt, output, ensure_ascii=False, indent=2)
        output.write('\n')
    print(json.dumps(receipt, ensure_ascii=False))
    return 0 if receipt['original_font_usable'] else 1


if __name__ == '__main__':
    sys.exit(main())
