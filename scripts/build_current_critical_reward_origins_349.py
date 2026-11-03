"""Build three explicit grant links from existing version-bound sources."""
from pathlib import Path
from hashlib import sha256
import argparse, json, sys
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from rouge import current_critical_reward_origins as model

def enc(value): return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf8')

def build():
    packets = [p.packet() for p in model.PROVIDERS]
    if any(p is None for p in packets): raise ValueError('All exact current readers required')
    current = model.version.packet()
    rows = model.source_rows(current['current']['details'], *packets)
    notes = {'section': 349, 'game_commit': model.version.NEW_COMMIT,
             'sources': [{'manifest': p.MANIFEST, 'manifest_sha256': p.MANIFEST_SHA256} for p in model.PROVIDERS],
             'new_capability': 'Three explicit item grants accessible from item pages with specialized condition comparison and exact existing flow entry. Old338/347 unchanged.',
             'web_crosscheck': 'https://prts.wiki/w/沉沦者的黑流树海',
             'web_establishes': '10源石锭取得谒日之祈、首次倒下后的一次救援取得破碎噩兆、制图桌可选生命蓝图，与固定316/321/339原记录核对。文献不是当前服务器执行证明。',
             'binding': '原项明确获得收藏品及独立itemId；没有字面藏品名，不要求模糊名称补配。',
             'unknown': ['完整出现前置和当前服务器资格', '独立领取件数', '一半生命上限的整数处理', '真实领取、扣费及生效', '全部其它取得来源和完整掉落池'],
             'new_mechanics_or_calculation': False, 'new_HTML_or_image_download': False,
             'actual_game_or_chat_operated': False}
    out = {model.DATA: enc({'schema': 'critical_reward_origins_349_v1', 'game_commit': model.version.NEW_COMMIT,
                           'rows': rows, 'complete_acquisition_pool': False}), model.PACK + '/source-notes.json': enc(notes)}
    names = set(out) | {p.DATA for p in model.PROVIDERS} | {p.MANIFEST for p in model.PROVIDERS}
    files = {}
    for name in sorted(names):
        raw = out[name] if name in out else (ROOT / name).read_bytes()
        files[name] = {'bytes': len(raw), 'sha256': sha256(raw).hexdigest()}
    out[model.MANIFEST] = enc({'schema': 'critical_reward_origins_349_manifest_v1',
                              'game_commit': model.version.NEW_COMMIT, 'files': files})
    return out

if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--check', action='store_true'); args = parser.parse_args()
    out = build()
    for name, raw in out.items():
        path = ROOT / name
        if args.check:
            if path.read_bytes() != raw: raise ValueError('Build differs: ' + name)
        else: path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(raw)
    digest = sha256(out[model.MANIFEST]).hexdigest()
    if args.check and digest != model.MANIFEST_SHA256: raise ValueError('Runtime manifest differs')
    print(json.dumps({'grant_choices': 3, 'items': 3, 'manifest_sha256': digest}))
