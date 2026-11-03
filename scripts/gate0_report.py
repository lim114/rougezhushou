"""Summarize local instrumentation; accuracy requires independently labelled video."""
from collections import Counter
import argparse
import json
import math
from pathlib import Path


def percentile(values, fraction):
    return sorted(values)[max(0, math.ceil(len(values)*fraction)-1)] if values else None


def summarize(folder):
    rows = [json.loads(line) for line in (folder/'events.jsonl').read_text('utf8').splitlines()]
    samples = [row for row in rows if row['event']=='sample']
    overlays = [row for row in rows if row['event']=='overlay']
    surfaces = [row for row in rows if row['event']=='surfaces']
    timings = [row['performance']['total_ms'] for row in samples if 'total_ms' in row['performance']]
    failures = Counter(row['reason'] for row in rows if row['event']=='sample_failure')
    result = {
        'schema': 'gate0_scorecard_v1', 'scope': 'local_session_observations',
        'scenario': rows[0]['scenario'], 'ended': rows[-1]['event']=='session_end',
        'duration_s': (rows[-1]['t_ms']-rows[0]['t_ms'])/1000,
        'samples': len(samples), 'pages': dict(Counter(row['page'] for row in samples)),
        'applied_samples': sum(row['applied'] for row in samples),
        'recognition_ms': {'median': percentile(timings,.5), 'p95': percentile(timings,.95), 'n':len(timings)},
        'sample_failures': dict(failures),
        'overlay_observations': len(overlays),
        'overlay_reasons': dict(Counter(row['reason'] for row in overlays)),
        'peak_visible_surfaces': max((len(row['visible']) for row in surfaces), default=0),
        'surface_changes':len(surfaces),
        'independent_video_review': 'pending', 'page_accuracy': None, 'wrong_map_or_node': None,
        'gate0_passed': False,
    }
    (folder/'scorecard.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf8')
    text = f"# 会话记录\n\n场景：{result['scenario']}；时长：{result['duration_s']:.1f}秒；采样：{len(samples)}次。\n\n"
    text += f"页面记录：{result['pages']}\n\n识别耗时（毫秒）：{result['recognition_ms']}\n\n"
    text += f"可见界面峰值：{result['peak_visible_surfaces']}；界面变化记录：{len(surfaces)}次。\n\n"
    text += f"采样失败：{dict(failures)}\n\n叠加判定记录：{result['overlay_reasons']}\n\n"
    text += '录像对照：待核对。页面准确率、误标、漏显和更新延迟在对照后填写。上述判定次数是日志观察，不自动列为故障。\n'
    (folder/'scorecard.md').write_text(text,'utf8')
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description='生成本地Gate 0会话摘要')
    parser.add_argument('folder',type=Path)
    args=parser.parse_args()
    print(json.dumps(summarize(args.folder),ensure_ascii=False,indent=2))
