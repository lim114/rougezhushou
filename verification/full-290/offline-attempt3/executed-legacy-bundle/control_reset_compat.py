"""Legacy False reset for a new optional ratio control, with no guessed value.

Harness only. A True checkbox declaration has no ratio semantics and is refused.
The production source is never edited; the actual public setValue(None) runs.
"""
import hashlib
import importlib
import json
from pathlib import Path


def install(root, expected_class_source_sha256, output=None):
    root = Path(root).resolve()
    module = importlib.import_module('rouge.susuro_healing_view')
    path = Path(module.__file__).resolve()
    if path != root / 'rouge/susuro_healing_view.py':
        raise AssertionError('The actual recipient class is outside the frozen source.')
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected_class_source_sha256:
        raise AssertionError('The independently checked recipient class source changed.')
    cls = module.RecipientRatioInput
    if hasattr(cls, 'setChecked'):
        raise AssertionError('Do not replace an existing recipient class method.')
    ledger = []

    def reset_only_false(widget, checked):
        if checked is not False:
            raise ValueError('Legacy checkbox compatibility only clears a ratio with False; True/0/null cannot declare a ratio.')
        before = {'effective_ratio': widget.value(), 'known': widget.known.isChecked(),
                  'raw_ratio': widget.ratio.value(), 'enabled': widget.ratio.isEnabled()}
        widget.setValue(None)
        after = {'effective_ratio': widget.value(), 'known': widget.known.isChecked(),
                 'raw_ratio': widget.ratio.value(), 'enabled': widget.ratio.isEnabled()}
        if (after['effective_ratio'] is not None or after['known'] is not False or
                after['enabled'] is not False or after['raw_ratio'] != before['raw_ratio']):
            raise AssertionError('The actual ratio reset did not preserve unknown semantics.')
        ledger.append({'input_is_exact_False': True, 'actual_public_method': 'setValue(None)',
                       'before': before, 'after': after, 'synthesized_numeric_ratio': False})

    cls.setChecked = reset_only_false

    def restore():
        if cls.__dict__.get('setChecked') is not reset_only_false:
            raise AssertionError('The narrow recipient harness method was replaced.')
        delattr(cls, 'setChecked')

    def write_ledger():
        if output is not None:
            path = Path(output) / 'recipient-false-reset-ledger.json'
            path.write_text(json.dumps({'scope': 'Actual False-only reset via unchanged public ratio API',
                'class_source_sha256': expected_class_source_sha256,
                'calls': ledger, 'true_or_numeric_alias_supported': False,
                'production_source_edited': False, 'raw_calculation_result_rewritten': False,
                'original_assertions_or_expectations_rewritten': False}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return restore, write_ledger, ledger
