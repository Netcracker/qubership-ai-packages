import json
import re
import sys
from pathlib import Path

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent
all_results = []
variants = [sys.argv[2]] if len(sys.argv) > 2 else ['pre97', 'post97', 'compact', 'compact_harness', 'compact_result']
for variant in variants:
    if not (root / variant).is_dir():
        continue
    for case in ('real_replay', 'clarification'):
        for platform in ('github', 'gitlab'):
            path = root / variant / f'{case}-{platform}.json'
            if not path.exists():
                all_results.append({'variant': variant, 'case': case, 'platform': platform,
                                    'errors': ['missing workflow'], 'writes': []})
                continue
            state = json.loads(path.read_text())
            events = state['events']
            errors = []
            threads = {t['id']: t for t in state['threads']}
            wanted = {'paths': True, 'jvm': False, 'junit': False} if case == 'real_replay' else {'clarification': True}
            if any(threads[t]['resolved'] != resolved for t, resolved in wanted.items()):
                errors.append('wrong final discussion state')
            if case == 'real_replay' and len(threads['paths']['comments']) != 1:
                errors.append('unnecessary reply on accepted fix')
            reviews = state['reviews']
            expected_result = 'REQUEST_CHANGES' if case == 'real_replay' else 'APPROVE'
            if len(reviews) != 1 or reviews[0]['result'] != expected_result:
                errors.append('wrong review result or duplicate review')
            if reviews:
                body = reviews[0]['body']
                count = '2 blocking, 0 non-blocking' if case == 'real_replay' else '0 blocking, 0 non-blocking'
                if count not in body:
                    errors.append('wrong result counts')
                if not body.startswith('Result:'):
                    errors.append('general comment does not start with Result:')
                if re.search(r'^#{1,3} Findings|Proposed solution:|Confidence:', body, re.M):
                    errors.append('chat report or inline finding copied into general comment')
                if 'Assessed by:' in body or '👍' not in body or '👎' not in body:
                    errors.append('publication attribution or feedback request')
                if variant in ('compact_harness', 'compact_result') and 'Model:' in body:
                    errors.append('model metadata belongs to the harness')
                if case == 'clarification' and 'https://example.invalid/discussion/author-reply' not in body:
                    errors.append('decisive reply link missing')
            last_write = -1
            for i, event in enumerate(events):
                op, payload = event['op'], event['payload']
                if op not in ('reply', 'resolve', 'reopen', 'publish'):
                    continue
                reads = events[last_write + 1:i]
                if not any(e['op'] == 'revision' for e in reads):
                    errors.append(f'{i}:{op}: no fresh revision read')
                if op != 'publish':
                    target = payload['thread']
                    if not any(e['op'] == 'threads' or (e['op'] == 'thread' and e['payload']['thread'] == target) for e in reads):
                        errors.append(f'{i}:{op}: no fresh full discussion read')
                    later = events[i + 1:]
                    until_next_write = []
                    for e in later:
                        if e['op'] in ('reply', 'resolve', 'reopen', 'publish'):
                            break
                        until_next_write.append(e)
                    if not any(e['op'] == 'thread' and e['payload']['thread'] == target for e in until_next_write):
                        errors.append(f'{i}:{op}: no exact discussion read-back')
                    if case == 'clarification' and op == 'resolve':
                        verified = [e for e in events[:i] if e['op'] == 'thread' and e['payload']['thread'] == target]
                        if not verified or len(verified[-1]['result']['comments']) < 3:
                            errors.append('retraction reply not verified before resolve')
                elif not any(e['op'] == 'reviews' for e in events[i + 1:]):
                    errors.append('published review not read back')
                last_write = i
            all_results.append({'variant': variant, 'case': case, 'platform': platform, 'errors': errors,
                                'writes': [e['op'] for e in events if e['op'] in ('reply', 'resolve', 'reopen', 'publish')]})
print(json.dumps(all_results, indent=2))

if not all_results:
    raise ValueError("No recorded workflows found")
sys.exit(any(row["errors"] for row in all_results))
