"""Fresh-read explicit legacy local/public byte pairs, never execute them."""
import json
from pathlib import Path
from full305_common import BASE, public, sha, write_new, input_bindings


def main():
    guard = json.loads((BASE / 'template-legacy/current-source-guard.json').read_bytes())
    archives = {
        'verification/full-290/legacy-retry-attempt4/archive-manifest.json': 'f307d8b47ea246c0983853b78b60cbd14246f68c0766b688d64cf242aaac5929',
        'verification/full-290/execution-attempt2/archive-manifest.json': '4c8b281bbaccc955636f95ef6d2ff461427c07107237e58ef732457adc0640aa'}
    by_hash = {}
    for name, expected in archives.items():
        path = public(name)
        if sha(path) != expected: raise ValueError('Exact captured archive changed.')
        for member, pin in json.loads(path.read_bytes())['files'].items():
            by_hash.setdefault(pin['sha256'], []).append((Path(name).parent / member).as_posix())
    bindings = []
    for name, expected in guard['source_additional_sha256'].items():
        if not name.startswith('.cache/'): continue
        candidates = [value for value in by_hash.get(expected, []) if Path(value).name == Path(name).name]
        if not candidates: raise ValueError('No exact original public byte counterpart: ' + name)
        selected = sorted(candidates, key=lambda value: ('executed-legacy-bundle/' not in value, len(value), value))[0]
        bindings.append({'local_path': name, 'public_path': selected, 'sha256': expected, 'bytes': public(selected).stat().st_size})
    observed = input_bindings(bindings)
    value = {'section': 305, 'kind': 'READ_ONLY_EXPLICIT_LEGACY_LOCAL_PUBLIC_COUNTERPART_PREFLIGHT_NOT_EXECUTION',
             'bindings': bindings, 'actual_verified_pairs': len(observed), 'fixed_capture_manifests': archives,
             'old_additional_scope': len(guard['source_additional_sha256']), 'sourcefreeze_or_runtime_started': False}
    write_new(BASE / 'legacy-local-public-counterpart-preflight.json', value)
    print(json.dumps({'verified_exact_legacy_local_public_pairs': len(observed), 'old_additional_scope': value['old_additional_scope'],
                      'actual_GUI_test_or_freeze_started': False}))


if __name__ == '__main__': main()
