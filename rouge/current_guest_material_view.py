"""Exact material source and title for the shared guest-boss reader."""
from . import current_guest_material as model
from .guest_mechanism_view import GuestMechanismPanel, GuestMechanismDialog


class CurrentGuestMaterialPanel(GuestMechanismPanel):
    model = model


class CurrentGuestMaterialDialog(GuestMechanismDialog):
    title = '“物欲拮抗者” · 指令、屏障与斯第奇'
    panel_type = CurrentGuestMaterialPanel
