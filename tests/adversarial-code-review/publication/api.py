import copy
import json
import sys
from pathlib import Path

root = Path(__file__).parent
session, case, platform, operation = sys.argv[1:5]
payload = json.loads(Path(sys.argv[5]).read_text()) if len(sys.argv) > 5 else {}
directory = root / session
directory.mkdir(exist_ok=True)
path = directory / f'{case}-{platform}.json'
if path.exists():
    state = json.loads(path.read_text())
else:
    fixture = json.loads((root / 'fixtures.json').read_text())
    state = copy.deepcopy(fixture['cases'][case])
    state.update(events=[], reviews=[], platform=platform, account='denifilatoff')
    state['revision'] = {'base': '3eee3aa9452514738d1936e79cbeca1748046b74',
                         'head': fixture['provenance']['head']}
    if platform == 'gitlab':
        state['revision']['start'] = state['revision']['base']
result = None
if operation == 'context':
    result = {key: state[key] for key in ('platform', 'account', 'revision', 'evidence')}
    result['threads'] = [t['id'] for t in state['threads']]
    result['user_request'] = 'Review this follow-up and publish in English now. Personal assessment not confirmed.'
elif operation == 'revision':
    result = state['revision']
elif operation == 'threads':
    result = state['threads']
elif operation in ('thread', 'reply', 'resolve', 'reopen'):
    thread = next(t for t in state['threads'] if t['id'] == payload['thread'])
    if operation == 'reply':
        comment = {'id': f'reply-{len(state["events"])}', 'author': state['account'],
                   'body': payload['body'], 'url': 'https://example.invalid/new-reply'}
        thread['comments'].append(comment)
        result = {'id': comment['id'], 'accepted': True}
    elif operation in ('resolve', 'reopen'):
        thread['resolved'] = operation == 'resolve'
        result = {'accepted': True}
    else:
        result = thread
elif operation == 'publish':
    review = {'id': f'review-{len(state["reviews"])}', **payload}
    state['reviews'].append(review)
    result = {'id': review['id'], 'accepted': True}
elif operation == 'reviews':
    result = state['reviews']
else:
    raise ValueError(operation)
state['events'].append({'op': operation, 'payload': payload, 'result': copy.deepcopy(result)})
path.write_text(json.dumps(state, indent=2))
print(json.dumps(result, indent=2))
