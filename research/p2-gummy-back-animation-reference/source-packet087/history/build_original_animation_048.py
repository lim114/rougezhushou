"""Build public original-animation references without binding client mechanics.

Input: pinned resource skeletons parsed by the cached upstream Spine reader.
Every event is retained; selectable records are a conservative subset. This
script never reads application settings, cultivation state or current-run data.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

FPS = 30
COMMIT = 'd0b5af0b004b044d322397ce5ae79632b6d9fcdd'
EPSILON_FRAMES = 1e-5  # representation tolerance, not a gameplay/tick tolerance


def frames(seconds):
    value = float(seconds) * FPS
    normalized = round(value) if abs(value - round(value)) <= EPSILON_FRAMES else value
    return {
        'seconds': float(seconds),
        'raw_frames_30hz': value,
        'strict_ceil_frames_30hz': math.ceil(value),
        'representation_normalized_frames_30hz': normalized,
        'ceil_frames_30hz': math.ceil(normalized),
    }


def build(catalog, extracted, downloads, cache):
    indexed = {item['file']: item for item in downloads}
    output = {
        'version': '0.48.0', 'fps': FPS, 'source_commit': COMMIT,
        'frame_normalization_tolerance': EPSILON_FRAMES,
        'binding_status': 'explicit_offline_reference_only',
        'default_numeric_behavior_changed': False,
        'scope': 'Original skins only. No measured skill reset, projectile, '
                 'multi-hit, phase or runtime animation-selector binding.',
        'operators': {},
    }
    for operator, profile in catalog['operators'].items():
        cid = profile['id']
        records = []
        missing = []
        for face in ('Front', 'Back'):
            file = f'{cid}-{face}.skel'
            item = indexed.get(file)
            data = extracted.get(file)
            if not item or not data or data.get('error'):
                missing.append({'orientation': face,
                                'reason': data.get('error') if data else 'not extracted'})
                continue
            path = cache / file
            binary = path.read_bytes()
            digest = hashlib.sha256(binary).hexdigest()
            blob = hashlib.sha1(b'blob ' + str(len(binary)).encode() + b'\0' + binary).hexdigest()
            if digest != item['sha256'] or blob != item['git_blob']:
                raise ValueError('Source skeleton hash mismatch: ' + file)
            for animation, values in data['animations'].items():
                events = [{'name': event['name'], **frames(event['time_seconds'])}
                          for event in values.get('events', [])]
                duration = frames(values['duration_seconds'])
                on_attack = [e for e in events if e['name'] == 'OnAttack']
                reasons = []
                if len(on_attack) != 1:
                    reasons.append('not exactly one OnAttack event')
                elif not 0 < on_attack[0]['seconds'] < duration['seconds']:
                    reasons.append('OnAttack must be strictly inside positive animation duration')
                if not ('Attack' in animation or animation.startswith('Skill')):
                    reasons.append('not a named attack or skill animation')
                if 'Loop' in animation:
                    reasons.append('loop named animation requires separate lifecycle binding')
                if 'Begin' in animation or 'End' in animation or 'Restart' in animation:
                    reasons.append('transition animation requires separate lifecycle binding')
                # Other events are retained, but their sequence can change the
                # effect lifecycle and must not be silently discarded.
                if len(events) != 1:
                    reasons.append('multiple or absent named events require separate binding')
                eligible = not reasons
                record = {
                    'id': f'{cid}:{face}:{animation}', 'orientation': face,
                    'skin': 'original', 'animation': animation,
                    'spine_version': data['spine_version'],
                    'duration': duration, 'events': events,
                    'selectable_as_conventional_reference': eligible,
                    'unverified_reasons': reasons,
                    'runtime_binding_verified': False,
                    'source': {'url': item['url'], 'sha256': digest,
                               'git_blob': blob, 'bytes': len(binary)},
                }
                if eligible:
                    windup = on_attack[0]['ceil_frames_30hz']
                    total = duration['ceil_frames_30hz']
                    record['preview'] = {
                        'windup_frames': windup, 'recovery_frames': total - windup,
                        'animation_frames': total,
                    }
                records.append(record)
        output['operators'][operator] = {
            'id': cid, 'name': profile['name'], 'records': records,
            'missing_sources': missing,
        }
    output['counts'] = {
        'operators': len(output['operators']),
        'source_skeletons': len(indexed),
        'animations': sum(len(p['records']) for p in output['operators'].values()),
        'selectable_references': sum(r['selectable_as_conventional_reference']
                                    for p in output['operators'].values() for r in p['records']),
        'unverified_or_transition_references': sum(not r['selectable_as_conventional_reference']
                                                  for p in output['operators'].values() for r in p['records']),
        'missing_skeletons': sum(len(p['missing_sources']) for p in output['operators'].values()),
    }
    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cache', type=Path, default=Path('.cache/research/timing-048'))
    parser.add_argument('--catalog', type=Path, default=Path('rouge/data/catalog.json'))
    parser.add_argument('--output', type=Path,
                        default=Path('.cache/research/timing-048/original-animation-references.json'))
    args = parser.parse_args()
    read = lambda path: json.loads(path.read_text(encoding='utf-8'))
    output = build(read(args.catalog), read(args.cache/'extracted-animation-events.json'),
                   read(args.cache/'skeleton-downloads.json'), args.cache)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(output['counts']))


if __name__ == '__main__':
    main()
