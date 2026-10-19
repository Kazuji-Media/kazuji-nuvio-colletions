"""Prepare a single streaming collection for import from a current Nuvio export."""
import argparse
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def apply(collections, patch, static=False):
    matches = [c for c in collections if c.get('id') == patch['collectionId']]
    if len(matches) != 1:
        raise ValueError('Expected exactly one streaming collection ID')
    result = copy.deepcopy(matches[0])
    ids = [f['id'] for f in result['folders']]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate folder IDs in input')
    for change in patch['folders']:
        matches = [f for f in result['folders'] if f['id'] == change['id']]
        if len(matches) != 1:
            raise ValueError('Missing streaming folder: ' + change['title'])
        matches[0].update(change['set'])
        if static:
            matches[0]['focusGifEnabled'] = False
            matches[0]['focusGifUrl'] = matches[0]['coverImageUrl']
    return [result]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--static', action='store_true')
    args = parser.parse_args()
    if args.input.resolve() == args.output.resolve():
        parser.error('Use a separate output file to preserve the original backup')
    data = json.loads(args.input.read_text('utf-8-sig'))
    patch = json.loads((ROOT / 'collections/streamings-artwork.json').read_text('utf-8'))
    result = apply(data, patch, args.static)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Prepared', len(result[0]['folders']), 'streaming folders; sources preserved')
