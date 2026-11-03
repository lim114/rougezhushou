"""Measure the installed Windows Python/Wine symlink fixture capability only."""
import json
import os
import platform
import stat
import tempfile
from pathlib import Path

observations = []
with tempfile.TemporaryDirectory(prefix='public-symlink-capability-095-') as folder:
    base = Path(folder)
    for present in (False, True):
        target = base / ('present-target.json' if present else 'absent-target.json')
        if present:
            target.write_bytes(b'{"public_probe":true}')
        link = base / ('present-link.json' if present else 'absent-link.json')
        row = {'target_present': present, 'link': str(link), 'target': str(target)}
        try:
            returned = os.symlink(target, link)
            row['creation'] = {'returned_type': type(returned).__name__, 'returned_repr': repr(returned)}
        except (OSError, NotImplementedError) as exc:
            row['creation'] = {'error_type': type(exc).__name__, 'error': str(exc), 'winerror': getattr(exc, 'winerror', None)}
        row['is_symlink'] = link.is_symlink()
        row['exists'] = link.exists()
        for operation in ('lstat', 'readlink', 'read_bytes'):
            try:
                result = getattr(link, operation)()
                if operation == 'lstat':
                    result = {'mode': result.st_mode, 'is_link_mode': stat.S_ISLNK(result.st_mode),
                              'file_attributes': getattr(result, 'st_file_attributes', None),
                              'reparse_tag': getattr(result, 'st_reparse_tag', None)}
                elif operation == 'read_bytes':
                    result = {'bytes_hex': result.hex()}
                else:
                    result = str(result)
                row[operation] = {'result': result}
            except OSError as exc:
                row[operation] = {'error_type': type(exc).__name__, 'error': str(exc), 'winerror': getattr(exc, 'winerror', None)}
        row['actual_directory_entries'] = sorted(p.name for p in base.iterdir())
        row['target_bytes_unchanged'] = (target.read_bytes() == b'{"public_probe":true}') if present else not target.exists()
        observations.append(row)
print(json.dumps({'platform': platform.system(), 'python': platform.python_version(),
                  'project_imports': 0, 'private_state_access': False, 'observations': observations}, indent=2))
