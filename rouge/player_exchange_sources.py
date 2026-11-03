"""Explicit source-described exchange input/output sets; never actual rewards."""
from copy import deepcopy
from . import public_archive

def _node_description(pool, text):
    return any(isinstance(row, dict) and row.get('sourceType') == 'node'
               and row.get('sourceIds') == ['SACRIFICE'] and row.get('description') == text
               for row in pool.get('sourceReferences', []))

def exchange_links(data, version, identity):
    """Pair only exact IDs, kinds, rarity labels AND explicit descriptions.

    Same name, same rarity or canSacrifice alone never establishes a reward pool.
    The source snapshot's conditions/version remain attached to each link.
    """
    public_archive.validate(data)
    if version not in data['versions']:
        return []
    pools = {pool['id']: pool for pool in data['versions'][version]}
    result = []
    for rarity in ('N', 'R', 'SR'):
        for kind, output_word in [('藏品', '收藏品'), ('零件', '零件')]:
            prefix = '失与得：' + rarity + kind
            source = pools.get('rogue_6:' + prefix + '输入')
            target = pools.get('rogue_6:' + prefix + '输出')
            if not source or not target or identity not in source['collectibles']:
                continue
            if source['name'] != prefix + '输入' or target['name'] != prefix + '输出':
                continue
            if not _node_description(source, f'可投入失与得节点的 {rarity} {kind}集合。'):
                continue
            if not _node_description(target, f'投入 {rarity} {kind}后的{output_word}输出集合；成员与频次来自人工观测。'):
                continue
            result.append({'version': version, 'input_id': source['id'], 'output_id': target['id'],
                           'input_name': source['name'], 'output_name': target['name'],
                           'kind': kind, 'rarity': rarity,
                           'input_sources': deepcopy(source['sourceReferences']),
                           'output_sources': deepcopy(target['sourceReferences']),
                           'members': public_archive.members(data, target),
                           'actual_eligible': None, 'actual_reward': None,
                           'complete_current_version_pool': None})
    return result

def exchange_label(link):
    rarity={'N':'低稀有度','R':'中稀有度','SR':'高稀有度'}.get(link['rarity'],'来源未分档')
    return '交出'+rarity+('收藏品'if link['kind']=='藏品'else'零件')+' → 查看换入候选'

def exchange_text(link):
    labels = {'base': '本体资料', 'dlc1': '内容拓展一资料'}
    return '\n'.join([
        exchange_label(link),
        '资料范围：' + labels.get(link['version'], '来源中的独立范围'),
        f'来源记录过{len(link["members"])}种可能换入的物品。',
        '对应关系来自资料对交出物品及换入物品的明确说明，不是按同名或稀有度猜测。',
        '', '可以查看该范围记录过哪些候选；不能据此认定本次能交出、会获得哪件或发放多少件。',
        '这些集合不表示当前DLC的完整奖励池，也不表示平均分配或抽取权重。',
        '本局持有、解锁、选项条件和实际领取仍需各自证据；不扣除或添加任何本局物品。'])
