"""Open only a revalidated acquisition's exact existing reader and target."""
from . import current_named_reward_origins as model
def make_event_dialog(row,parent=None):
    if type(row)is not dict or type(row.get('item_id'))is not str:return None
    fresh=model.reference('relics',row['item_id'])
    if fresh is None or not any(model_row==row for model_row in fresh['rows']):return None
    target=row['target'];reader=row['reader_key']
    if reader=='resources':
        from .current_resource_events_view import CurrentResourceEventsDialog
        return CurrentResourceEventsDialog(target['event_id'],target['scene_id'],target['choice_id'],parent)
    if reader=='encounters':
        from .current_encounters_view import CurrentEncountersDialog
        return CurrentEncountersDialog(target['event_id'],target['scene_id'],target['choice_id'],parent)
    if reader=='peace':
        from .current_peace_view import CurrentPeaceDialog
        return CurrentPeaceDialog(target['scene_id'],target['choice_id'],parent)
    if reader=='ritual':
        from .current_ritual_view import CurrentRitualDialog
        return CurrentRitualDialog(target['event_id'],target['scene_id'],target['choice_id'],parent)
    if reader=='reconstruction':
        from .current_reconstruction_view import CurrentReconstructionDialog
        return CurrentReconstructionDialog(target,parent)
    if reader=='resting':
        from .current_resting_view import CurrentRestingDialog
        return CurrentRestingDialog(target,parent)
    if reader=='shadow':
        from .current_shadow_view import CurrentShadowDialog
        return CurrentShadowDialog(target,parent)
    return None
