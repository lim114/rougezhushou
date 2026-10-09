"""Independent public capability controls only; Root records actual primary."""
import argparse
import json
import sys
from pathlib import Path
from suite_common100 import fresh_capability, require, workspace_evidence_path, write_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--wine', action='store_true')
    args = parser.parse_args()
    args.out = workspace_evidence_path(str(args.out))
    require(not args.out.exists(), 'Fresh exclusive probe output required')
    value = fresh_capability(args.wine)
    write_json(args.out, value)
    print(json.dumps({'passed': value['passed'], 'admission_mode': value['admission_mode'],
                      'project_calls': 0, 'native_windows_integration_verified': False}, ensure_ascii=False))
    return 0 if value['passed'] else 1


if __name__ == '__main__':
    sys.exit(main())
