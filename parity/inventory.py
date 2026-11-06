"""Inventory of every TextAttributesKey the bundled Default/Darcula schemes (plus plugin
additionalTextAttributes) set, across the installed JetBrains IDEs. Output: parity/inventory.json
  {"light": {KEY: {opt: val}}, "dark": {...}, "sources": {KEY: [file, ...]}}"""
import glob, json, os, re, sys, zipfile
import xml.etree.ElementTree as ET

IDES = ['/Applications/PhpStorm.app/Contents', '/Applications/IntelliJ IDEA.app/Contents',
        '/Applications/Android Studio.app/Contents']
# extra plugin/IDE trees (Marketplace plugin zips, Rider) given via env PARITY_EXTRA (colon-separated dirs)
EXTRA = [d for d in os.environ.get('PARITY_EXTRA', '').split(':') if d]
SCHEME = {'Default': 'light', 'Darcula': 'dark'}

def attrs_of(root):
    out = {}
    a = root if root.tag == 'list' else root.find('attributes')
    if a is None: return out
    for o in a.findall('option'):
        v = o.find('value')
        if o.get('baseAttributes'):
            out[o.get('name')] = {'baseAttributes': o.get('baseAttributes')}
        elif v is not None:
            out[o.get('name')] = {x.get('name'): x.get('value') for x in v.findall('option')}
        else:
            out[o.get('name')] = {}
    return out

def jars(ide):
    if ide in EXTRA: return glob.glob(f'{ide}/**/*.jar', recursive=True)
    return glob.glob(f'{ide}/lib/*.jar') + glob.glob(f'{ide}/plugins/*/lib/*.jar') + glob.glob(f'{ide}/plugins/*/lib/modules/*.jar')

res = {'light': {}, 'dark': {}, 'sources': {}}
def add(variant, attrs, src):
    for k, v in attrs.items():
        res[variant].setdefault(k, v)
        res['sources'].setdefault(k, []).append(src)

for ide in IDES + EXTRA:
    if not os.path.isdir(ide): continue
    idename = ide.split('/')[2]
    for j in jars(ide):
        try: z = zipfile.ZipFile(j)
        except Exception: continue
        names = set(z.namelist())
        if 'DefaultColorSchemesManager.xml' in names:
            r = ET.fromstring(z.read('DefaultColorSchemesManager.xml'))
            for s in r.findall('scheme'):
                if s.get('name') in SCHEME: add(SCHEME[s.get('name')], attrs_of(s), f'{idename}:{s.get("name")}')
        for n in names:
            if not n.endswith('.xml') or not (n.startswith('META-INF/') or n.count('/') == 0): continue
            try: txt = z.read(n).decode('utf-8', 'replace')
            except Exception: continue
            for m in re.finditer(r'<additionalTextAttributes\s+([^>]*)/?>', txt):
                at = dict(re.findall(r'(\w+)="([^"]*)"', m.group(1)))
                sch, f = at.get('scheme'), at.get('file', '').lstrip('/')
                if sch not in SCHEME or not f: continue
                for jj in jars(ide):  # resource may live in a sibling jar of the plugin
                    try:
                        zz = zipfile.ZipFile(jj)
                        if f in zz.namelist():
                            add(SCHEME[sch], attrs_of(ET.fromstring(zz.read(f))), f'{idename}:{os.path.basename(jj)}:{f}')
                            break
                    except Exception: pass
json.dump(res, open(os.path.join(os.path.dirname(__file__), 'inventory.json'), 'w'), indent=1, sort_keys=True)
print('light keys', len(res['light']), 'dark keys', len(res['dark']), 'union', len(set(res['light']) | set(res['dark'])))
