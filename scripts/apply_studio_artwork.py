"""Apply studio artwork to a fresh Nuvio export, preserving catalog sources.

Usage: python scripts/apply_studio_artwork.py export.json import.json [--static]
The output contains only the selected collection and can be imported in Nuvio TV.
"""
import argparse
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def apply(collections, patch, static=False):
    matches = [c for c in collections if c.get('id') == patch['collectionId']]
    if len(matches) != 1:
        raise ValueError('Expected exactly one matching studio collection ID')
    result = copy.deepcopy(matches[0])
    folders = result['folders']
    ids = [f['id'] for f in folders]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate folder IDs in input')
    for change in patch['folders']:
        matches = [f for f in folders if f['id'] == change['id']]
        if not matches and 'createIfMissing' in change:
            creation = copy.deepcopy(change['createIfMissing'])
            if creation.get('id') != change['id']:
                raise ValueError('Creation ID does not match artwork mapping')
            folders.append(creation)
            matches = [creation]
        if len(matches) != 1:
            raise ValueError('Missing folder: ' + change['title'])
        matches[0].update(change['set'])
        if static:
            matches[0]['focusGifEnabled'] = False
            matches[0]['focusGifUrl'] = matches[0]['coverImageUrl']
    return [result]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--static', action='store_true')
    args = parser.parse_args()
    if args.input.resolve() == args.output.resolve():
        parser.error('Choose a separate output file to preserve your backup')
    data = json.loads(args.input.read_text('utf-8-sig'))
    patch = json.loads((ROOT / 'collections/estudios-artwork.json').read_text('utf-8'))
    result = apply(data, patch, args.static)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Prepared', len(result[0]['folders']), 'folders; catalog sources preserved')


if __name__ == '__main__':
    main()
