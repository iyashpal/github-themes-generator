"""IntelliJ TextAttributesKey -> VS Code TextMate scope stack, per language.

Each module in this package (one per language family) defines:

    SAMPLES = {'php': ('text.html.php', r'''<?php ...''')}   # name -> (VS Code grammar scope or language id, code)
    MAP = {
        'PHP_KEYWORD':  ('php', 'function', 1),       # token containing the 1st char of the nth occurrence of
                                                       # `find` in SAMPLES['php'], as tokenised by VS Code
        'PHP_TAG':      'text.html.php meta.embedded.block.php punctuation.section.embedded.begin.php',
                                                       # explicit scope stack (no sample can produce it)
        'PHP_BRACES':   ('=', 'DEFAULT_BRACES'),       # same colour as another key
    }
    NOTES = {'PHP_IDENTIFIER': 'why a compromise was needed'}   # optional, shown in the parity report

Colours are not stored anywhere: gen_themes.py resolves every scope stack against each variant's
VS Code tokenColors with vscode-textmate (parity/resolve.js), so all 11 variants follow from one map.
How to choose the construct for a key, and how to verify it: MAPPING.md.
"""
import hashlib, importlib, json, os, pkgutil, subprocess

HERE = os.path.dirname(__file__)
PARITY = os.path.join(HERE, '..', 'parity')

IMPORT_ERRORS = []

def modules():
    for m in sorted(pkgutil.iter_modules([HERE]), key=lambda m: m.name):
        if not m.name.startswith('_'):
            try:
                yield m.name, importlib.import_module(f'syntax.{m.name}')
            except Exception as e:  # a module being edited must not break the others
                IMPORT_ERRORS.append(f'{m.name}: import failed: {e!r}')

def _node(script, payload):
    data = json.dumps(payload)
    cache = os.path.join(PARITY, '.cache')
    os.makedirs(cache, exist_ok=True)
    src = open(os.path.join(PARITY, script)).read()
    h = hashlib.sha1((src + data).encode()).hexdigest()
    path = os.path.join(cache, f'{script}.{h}.json')
    if os.path.exists(path):
        return json.load(open(path))
    r = subprocess.run(['node', os.path.join(PARITY, script)], input=data, capture_output=True, text=True, check=True)
    out = json.loads(r.stdout)
    json.dump(out, open(path, 'w'))
    return out

def load():
    """-> (scopes {key: stack}, origin {key: module}, notes {key: str}, errors [str])"""
    entries, origin, notes, errors, samples = {}, {}, {}, [], {}
    IMPORT_ERRORS.clear()
    for name, mod in modules():
        for sname, (lang, code) in getattr(mod, 'SAMPLES', {}).items():
            samples[f'{name}:{sname}'] = (lang, code)
        for k, v in mod.MAP.items():
            if k in entries:
                errors.append(f'{k}: defined in {origin[k]} and {name}')
                continue
            entries[k] = (name, v); origin[k] = name
        for k, v in getattr(mod, 'NOTES', {}).items():
            notes[k] = v
    reqs = []
    for k, (mod, v) in entries.items():
        if isinstance(v, tuple) and v[0] != '=':
            sname, find, nth = (v + (1,))[:3] if len(v) == 2 else v
            lang, code = samples.get(f'{mod}:{sname}', (None, None))
            if code is None:
                errors.append(f'{k}: unknown sample {sname!r} in {mod}'); continue
            reqs.append({'id': k, 'lang': lang, 'code': code, 'find': find, 'nth': nth})
    tok = _node('tokenize.js', reqs) if reqs else {}
    scopes = {}
    for k, (mod, v) in entries.items():
        if isinstance(v, str):
            scopes[k] = v
        elif isinstance(v, tuple) and v[0] != '=':
            r = tok.get(k, {'error': 'not tokenised'})
            if 'error' in r: errors.append(f'{k} ({mod}): {r["error"]}')
            else: scopes[k] = r['scopes']
    # aliases, resolved after everything else (may chain)
    for _ in range(5):
        for k, (mod, v) in entries.items():
            if isinstance(v, tuple) and v[0] == '=' and k not in scopes and v[1] in scopes:
                scopes[k] = scopes[v[1]]
    for k, (mod, v) in entries.items():
        if k not in scopes and not any(e.startswith(k) for e in errors):
            errors.append(f'{k} ({mod}): unresolved alias {v}')
    return scopes, origin, notes, IMPORT_ERRORS + errors

def resolve(scopes, themes):
    """themes: {variant: {'fg','bg','tokenColors'}} -> {variant: {key: {'fg', 'fontStyle'}}}"""
    stacks = sorted(set(scopes.values()))
    res = _node('resolve.js', {'themes': themes, 'stacks': stacks})
    return {v: {k: res[v][s] for k, s in scopes.items()} for v in themes}
