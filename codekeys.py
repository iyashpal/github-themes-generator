"""UI colour keys whose fallback lives in IDE code, not in any theme file.

Platform and plugin code reads many colours as `JBColor.namedColor("Some.key", <hardcoded colour>)`.
When neither our theme nor the JetBrains parent chain sets "Some.key", the hardcoded JetBrains colour
shows. This scans the IDE's class files for such call sites and records each key with its hardcoded
light/dark default in jetbrains/code_defaults.json:

    {"ProgressIcon.color": {"light": "#a8adbd", "dark": "#6f737a", "class": "com/intellij/ui/SpinningProgressIcon"}, ...}

islands_map.inherited() repaints these like the chain's own keys (snap to the nearest Primer colour,
explicit mappings in gen_themes.py win), and audit2.py fails if any of them is left unset.

Keys used only as a fallback for another key (`namedColor("Popup.borderColor", namedColor("Popup.Border.color", ...))`)
are recorded under the primary key, with the fallback's hardcoded colour. A default computed from other
keys (UIUtil.getLabelForeground(), JBUI.CurrentTheme...) already follows our theme and is skipped. A
fixed colour constant whose value javap does not show (Color.WHITE, JBColor.GRAY) is recorded as null and
repainted by role. A key the theme's "*" block covers (JBColor.namedColor matches "*" keys as name
suffixes, e.g. "*.foreground" for "Banner.foreground") never reaches its default; gen_themes.py skips those.

    python3 codekeys.py [/Applications/IDE.app ...]   # default: every installed JetBrains IDE
Needs `javap` (any JDK) on PATH.
"""
import glob, json, os, re, subprocess, sys, tempfile, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'parity'))
from classstrings import utf8_strings

KEY = re.compile(r'^[A-Z][A-Za-z0-9]*(\.[A-Za-z0-9]+)+$')
COLOURISH = re.compile(r'(Background|Foreground|Color|background|foreground|color)$')
STR = re.compile(r'// String (\S+)\s*$')
INT = re.compile(r'(?:// int (-?\d+)|\b[sb]ipush\s+(-?\d+)|\biconst_(m1|\d))')
DBL = re.compile(r'// double ([\d.Ee-]+)d')
GRAY = re.compile(r'getstatic.*com/intellij/ui/Gray\._(\d+):')
CONSTANT = re.compile(r'getstatic.*(com/intellij/ui/Gray\.(?!_\d)|java/awt/Color\.|JBColor\.(WHITE|BLACK|GRAY|LIGHT_GRAY|DARK_GRAY|RED|BLUE|GREEN|YELLOW|ORANGE|PINK|CYAN|MAGENTA))')
DERIVED = re.compile(r'invoke\w+.*(UIUtil|NamedColorUtil|JBUI|getColor|StartupUiUtil|EditorColors|getGlobalScheme|JBColor\.(lazy|namedColor|border|foreground|background|panelBackground))|getstatic(?!.*(Gray|java/awt/Color\.|JBColor\.[A-Z_]+:))')


def jars(app):
    c = os.path.join(app, 'Contents')
    return glob.glob(f'{c}/lib/*.jar') + glob.glob(f'{c}/plugins/*/lib/*.jar') + glob.glob(f'{c}/plugins/*/lib/modules/*.jar')


def hexcol(v, a=1.0):
    v &= 0xFFFFFF
    return '#%06x' % v + ('' if a >= 1 else '%02x' % round(a * 255))


def defaults(ints, alphas):
    """(light, dark) from the literals between the key and the namedColor call."""
    if len(ints) == 3 and all(0 <= i <= 255 for i in ints):  # Color(r, g, b)
        ints = [(ints[0] << 16) | (ints[1] << 8) | ints[2]]
    cols = [hexcol(v, alphas.get(i, 1.0)) for i, v in enumerate(ints)]
    if len(cols) == 1: return cols[0], cols[0]
    if len(cols) == 2: return cols[0], cols[1]
    return None, None


def parse(lines, keys, cls, out):
    for i, l in enumerate(lines):
        m = STR.search(l)
        if not m or m.group(1) not in keys:
            continue
        key = m.group(1)
        prev = STR.search(lines[i - 1]) if i else None
        if prev and 'ldc' in lines[i - 1]:
            key = prev.group(1)  # fallback name of another key: its default is the primary key's default
        ints, alphas, const, derived, called = [], {}, False, False, False
        for l2 in lines[i + 1:i + 20]:
            if 'namedColor' in l2:
                called = True; break
            if STR.search(l2):
                break  # next key (or this key's fallback name, handled on its own line)
            mi = INT.search(l2)
            if mi:
                g = mi.group(1) or mi.group(2) or mi.group(3)
                ints.append(-1 if g == 'm1' else int(g))
            md = DBL.search(l2)
            if md and ints and float(md.group(1)) < 1:
                alphas[len(ints) - 1] = float(md.group(1))
            mg = GRAY.search(l2)
            if mg:
                n = int(mg.group(1)); ints.append((n << 16) | (n << 8) | n); continue
            if CONSTANT.search(l2):
                const = True
            elif DERIVED.search(l2):
                derived = True
        if not called:
            continue
        if derived:
            continue  # computed from other keys: already follows our theme
        if ints and not const:
            light, dark = defaults(ints, alphas)
            if light is None:
                continue
        elif const:
            light = dark = None
        else:
            continue
        if key not in out or (out[key]['light'] is None and light):
            out[key] = {'light': light, 'dark': dark, 'class': cls}


def installed():
    """Every installed JetBrains IDE (Android Studio included): their plugins read different keys."""
    apps = glob.glob('/Applications/*.app') + glob.glob(os.path.expanduser('~/Applications/*.app'))
    return sorted(a for a in apps if os.path.exists(os.path.join(a, 'Contents/Resources/product-info.json'))
                  and glob.glob(os.path.join(a, 'Contents/lib/intellij.platform.*.jar')))


def scan(apps):
    out = {}
    with tempfile.TemporaryDirectory() as tmp:
        work = []
        for j in [j for app in apps for j in jars(app)]:
            try: z = zipfile.ZipFile(j)
            except Exception: continue
            for n in z.namelist():
                if not n.endswith('.class'): continue
                data = z.read(n)
                if b'namedColor' not in data: continue
                keys = {s for s in utf8_strings(data) if KEY.match(s) and COLOURISH.search(s)
                        and not s.startswith(('com.', 'org.', 'java', 'kotlin'))}
                if not keys: continue
                p = os.path.join(tmp, f'{len(work)}.class')
                open(p, 'wb').write(data)
                work.append((p, n[:-6], keys))
        for b in range(0, len(work), 60):
            batch = work[b:b + 60]
            txt = subprocess.run(['javap', '-c', '-p', '-constants'] + [p for p, _, _ in batch],
                                 capture_output=True, text=True).stdout
            # javap prints one "Compiled from"/class header per file, in argument order
            parts = re.split(r'(?m)^(?=(?:Compiled from|(?:public |final |abstract |private |protected |static |sealed )*(?:class|interface|enum) ))', txt)
            parts = [p for p in parts if re.match(r'(?:public |final |abstract |private |protected |static |sealed )*(?:class|interface|enum) ', p)]
            if len(parts) != len(batch):  # header split failed: fall back to one javap per class
                parts = [subprocess.run(['javap', '-c', '-p', '-constants', p], capture_output=True, text=True).stdout
                         for p, _, _ in batch]
            for (_, cls, keys), part in zip(batch, parts):
                parse(part.splitlines(), keys, cls, out)
    return dict(sorted(out.items()))


def main():
    apps = sys.argv[1:] or installed()
    out = scan(apps)
    json.dump(out, open(os.path.join(HERE, 'jetbrains/code_defaults.json'), 'w'), indent=1)
    print(f'codekeys: {len(out)} keys with a hardcoded default in {", ".join(os.path.basename(a) for a in apps)}')


if __name__ == '__main__':
    main()
