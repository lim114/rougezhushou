"""Read the two pinned visible-marker packages with their declared identities."""
from hashlib import sha256
from pathlib import PurePosixPath
import json


def load_marker_packet(root, manifest_path, manifest_digest, data_path, expected_files,
                       manifest_schema, data_schema, game_commit, stages):
    try:
        raw = (root / manifest_path).read_bytes()
        if sha256(raw).hexdigest() != manifest_digest:
            return None
        manifest = json.loads(raw)
        if (manifest['schema'] != manifest_schema or manifest['game_commit'] != game_commit
                or set(manifest['files']) != expected_files):
            return None
        data = None
        resolved_root = root.resolve()
        for name, pin in manifest['files'].items():
            relative = PurePosixPath(name)
            if relative.is_absolute() or '..' in relative.parts or '\\' in name or ':' in name:
                return None
            path = root.joinpath(*relative.parts)
            if path.is_symlink() or not path.resolve().is_relative_to(resolved_root):
                return None
            for parent in path.parents:
                if parent == root:
                    break
                if parent.is_symlink():
                    return None
            raw = path.read_bytes()
            if len(raw) != pin['bytes'] or sha256(raw).hexdigest() != pin['sha256']:
                return None
            if name == data_path:
                data = json.loads(raw)
        if data is None or data['schema'] != data_schema or tuple(data['bindings']) != stages:
            return None
        return {'data': data, 'source_identity': manifest_digest}
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None
