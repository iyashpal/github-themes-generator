"""Cross-checks of the generated editor schemes against VS Code.
    python3 parity/verify.py <out-dir>        (out-dir = gen_themes.py output)
1. every mapped syntax key's colour/style in every variant == vscode-textmate resolution (AA nudges listed)
2. every sample-based mapping hits a token whose text belongs to the `find` string (not whitespace,
   not a neighbouring token)
3. coverage: every JetBrains-set key and every mapped key is present in all 11 schemes, same key set
"""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.dirname(HERE)
sys.path.insert(0, GEN)
import syntax  # noqa: E402

OUT = sys.argv[1]
VS = json.load(open(os.path.join(GEN, 'vsc/vscode.json')))
INV = json.load(open(os.path.join(HERE, 'inventory.json')))
VARIANTS = sorted(f[:-4] for f in os.listdir(os.path.join(OUT, 'scheme')) if f.endswith('.xml'))

def attrs(path):
    s = open(path).read().split('<attributes>')[1]
    d = {}
    for m in re.finditer(r'\n        <option name="([^"]+)"(?: baseAttributes="([^"]+)")?\s*/?>(.*?)(?=\n        <option name=|\n    </attributes>)', s, re.S):
        if m.group(2): d[m.group(1)] = {'BASE': m.group(2)}; continue
        d[m.group(1)] = dict(re.findall(r'<option name="([A-Z_]+)" value="([^"]*)"', m.group(3)))
    return d

scopes, origin, notes, errors = syntax.load()
problems = {1: [], 2: [], 3: []}
for e in errors: problems[1].append(f'map error: {e}')
themes = {n: {'fg': VS[n]['colors']['editor.foreground'], 'bg': VS[n]['colors']['editor.background'],
              'tokenColors': VS[n]['tokenColors']} for n in VARIANTS}
res = syntax.resolve(scopes, themes)
schemes = {v: attrs(os.path.join(OUT, 'scheme', v + '.xml')) for v in VARIANTS}

# 1 -- output == VS Code resolution
nudged = 0
for v in VARIANTS:
    for k in scopes:
        a = schemes[v].get(k)
        if a is None: problems[1].append(f'{v}: {k} missing'); continue
        want = res[v][k]['fg'].lstrip('#').lower()
        got = a.get('FOREGROUND', '').lower()
        st = res[v][k]['fontStyle'].split()
        ft = str((1 if 'bold' in st else 0) | (2 if 'italic' in st else 0))
        if got != want:
            # allowed only as a minimal AA nudge: VS Code value below the threshold, ours meets it
            bg = VS[v]['colors']['editor.background']
            sys.path.insert(0, GEN)
            from gen_themes import contrast, over  # noqa
            cw, cg = contrast(over('#' + want, bg), over(bg, '#000000')), contrast('#' + got, over(bg, '#000000'))
            if cw < 4.5 and 4.5 <= cg < 5.2:
                nudged += 1
            else:
                problems[1].append(f'{v}: {k} {want} -> {got} (VS Code {cw:.2f}, ours {cg:.2f}) NOT an AA nudge')
        if (a.get('FONT_TYPE', '0') or '0') != ft:
            problems[1].append(f'{v}: {k} font {a.get("FONT_TYPE", "0")} != VS Code {ft} ({res[v][k]["fontStyle"]})')

# 2 -- sample targeting
reqs, meta = [], {}
samples = {}
for name, mod in syntax.modules():
    for sname, (lang, code) in getattr(mod, 'SAMPLES', {}).items(): samples[(name, sname)] = (lang, code)
    for k, v in mod.MAP.items():
        if isinstance(v, tuple) and v[0] != '=':
            sname, find, nth = (v + (1,))[:3] if len(v) == 2 else v
            lang, code = samples[(name, sname)]
            reqs.append({'id': k, 'lang': lang, 'code': code, 'find': find, 'nth': nth}); meta[k] = (name, find)
tok = syntax._node('tokenize.js', reqs)
for k, r in tok.items():
    name, find = meta[k]
    t = r.get('text', '')
    if 'error' in r: problems[2].append(f'{k} ({name}): {r["error"]}'); continue
    f = find.strip()
    if not t.strip() and f:
        problems[2].append(f'{k} ({name}): hits whitespace {t!r} for find {find!r}')
    elif not (f.startswith(t.strip()) or t.strip().startswith(f) or f in t or (t.strip() and t.strip() in f)):
        problems[2].append(f'{k} ({name}): token {t!r} vs find {find!r}')

# 3 -- coverage & parity
inv = set(INV['light']) | set(INV['dark'])
keysets = {v: set(schemes[v]) for v in VARIANTS}
base = keysets[VARIANTS[0]]
for v in VARIANTS:
    if keysets[v] != base: problems[3].append(f'{v}: key set differs ({len(keysets[v] ^ base)} keys)')
    miss = inv - keysets[v] - {'TAB_SELECTED', 'TAB_SELECTED_INACTIVE'}
    if miss: problems[3].append(f'{v}: JetBrains-set keys missing: {sorted(miss)[:10]} (+{max(0, len(miss) - 10)})')
    for k, a in schemes[v].items():
        if 'BASE' in a and a['BASE'] not in schemes[v] and a['BASE'] != 'TEXT':
            problems[3].append(f'{v}: {k} inherits missing {a["BASE"]}')

print(f'(check 1: {nudged} values differ from VS Code only by a minimal AA nudge)')
for i, title in ((1, 'output == VS Code resolution'), (2, 'sample targeting'), (3, 'coverage / parity')):
    p = problems[i]
    print(f'== check {i}: {title}: {"OK" if not p else str(len(p)) + " issue(s)"}')
    for x in p[:400]: print('  ', x)
