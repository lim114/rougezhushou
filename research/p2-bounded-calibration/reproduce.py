"""Reproduce literal formula bounds and an independent finite order oracle."""
from fractions import Fraction
from itertools import product
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from rouge.bounded_calibration import bounded_calibration, _OrderBounds


def main():
    examples = json.loads(Path(__file__).with_name('examples.json').read_text(encoding='utf-8'))
    cases = []
    for example in examples['cases']:
        result = bounded_calibration(**example['payload'])
        if result['native_verified'] or any(row['classification'] != 'all_compatible' for row in result['panel']['rows']):
            raise ValueError('公开公式退化界限不符；不能认证游戏。')
        cases.append({'id': example['id'], 'panel_states': [r['classification'] for r in result['panel']['rows']],
            'timing_joint_declarations_feasible': result['timing']['joint_constraints_feasible'],
            'native_verified': result['native_verified']})
    graph = _OrderBounds()
    domains = {'a': (0, 3), 'b': (1, 4), 'c': (2, 5)}
    for name, bounds in domains.items():
        graph.add(name, tuple(Fraction(v) for v in bounds))
    graph.order('a', 'b')
    graph.order('b', 'c')
    graph.solve()
    feasible = [dict(zip(domains, values)) for values in product(*(range(lo, hi + 1) for lo, hi in domains.values()))
                if values[0] <= values[1] <= values[2]]
    pairs = []
    for a in domains:
        for b in domains:
            values = [sample[b] - sample[a] for sample in feasible]
            bounds = graph.difference(a, b)
            if (bounds['lower'], bounds['upper']) != (min(values), max(values)):
                raise ValueError('联合区间与独立枚举不符。')
            pairs.append({'before': a, 'after': b, 'minimum': min(values), 'maximum': max(values)})
    print(json.dumps({'scope': 'declared_bounds_not_measurement_confidence', 'cases': cases,
        'independent_finite_order_oracle': {'feasible_assignments': len(feasible), 'pairs': pairs}},
        ensure_ascii=False, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
