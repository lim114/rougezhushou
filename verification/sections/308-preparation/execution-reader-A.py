"""Seal first independent manual readings; no fit, peer input, or acceptance calculation."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
INPUT = ROOT / '.cache/p3-308-reader-inputs'

# Coordinates below are first manual readings from source PNG pixels, not a projection.
READINGS = {
    'ro6_n_5_1': [
        (1, 9, (359, 76), '右上蓝色终点左侧绿地；可见上、下横缝及两侧边界。'),
        (2, 1, (124, 96), '左上道路窄绿面，右邻浅色墙顶之前；中心露出。'),
        (2, 2, (154, 95), '左侧纵向浅色墙顶后方的绿地顶面；左右地面边可辨。'),
        (2, 3, None, '金色树根和装置遮住中心，不能把遮挡物表面当作低地中心。'),
        (2, 5, (244, 96), '中间纵向白色墙顶后方露出的绿地；横缝与两侧边可辨。'),
        (2, 6, None, '树根及箭头装置覆盖中心，低地中心不能直接读清。'),
        (2, 7, None, '金色枝根与装置覆盖该道路中部，不能独立确定低地中心。'),
        (2, 9, (360, 96), '右侧纵向高墙左侧的绿色道路面；四边有连续缝线。'),
        (3, 1, (123, 120), '左侧长白墙左边的草地道路，横向接缝上下可见。'),
        (3, 3, None, '栅栏前景金色枝条盖住道路中心，不能用相邻格补算。'),
        (3, 5, (244, 120), '中央白墙左边绿地道路，横缝与竖缝可直接辨认。'),
        (3, 7, (304, 120), '中央白墙右边、金色装置左边的露出绿面。'),
        (3, 9, (364, 121), '右侧长墙左边露出的道路绿面，上下缝线可见。'),
        (4, 1, (120, 143), '左侧长白墙下半部左侧的道路格，底缝在下一排之前。'),
        (4, 3, None, '金色枝条及栅栏覆盖格中部，裸露边缘不足以确认中心。'),
        (4, 4, None, '低地地板中心被栅栏/根状物完全挡住；不借墙顶或邻格。'),
        (4, 5, (242, 143), '中央白墙左侧下方绿面，前方横墙上沿之前可见。'),
        (4, 7, (305, 143), '中央白墙右侧下方绿面，右侧枝根没有遮住所读中心。'),
        (4, 8, None, '右侧栅栏装置与枝根遮挡地板中心，无法直接读数。'),
        (4, 9, (365, 144), '右侧长墙左边下方绿面，前景黑色结构上方仍可见中心。'),
        (5, 1, (116, 168), '左侧蓝色终点右边的道路格，左右边与下横缝可见。'),
        (5, 2, (148, 168), '左侧蓝色终点与前方浅色横墙之间的第二个绿地格。'),
        (6, 2, (146, 199), '底部连续金属纹草地带最左格，紧邻左侧浅色墙。'),
        (6, 3, (180, 199), '底部第二个连续金属纹格，竖框及上下边清楚。'),
        (6, 4, (213, 199), '底部第三个连续金属纹格，直接按该格可见边框读中心。'),
        (6, 5, (247, 199), '底部第四个连续金属纹格，竖框及上下边清楚。'),
        (6, 6, (280, 199), '底部第五个连续金属纹格，中心面完整露出。'),
        (6, 7, (314, 199), '底部第六个连续金属纹格，中心与边框完整可见。'),
        (6, 8, (348, 199), '底部红色入口左邻金属纹格，右侧框线可辨。'),
        (6, 10, (415, 199), '底部红色入口右侧的暗色金属纹格，左右框线可见。'),
    ],
    'ro6_n_5_5': [
        (1, 1, (123, 77), '左上两列金属纹地板的左上格，格框清楚。'),
        (1, 2, (148, 77), '左上两列金属纹地板的右上格，格框清楚。'),
        (1, 4, None, '蓝色终点立体标记向后覆盖该格中心，不把标记顶面当作地面。'),
        (1, 5, (229, 76), '蓝色标记右边、白色横墙左后方露出的草地格。'),
        (1, 6, (258, 75), '白色横墙后方第一格露出绿色中心，上边和列边可辨。'),
        (1, 7, (286, 75), '白色横墙后方中间格的露出草地中心。'),
        (1, 8, (315, 76), '白色横墙后方右格的露出草地中心，右侧金属纹列作边界。'),
        (1, 9, (344, 78), '右上红色入口左侧的金属纹地板格，格框可见。'),
        (1, 10, (373, 78), '右上红色入口紧左邻暗蓝色格，横向格边清楚。'),
        (2, 1, (120, 98), '左上两列金属纹地板的左下格，完整格框可见。'),
        (2, 2, (148, 98), '左上两列金属纹地板的右下格，完整格框可见。'),
        (3, 1, (116, 122), '左侧纵向道路上段，金属地板下面的绿色格。'),
        (3, 4, (197, 123), '蓝色终点下面纵向金属纹带的首格，横框与两侧边可见。'),
        (3, 7, (287, 123), '中部双排绿地的上排第一格，蓝色传送口右邻。'),
        (3, 8, (316, 123), '中部双排绿地的上排第二格，完整接缝可见。'),
        (3, 9, (345, 123), '中部双排绿地的上排第三格，完整接缝可见。'),
        (3, 10, (374, 123), '中部双排绿地的上排第四格，完整接缝可见。'),
        (3, 11, (405, 123), '中部双排绿地的上排第五格，右邻蓝色传送口。'),
        (4, 1, (110, 146), '左侧道路中段，左侧枝根没有盖住所读绿色中心。'),
        (4, 2, None, '木板堆与树根覆盖该地板中心，未使用物件顶部代替地板。'),
        (4, 4, (194, 147), '中间纵向金属纹带的第二格，完整方框可见。'),
        (4, 7, (288, 145), '中部双排绿地下排第一格，前方白色墙上沿之前露出。'),
        (4, 8, (318, 145), '中部双排绿地下排第二格，竖缝清楚。'),
        (4, 9, (348, 145), '中部双排绿地下排第三格，右邻金属纹地板。'),
        (4, 10, (379, 145), '中部下排金属纹地板，草地与右侧道路之间。'),
        (4, 11, (411, 146), '中部双排绿地下排最右道路格，蓝色传送口左侧。'),
        (5, 1, (104, 172), '左下纵向道路，浅色高墙左边的绿色格。'),
        (5, 4, (192, 173), '中间纵向金属纹带第三格，浅色横墙左边。'),
        (6, 1, (96, 199), '左下蓝色传送口上方绿色道路格，右侧立墙边界清楚。'),
        (6, 4, (188, 200), '底部蓝色传送口上方金属纹格，左右框及上下边可见。'),
        (6, 5, (222, 199), '底部横向道路首个绿色格，左邻金属纹格。'),
        (6, 6, (255, 199), '底部横向道路第二个绿色格，完整接缝可见。'),
        (6, 7, (289, 199), '底部横向道路第三个绿色格，完整接缝可见。'),
        (6, 8, (323, 199), '底部横向道路第四个绿色格，完整接缝可见。'),
        (6, 9, (357, 199), '底部横向道路第五个绿色格，右侧红色枝条未遮住中心。'),
        (6, 10, (392, 199), '底部右侧第一块金属纹地板，上下边与竖框可见。'),
        (6, 11, (426, 199), '底部红色入口左邻金属纹地板，右侧边框可见。'),
    ],
}

def pin(path: Path) -> dict:
    b = path.read_bytes()
    return {'sha256': hashlib.sha256(b).hexdigest(), 'bytes': len(b)}

def exclusive_json(name: str, value: dict) -> Path:
    p = HERE / name
    with p.open('xb') as f:
        f.write((json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))
    return p

source_pin_path = INPUT / 'SOURCE_PINS.json'
source_pins = json.loads(source_pin_path.read_text(encoding='utf-8'))
requests = json.loads((INPUT / 'REQUESTS.json').read_text(encoding='utf-8'))
for filename, expected in source_pins['files'].items():
    assert pin(INPUT / filename) == expected, filename

images = []
for group in requests['groups']:
    stage = group['stage_id']
    literal = READINGS[stage]
    expected_ids = [(r['row'], r['col']) for r in group['all_requests']]
    assert [(r, c) for r, c, _, _ in literal] == expected_ids, stage
    rows = []
    for request, (r, c, pixel, cue) in zip(group['all_requests'], literal):
        assert pixel is None or all(type(x) is int for x in pixel)
        rows.append({
            'request_id': request['request_id'], 'row': r, 'col': c,
            'tile_key': request['tile_key'], 'height_type': request['height_type'],
            'observed_pixel': list(pixel) if pixel is not None else None,
            'readable': pixel is not None,
            'cue': cue,
            'reason': 'source_surface_center_directly_read' if pixel is not None else 'source_center_occluded_or_not_independently_locatable',
        })
    images.append({
        'stage_id': stage, 'title': group['title'],
        'image_file': group['image_file'], 'grid_file': group['grid_file'],
        'image_sha256': source_pins['files'][group['image_file']]['sha256'],
        'width': group['image']['width'], 'height': group['image']['height'],
        'rows': group['rows'], 'cols': group['cols'],
        'request_count': len(rows), 'readings': rows,
    })

original = exclusive_json('READER_A_ORIGINAL.json', {
    'schema': 'section308-independent-fixed-image-readings-v1',
    'reader': 'A', 'recorded_utc': datetime.now(timezone.utc).isoformat(),
    'coordinates': 'original PNG integer x,y; zero-based raw mapData array row,col; no route row flip',
    'source_pin_manifest': {'path': '.cache/p3-308-reader-inputs/SOURCE_PINS.json', **pin(source_pin_path)},
    'source_pins': source_pins['files'],
    'independence': {
        'other_reader_coordinate_files_or_results_seen': False,
        'other_reader_freeze_notification_seen_without_reading_files': True,
        'existing_projection_matrix_or_landmark_pixels_for_these_two_images_seen': False,
        'fit_interpolation_or_extrapolation_used': False,
        'averaging_or_coordinate_adjustment_against_peer_used': False,
        'source_PNG_bytes_modified': False,
        'view_aids': 'nearest-neighbor enlargements/crops with external coordinate ticks only; no predicted or candidate points drawn',
        'formal_first_readings_sealed_before_any_comparison': True,
    },
    'images': images,
    'requested': sum(x['request_count'] for x in images),
    'readable': sum(row['readable'] for image in images for row in image['readings']),
    'null': sum(not row['readable'] for image in images for row in image['readings']),
    'acceptance_or_actual_positions_verified': False,
})
ready = exclusive_json('READY_A_ORIGINAL.json', {
    'schema': 'section308-reader-A-first-original-freeze-v1',
    'reader': 'A', 'first_original': {'path': original.relative_to(ROOT).as_posix(), **pin(original)},
    'source_pin_manifest': {'path': source_pin_path.relative_to(ROOT).as_posix(), **pin(source_pin_path)},
    'request_manifest': {'path': (INPUT / 'REQUESTS.json').relative_to(ROOT).as_posix(), **pin(INPUT / 'REQUESTS.json')},
    'producer': {'path': Path(__file__).relative_to(ROOT).as_posix(), **pin(Path(__file__))},
    'requested': sum(x['request_count'] for x in images),
    'per_image': [{'stage_id': image['stage_id'], 'requested': image['request_count'],
                   'readable': sum(r['readable'] for r in image['readings']),
                   'null': sum(not r['readable'] for r in image['readings'])} for image in images],
    'independent_before_comparison': True,
    'no_peer_results_read': True,
    'acceptance_not_computed': True,
    'production_or_Git_modified': False,
})
print(json.dumps({'ready': str(ready), 'ready_pin': pin(ready), 'original_pin': pin(original), 'requested': 67}, ensure_ascii=False))
