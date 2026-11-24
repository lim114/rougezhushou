"""Measure a map replay from visible source frames to the witnessed assistant window.

The fixture supplies source paint times in perf_counter seconds and the first
correct window capture in milliseconds relative to first_paint. Choose the
onset and clear frames by inspecting the source recording independently.
"""
import argparse
import json
from pathlib import Path


def measure(shown, first_paint, window_pixels_ms, onset_frame, clear_frame):
    if not 0 <= onset_frame <= clear_frame:
        raise ValueError('转场起点必须早于或等于清晰帧。')
    if not shown or any(i >= j or t > u for (i, t), (j, u) in zip(shown, shown[1:])):
        raise ValueError('需要按实际绘制顺序记录的源帧和时间。')
    if shown[0][0] >= onset_frame:
        raise ValueError('缺少转场前已显示的源帧。')
    visible = {}
    for label, frame in [('onset', onset_frame), ('clear', clear_frame)]:
        first = next(((i, t) for i, t in shown if i >= frame), None)
        if first is None:
            raise ValueError(f'源窗口尚未显示第 {frame} 帧。')
        index, timestamp = first
        elapsed = window_pixels_ms - (timestamp - first_paint) * 1000
        if label == 'onset' and elapsed < 0:
            raise ValueError('目标窗口证据早于源窗口转场。')
        visible[f'{label}_shown_frame'] = index
        visible[f'{label}_to_window_ms'] = round(elapsed, 2)
    return visible


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('shown', type=Path, help='源窗口实际绘制的帧序号和单调时钟列表')
    parser.add_argument('source', type=Path, help='回放夹具的源窗口时钟记录')
    parser.add_argument('witness', type=Path, help='已核验正确内容的助手窗口像素时钟记录')
    parser.add_argument('--onset-frame', type=int, required=True)
    parser.add_argument('--clear-frame', type=int, required=True)
    args = parser.parse_args()
    shown = json.loads(args.shown.read_bytes())
    source = json.loads(args.source.read_bytes())[1]
    witness = json.loads(args.witness.read_bytes())
    result = measure(shown, source['first_paint'], witness['window_pixels_ms'],
                     args.onset_frame, args.clear_frame)
    print(json.dumps(result))


if __name__ == '__main__':
    main()
