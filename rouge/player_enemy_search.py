"""Literal search over normalized enemy records from current_battle_reference."""

def matches(enemy,query):
    needle=query.strip().casefold()
    parts=[enemy['name'],enemy['description'],*enemy['abilities']]
    return not needle or needle in '\n'.join(parts).casefold()
