"""Player wording for declared map-cell labels, without placement prediction."""
import json

TERRAIN = {'tile_floor': '地面地块', 'tile_road': '道路', 'tile_wall': '高台地块',
           'tile_start': '敌人入口', 'tile_end': '保护目标'}
HEIGHT = {'LOWLAND': '地面', 'HIGHLAND': '高台'}
BUILDABLE = {'NONE': '不可部署', 'MELEE': '近战位', 'RANGED': '远程位', 'ALL': '全部类型'}
PASSABLE = {'ALL': '全部类型', 'FLY_ONLY': '仅飞行'}


def tile_information_text(cell, tile, *, mapped=False, technical=False):
    """Translate explicit labels only; no inference about units or battle state."""
    if (not isinstance(cell, dict) or not isinstance(tile, dict)
            or any(type(cell.get(key)) is not int or cell[key] < 0 for key in ('row', 'col'))):
        return '尚未选择有效地图格子；无法确认地形或对应图片位置。'
    def label(names, key, unknown):
        value = tile.get(key)
        return names.get(value, unknown) if isinstance(value, str) else unknown
    lines = [f"格图第{cell['row'] + 1}行、第{cell['col'] + 1}列",
             '地形：' + label(TERRAIN, 'tileKey', '名称尚未整理'),
             '位置高度：' + label(HEIGHT, 'heightType', '尚未确认'),
             '地块部署标记：' + label(BUILDABLE, 'buildableType', '尚未整理'),
             '地块通行标记：' + label(PASSABLE, 'passableMask', '尚未整理'),
             '这些是固定地图的地块标记，不包含战斗中的变化或其他特殊限制。',
             '当前筛选下未找到从本格出场的敌人资料；不等于本局一定没有敌人经过。',
             ('固定原图：已标出本格近似中心。' if mapped else '固定原图：本格位置尚未核对。')]
    if technical:
        lines.extend(['', '【原始地块资料】', json.dumps(tile, ensure_ascii=False, indent=2)])
    return '\n'.join(lines)
