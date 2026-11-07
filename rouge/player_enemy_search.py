"""Literal search over normalized enemy records from current_battle_reference."""

def matches(enemy,query):
    return matches_normalized(enemy, query.strip().casefold())


def matches_normalized(enemy, needle):
    parts=[enemy['name'],enemy['description'],*enemy['abilities']]
    return not needle or needle in '\n'.join(parts).casefold()
