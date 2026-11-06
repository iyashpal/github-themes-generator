"""Check the syntax map: tokenisation errors, and the resolved colour of each key in two variants.
    python3 syntax_check.py [module ...]      # e.g. python3 syntax_check.py php"""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import syntax
VS = json.load(open(os.path.join(os.path.dirname(__file__), 'vsc/vscode.json')))
only = set(sys.argv[1:])
scopes, origin, notes, errors = syntax.load()
for e in errors:
    if not only or any(f'({m})' in e or m in e for m in only): print('ERROR', e)
themes = {n: {'fg': VS[n]['colors']['editor.foreground'], 'bg': VS[n]['colors']['editor.background'],
              'tokenColors': VS[n]['tokenColors']} for n in ('light', 'light-default', 'dark-default')}
res = syntax.resolve(scopes, themes)
for k in sorted(scopes):
    if only and origin[k] not in only: continue
    c = ' '.join(f"{res[v][k]['fg']}{'/' + res[v][k]['fontStyle'] if res[v][k]['fontStyle'] else ''}" for v in themes)
    print(f'{k:45} {c:40} {scopes[k]}' + (f'   # {notes[k]}' if k in notes else ''))
print(f'{len(scopes)} keys, {len(errors)} errors', file=sys.stderr)
