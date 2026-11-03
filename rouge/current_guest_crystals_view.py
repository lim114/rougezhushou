"""Exact crystals source and title for the shared guest-boss reader."""
from . import current_guest_crystals as model
from .guest_mechanism_view import GuestMechanismPanel, GuestMechanismDialog


class CurrentGuestCrystalsPanel(GuestMechanismPanel):
    model = model


class CurrentGuestCrystalsDialog(GuestMechanismDialog):
    title = '晶矿惊蝗 · 双晶兽的护盾与捕杀'
    panel_type = CurrentGuestCrystalsPanel
