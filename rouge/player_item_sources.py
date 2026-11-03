"""Exact item-to-pool lookup over licensed, local public references."""
from . import public_archive as archive
from .expansion_reference import _plain
from datetime import datetime,timezone,timedelta

VERSION_LABELS = {'base': '本体资料', 'dlc1': '内容拓展一资料'}

def pool_label(pool):
    nodes = list(dict.fromkeys(b['nodeName'] for b in pool.get('nodeBindings', []) if b.get('nodeName')))
    return pool['name'] + (' · ' + '、'.join(nodes) if nodes else '')

class ItemSourceIndex:
    def __init__(self, data):
        self.data = archive.validate(data)
        self.by_item = {}
        for version, pools in data['versions'].items():
            for pool in pools:
                for identity in dict.fromkeys(pool['collectibles']):
                    self.by_item.setdefault((version, identity), []).append(pool)

    def pools(self, version, identity):
        return list(self.by_item.get((version, identity), []))

    def describe(self, version, identity, pool_id):
        pool = next((p for p in self.pools(version, identity) if p['id'] == pool_id), None)
        if pool is None:
            return '所选资料已不可用；没有沿用其他同名物品或其他资料范围。'
        lines = [pool_label(pool), '资料范围：' + VERSION_LABELS.get(version, '来源范围 ' + version)]
        if pool['name'].startswith('失与得：') and pool['name'].endswith('输入'):
            lines += ['用途：交换时可提供的物品集合；不是交换奖励池。']
        else:
            lines += ['用途：该资料集合列有此物品；仍需满足来源、解锁和领取条件。']
        if pool.get('description'):lines.append('来源条件：' + _plain(pool['description']))
        for ref in pool.get('sourceReferences', []):
            if ref.get('description'):lines.append(_plain(ref['description']).replace('drop_extra_pool','额外收藏品掉落'))
        channels = list(dict.fromkeys(c['sourceName'] for c in pool.get('usageChannels', []) if c.get('sourceName')))
        if channels:lines.append('关联来源：' + '、'.join(channels))
        found = False
        for number, (_, label, distribution) in enumerate(archive.distributions(pool),1):
            if label.startswith('自动战斗'):label='自动战斗样本 ' + str(number)
            member = next(r for r in archive.members(self.data, pool, distribution,version=version) if r['id'] == identity)
            scope = _plain(distribution.get('scopeLabel') or '来源未说明统计条件')
            rate = f"{member['rate']:.2%}（{member['count']} / {member['total']}次候选出现）" if member['rate'] is not None else '未知（没有可核对的次数与分母）'
            lines += ['', label + '：' + rate, '统计条件：' + scope]
            if distribution.get('updatedAt'):
                try:
                    updated=datetime.fromisoformat(distribution['updatedAt'].replace('Z','+00:00'))
                    if updated.tzinfo is None:raise ValueError('Missing source timezone')
                    time=updated.astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M（北京时间）')
                except(ValueError,TypeError,AttributeError):time='来源未提供可核对的时间'
                lines.append('来源更新时间：' + time)
            found = True
        if not found:lines += ['', '候选出现频率：暂无可核对的统计。']
        lines += ['', '以上频率不是抽取权重，也不是本局最终获得概率；不同来源可能重叠，不相加。', '当前版本是否完整适用仍待核验；藏品池成员不代表本局已解锁、可选或必掉。']
        return '\n'.join(lines)
