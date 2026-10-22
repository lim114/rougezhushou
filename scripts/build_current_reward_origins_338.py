"""Build only from existing complete, pinned event readers; no network or private state."""
from pathlib import Path
from hashlib import sha256
import argparse, json, sys
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from rouge import current_reward_origins as model

def encoded(value): return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf8')
def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--check', action='store_true'); args = parser.parse_args()
    packets = {k: p.packet() for k, p in model.PROVIDERS.items()}
    if any(v is None for v in packets.values()): raise ValueError('Existing complete sources unavailable')
    rows = model.source_rows(packets)
    notes = {'schema': 'current_reward_origins_338_sources_v1', 'new_download': False,
             'method': '完整复用333/335/336固定国服原件与所选文献段落，严格使用各阅读器已核对的奖励字段。不是新调查完整物品池。',
             'complete_acquisition_pool': False, 'actual_server_verified': False,
             'excluded_roles': ['持有笼控器的条件', '消耗源私钥', '前往或标记应急助力', '单独物品提示图标'],
             'providers': {k: {'manifest': p.MANIFEST, 'manifest_sha256': p.MANIFEST_SHA256} for k, p in model.PROVIDERS.items()}}
    output = {model.DATA: encoded({'schema': 'current_reward_origins_338_v1', 'game_commit': model.version.NEW_COMMIT,
                                  'rows': rows, 'complete_acquisition_pool': False}),
              'research/p3-current-reward-origins-338/source-notes.json': encoded(notes)}
    names = set(output) | {p.DATA for p in model.PROVIDERS.values()} | {p.MANIFEST for p in model.PROVIDERS.values()}
    files = {}
    for name in sorted(names):
        content = output[name] if name in output else (ROOT / name).read_bytes()
        files[name] = {'bytes': len(content), 'sha256': sha256(content).hexdigest()}
    output[model.MANIFEST] = encoded({'schema': 'current_reward_origins_338_manifest_v1', 'files': files})
    digest = sha256(output[model.MANIFEST]).hexdigest()
    for name, raw in output.items():
        path = ROOT / name
        if args.check:
            if path.read_bytes() != raw: raise ValueError('Build differs: ' + name)
        else: path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(raw)
    if args.check and model.MANIFEST_SHA256 != digest: raise ValueError('Runtime manifest binding differs')
    print(json.dumps({'source_checked': True, 'check_only': args.check, 'rows': len(rows),
                      'items': len({r['item_id'] for r in rows}), 'manifest_sha256': digest}, ensure_ascii=False))
if __name__ == '__main__': main()
