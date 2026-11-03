"""Read temporary editor objects without duplicate keys or nonfinite numbers."""
import json
import math


def parse_preview_object(text, label):
    """App editor policy; does not change dictionary-based calculation inputs."""
    def reject_constant(_token):
        raise ValueError(label + '不接受非有限JSON数值。')

    def finite_float(token):
        value = float(token)
        if not math.isfinite(value):
            reject_constant(token)
        return value

    def unique_object(pairs):
        value = {}
        for key, item in pairs:
            if key in value:
                raise ValueError(label + '不接受重复字段：' + key + '。')
            value[key] = item
        return value

    try:
        value = json.loads(text, object_pairs_hook=unique_object,
                           parse_constant=reject_constant, parse_float=finite_float)
    except json.JSONDecodeError:
        raise ValueError(label + '需要合法JSON对象。') from None
    if not isinstance(value, dict):
        raise ValueError(label + '需要JSON对象。')
    return value
