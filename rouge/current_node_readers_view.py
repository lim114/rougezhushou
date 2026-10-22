"""Open already verified current readers from node information, without run inputs."""
from PySide6.QtWidgets import QLabel
from . import current_node_readers as model

def make_dialog(binding,parent=None,*,historical=False):
    b=model.recheck(binding)
    if b is None:return None
    kind=b['reader'];event=b['current_event_id']
    if kind=='portal341':
        from .current_portal_view import CurrentPortalDialog
        dialog=CurrentPortalDialog(parent=parent)
    elif kind=='agency340':
        from .current_agency_view import CurrentAgencyDialog
        dialog=CurrentAgencyDialog(parent=parent)
    elif kind=='exit339':
        from .current_exit_view import CurrentExitDialog
        dialog=CurrentExitDialog(parent=parent)
    elif kind=='memory336':
        from .current_memory_tree_view import CurrentMemoryTreeDialog
        dialog=CurrentMemoryTreeDialog(parent=parent)
    elif kind=='dog335':
        from .current_lone_dog_view import CurrentLoneDogDialog
        dialog=CurrentLoneDogDialog(parent=parent)
    elif kind=='cave334':
        from .current_cave_view import CurrentCaveDialog
        dialog=CurrentCaveDialog(parent=parent)
    elif kind=='vine333':
        from .current_vine_events_view import CurrentVineEventsDialog
        dialog=CurrentVineEventsDialog(event,parent=parent)
    elif kind=='rest':
        from .current_rest_travel_view import CurrentRestTravelDialog
        dialog=CurrentRestTravelDialog(event,parent=parent)
    elif kind=='shop':
        from .current_unattended_shop_view import CurrentUnattendedShopDialog
        dialog=CurrentUnattendedShopDialog(parent=parent)
    elif kind=='resources':
        from .current_resource_events_view import CurrentResourceEventsDialog
        dialog=CurrentResourceEventsDialog(event,parent=parent)
    elif kind=='lake':
        from .current_lake_view import CurrentLakeDialog
        dialog=CurrentLakeDialog(parent=parent)
    elif kind=='encounters':
        from .current_encounters_view import CurrentEncountersDialog
        dialog=CurrentEncountersDialog(event,parent=parent)
    elif kind=='sand':
        from .current_sand_view import CurrentSandDialog
        dialog=CurrentSandDialog(event,parent=parent)
    elif kind=='ritual':
        from .current_ritual_view import CurrentRitualDialog
        dialog=CurrentRitualDialog(event,parent=parent)
    elif kind=='box':
        from .box_event_view import BoxEventDialog
        dialog=BoxEventDialog(parent=parent)
    else:return None
    if not model.matches_current(b,dialog.panel.result):dialog.close();return None
    banner=QLabel(('从历史节点打开的资料参考。'if historical else'从节点目录打开的资料参考。')+model.NOTICE);banner.setWordWrap(True);banner.setAccessibleName('当前事件资料的版本与范围');dialog.layout().insertWidget(0,banner);dialog.node_reference_banner=banner;dialog.node_reference_binding=b;return dialog
