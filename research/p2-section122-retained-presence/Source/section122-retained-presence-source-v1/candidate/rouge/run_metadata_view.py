"""Display current-run recipient metadata without inventing unknown names.

The raw persisted evidence and the numerical API stay authoritative. Unknown
IDs remain in the caller so calculation keeps its existing explicit error.
"""

from .record_flags import record_flag,active_record,metadata_mask,projected_run_metadata,RECIPIENT_KEYS


def format_run_buff_status(state, buffs):
    """Keep existing healthy labels and mark unrecognized displayed IDs unusable.

    The saved-shape and current-run gates already qualify consumed ID lists.
    This is a display consumer, not a new recipient schema or repair.
    """
    if state.get('scope')=='run' and record_flag(state,'present') is None:
        return '本局记录的在场状态未确认；原强化记录保留，暂不自动套用。'
    qualified=projected_run_metadata(state)
    if (state.get('scope')=='run' and active_record(state,'present')
            and metadata_mask(state).intersection(RECIPIENT_KEYS) and not qualified.get('char_buff_ids')):
        return '保留的个人强化资格尚未重新确认；原记录保留，暂不自动套用。'
    retained=metadata_mask(state).intersection(RECIPIENT_KEYS)
    state=qualified
    current = state.get('scope') == 'run' and active_record(state,'present')
    ids = state.get('char_buff_ids', []) if current else []
    pending = state.get('char_buff_pending_ids', []) if current else []
    unknown = [bid for bid in ids + pending if bid not in buffs]
    if unknown:
        return ('个人强化记录含无法识别的条目：' + '、'.join(unknown) +
                '；暂不可确认该记录，请重新读取强化列表。')
    names = '、'.join(buffs[bid]['name'] for bid in ids)
    text = (names if ids else '已核对：无个人强化'
            if current and state.get('char_buffs_complete') is True else
            '个人强化归属尚未确认；不会根据持有藏品推断')
    if pending:
        text = (('已确认：' + names + '；' if ids else '') +
                '、'.join(buffs[bid]['name'] for bid in pending) +
                '归属待更新：本局藏品或进阶情况已变化，旧的未领取结论已失效。')
    if current and retained:text+='；其他保留的个人强化资格尚未重新确认。'
    return text
