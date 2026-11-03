"""Read human-authored component reviews; never create a visual judgment."""

A2_REVIEW_SHA = 'a8e08cbac02ec97610157eb0b71fc3325d74d25d713d17f7ff0de1ec6f00af7c'
SOURCE75_SHA = '75cec266144a389b93aced04d150c4cf6e72a23403f250a9caab9915543e6ec0'


def verify_A2_visual_review(b, path):
    root = b.ROOT
    main = root / 'verification/full-290/execution-attempt2'
    p3 = root / 'verification/full-290/p3-supplementary-attempt2'
    review = b.read(path)
    b.require(b.sha(path) == A2_REVIEW_SHA
        and review['kind'] == 'root_manual_visual_review_not_test_execution'
        and review['source_freeze_sha256'] == SOURCE75_SHA
        and review['legacy_retry_not_reviewed'] is True and review['full_validation_pass_claimed'] is False,
        'actual root A2 current/P3 manual review, not legacy retry or whole full PASS')
    expected = {}
    for folder in (main, p3):
        manifest = b.read(folder / 'archive-manifest.json')
        for relative, record in manifest['files'].items():
            if relative.endswith('.png') and (relative.startswith('current29/actual/')
                    or relative.startswith('current30/actual/') or relative.startswith('p3_')):
                expected[(folder.name, relative)] = record['sha256']
    seen = set()
    for image in review['images']:
        component, relative = image['component'], image['relative_path']
        if component == 'p3':
            key, folder = (p3.name, relative), p3
            b.require(relative.startswith('p3_'), 'P3 actual component path')
        else:
            b.require(component in ('current29', 'current30_partial_nonpass'), 'exact declared A2 current component')
            key, folder = (main.name, relative), main
            b.require(relative.startswith(('current29/' if component == 'current29' else 'current30/') + 'actual/'),
                'actual current source component path')
            if component == 'current30_partial_nonpass':
                b.require(image['does_not_override_current30_failure'] is True, 'failure image review cannot convert1314 to pass')
        b.require(key in expected and key not in seen and image['sha256'] == expected[key]
            and b.sha(b.safe_child(folder, relative)) == expected[key]
            and isinstance(image['review'], str) and bool(image['review'].strip()), 'actual image SHA and human review row')
        seen.add(key)
    b.require(seen == set(expected) and review['actual_unique_images_separately_viewed'] == len(set(expected.values()))
        and review['identical_current30_images_reused_by_sha'] == len(expected) - len(set(expected.values())),
        'all actual current/P3 PNG paths reviewed, byte-identical duplicates explicitly distinguished')
    return {'path': b.relative(path), 'sha256': b.sha(path), 'source_freeze_sha256': SOURCE75_SHA,
        'actual_validation_attempt': 2, 'actual_image_paths': len(expected),
        'actual_unique_images_directly_viewed': review['actual_unique_images_separately_viewed'],
        'identical_current30_images_reused_by_sha': review['identical_current30_images_reused_by_sha'],
        'current30_review_does_not_override_failure': True, 'legacy_retry_images_in_this_review': False}


def verify_legacy_visual_review(b, path, legacy):
    review = b.read(path)
    b.require(review['kind'] == 'root_manual_visual_review_not_test_execution'
        and review['source_freeze_sha256'] == SOURCE75_SHA
        and review['validation_segment'] == 'legacy_retry' and review['actual_legacy_execution_ordinal'] == 3
        and review['full_validation_pass_claimed'] is False, 'root separate actual legacy retry manual review authority')
    expected = legacy['pngs']
    seen = set()
    for image in review['images']:
        relative = image['relative_path']
        target = b.safe_child(legacy['folder'], relative)
        public_name = b.relative(target)
        b.require(public_name in expected and public_name not in seen
            and image['sha256'] == expected[public_name] == b.sha(target)
            and isinstance(image['review'], str) and bool(image['review'].strip()), 'individually reviewed new actual legacy PNG')
        seen.add(public_name)
    b.require(seen == set(expected), 'all new complete legacy four PNGs actually reviewed, no A1/A2 substitution')
    return {'path': b.relative(path), 'sha256': b.sha(path), 'source_freeze_sha256': SOURCE75_SHA,
        'validation_segment': 'legacy_retry', 'actual_legacy_execution_ordinal': 3,
        'actual_image_paths': len(expected), 'A2_partial_legacy_images_used_as_success_evidence': False}
