"""Exact knights source and title for the shared guest-boss reader."""
from . import current_guest_knights as model
from .guest_mechanism_view import GuestMechanismPanel, GuestMechanismDialog


class CurrentGuestKnightsPanel(GuestMechanismPanel):
    model = model

    def _technical_extra(self, row, topic):
        return {
            'documentation_limits_original': self.result['data']['limits'],
            'complete_original_enemy_database': self.result['data']['originals']['enemy_definitions'].get(row['entity_id']) if row else None,
            'timing_interpretation_note': '原始ChargeAttack黑板duration=4仅是原参数；未证明完整蓄力或命中相位，不换算成4秒蓄力或技能周期。原编目topic_text中固定数据另记蓄力4秒的解释已撤出默认说明，原件留存供审计。',
        }


class CurrentGuestKnightsDialog(GuestMechanismDialog):
    title = '恶意讨薪 · 双骑士联动与完整招式'
    panel_type = CurrentGuestKnightsPanel
