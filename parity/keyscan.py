"""List TextAttributesKey external names declared by installed IDE plugins: string constants of
classes that call createTextAttributesKey. Output parity/keyscan.json {KEY: [class, ...]}"""
import glob, json, os, re, sys, zipfile
sys.path.insert(0, os.path.dirname(__file__))
from classstrings import utf8_strings
IDES = ['/Applications/PhpStorm.app/Contents', '/Applications/IntelliJ IDEA.app/Contents',
        '/Applications/Android Studio.app/Contents']
# extra plugin/IDE trees (Marketplace plugin zips, Rider) given via env PARITY_EXTRA (colon-separated dirs)
EXTRA = [d for d in os.environ.get('PARITY_EXTRA', '').split(':') if d]
NAME = re.compile(r'^[A-Za-z][A-Za-z0-9_.:\- /]{1,80}$')
found = {}
for ide in IDES + EXTRA:
    js = glob.glob(f'{ide}/**/*.jar', recursive=True) if ide in EXTRA else \
        glob.glob(f'{ide}/lib/*.jar') + glob.glob(f'{ide}/plugins/*/lib/*.jar') + glob.glob(f'{ide}/plugins/*/lib/modules/*.jar')
    for j in js:
        try: z = zipfile.ZipFile(j)
        except Exception: continue
        for n in z.namelist():
            if not n.endswith('.class'): continue
            data = z.read(n)
            if b'createTextAttributesKey' not in data: continue
            ss = utf8_strings(data)
            for s in ss:
                if NAME.match(s) and (s.upper() == s or '.' in s or '_' in s) and not s.startswith(('L', '(')) or re.match(r'^[A-Z][A-Z0-9]*[._][A-Z0-9_.]+$', s):
                    if re.match(r'^[A-Z0-9_.\-:]+$', s) and len(s) > 2:
                        found.setdefault(s, set()).add(n.rsplit('/', 1)[-1][:-6])
json.dump({k: sorted(v) for k, v in sorted(found.items())}, open(os.path.join(os.path.dirname(__file__), 'keyscan.json'), 'w'), indent=0)
print(len(found))
