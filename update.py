#!/usr/bin/env python3
"""Pull the latest GitHub VS Code theme release and regenerate the IntelliJ themes.

    python3 update.py            # fetch latest release, rebuild, audit, show what would change
    python3 update.py --apply    # ...and copy the result into resources/theme/
    python3 update.py --tag v6.3.5   # use a specific release instead of the latest

Steps: download the release tarball into a fresh temp dir, copy its src/ into vsc/src,
re-apply the tritanopia patch, pin @primer/primitives to the release's exact version,
rebuild vsc/vscode.json, check the 9 upstream variants still match the release's
published themes/*.json, then run gen_themes.py + audit2.py.
"""
import argparse, filecmp, json, os, re, shutil, subprocess, sys, tarfile, tempfile, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
VSC = os.path.join(HERE, 'vsc')
RESOURCES = os.path.normpath(os.path.join(HERE, '..', '..', 'resources', 'theme'))
REPO = 'primer/github-vscode-theme'
UA = {'User-Agent': 'intellij-github-themes-generator', 'Accept': 'application/vnd.github+json'}

def die(msg): sys.exit(f'update: {msg}')

def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
        return r.read()

def latest_tag():
    return json.loads(get(f'https://api.github.com/repos/{REPO}/releases/latest'))['tag_name']

def fetch(tag, dest):
    """Download and extract the release tarball; returns the extracted root dir."""
    tgz = os.path.join(dest, 'src.tar.gz')
    with open(tgz, 'wb') as f:
        f.write(get(f'https://codeload.github.com/{REPO}/tar.gz/refs/tags/{tag}'))
    out = os.path.join(dest, 'x'); os.makedirs(out)
    with tarfile.open(tgz) as t:
        t.extractall(out, filter='data')  # 'data' filter rejects absolute paths, links outside, devices
    roots = os.listdir(out)
    if len(roots) != 1: die('unexpected tarball layout')
    return os.path.join(out, roots[0])

def patch_tritanopia(src):
    """theme.js/colors.js only know 7 Primer palettes; add the two tritanopia ones."""
    cj = os.path.join(src, 'colors.js'); s = open(cj).read()
    if 'tritanopia' not in s:
        a = 'const dimmedColors'
        b = '    case "dark_dimmed":'
        if a not in s or b not in s: die('colors.js changed upstream: tritanopia patch anchors missing')
        s = s.replace(a, 'const lightTritanopiaColors = require("@primer/primitives/dist/json/colors/light_tritanopia.json");\n'
                         'const darkTritanopiaColors = require("@primer/primitives/dist/json/colors/dark_tritanopia.json");\n' + a)
        s = s.replace(b, '    case "light_tritanopia":\n      return lightTritanopiaColors;\n'
                         '    case "dark_tritanopia":\n      return darkTritanopiaColors;\n' + b)
        open(cj, 'w').write(s)
    else:
        print('  colors.js already handles tritanopia upstream; patch skipped')
    tj = os.path.join(src, 'theme.js'); s = open(tj).read()
    old = 'const themes = (options) => options[theme];'
    new = "const themes = (options) => (theme in options ? options[theme] : options[theme.replace('tritanopia','colorblind')]);"
    if new in s: return
    if old not in s:
        if 'tritanopia' in s: print('  theme.js already handles tritanopia upstream; patch skipped'); return
        die('theme.js changed upstream: themes() helper not found')
    open(tj, 'w').write(s.replace(old, new))

def check_variants(root):
    """Warn if upstream added/removed theme variants our gen.js doesn't know about."""
    idx = open(os.path.join(root, 'src', 'index.js')).read()
    up = set(re.findall(r'\./themes/([\w-]+)\.json', idx))
    ours = set(re.findall(r"'([\w-]+)'\s*:", open(os.path.join(VSC, 'gen.js')).read().split('const variants=')[1].split('};')[0]))
    ours |= {'light', 'dark'}
    if up - ours: print(f'  WARNING: new upstream variants not generated: {sorted(up - ours)}')

JB_FILES = {  # path inside lib/intellij.platform.ide.impl.jar -> file in jetbrains/
    'themes/darcula.theme.json': 'darcula.theme.json',
    'themes/intellijlaf.theme.json': 'intellijlaf.theme.json',
    'themes/expUI/expUI_dark.theme.json': 'expUI_dark.theme.json',
    'themes/expUI/expUI_light.theme.json': 'expUI_light.theme.json',
    'themes/expUI/expUI_light_with_light_header.theme.json': 'expUI_light_with_light_header.theme.json',
    'themes/islands/ManyIslandsDark.theme.json': 'ManyIslandsDark.theme.json',
    'themes/islands/ManyIslandsLight.theme.json': 'ManyIslandsLight.theme.json',
}

def refresh_jetbrains():
    """Copy the parent theme chain (Darcula/IntelliJ -> expUI -> Islands) from the newest installed
    JetBrains IDE into jetbrains/. These are the themes our files inherit from, so the generator can
    repaint every colour they would otherwise leak. Skipped if no IDE is installed."""
    import glob, zipfile
    cands = []
    for app in glob.glob('/Applications/*.app') + glob.glob(os.path.expanduser('~/Applications/*.app')):
        # the themes live in intellij.platform.resources.jar since 2026.3 (ide.impl.jar before)
        jar = next((j for j in (os.path.join(app, 'Contents/lib', n) for n in
                                ('intellij.platform.resources.jar', 'intellij.platform.ide.impl.jar'))
                    if os.path.exists(j) and 'themes/islands/ManyIslandsDark.theme.json' in zipfile.ZipFile(j).namelist()), None)
        info = os.path.join(app, 'Contents/Resources/product-info.json')
        if jar and os.path.exists(info):
            build = json.load(open(info)).get('buildNumber', '0')
            cands.append((tuple(int(x) for x in re.findall(r'\d+', build)), build, app, jar))
    if not cands:
        print('jetbrains: no installed IDE found; keeping jetbrains/ as is'); return
    _, build, app, jar = max(cands)
    dst = os.path.join(HERE, 'jetbrains'); os.makedirs(dst, exist_ok=True)
    with zipfile.ZipFile(jar) as z:
        names = set(z.namelist())
        missing = [p for p in JB_FILES if p not in names]
        if missing: die(f'{os.path.basename(app)} {build}: theme files moved: {missing}')
        for src, name in JB_FILES.items():
            with z.open(src) as f, open(os.path.join(dst, name), 'wb') as out:
                out.write(f.read())
    prev = json.load(open(os.path.join(dst, 'SOURCE.json'))).get('build') if os.path.exists(os.path.join(dst, 'SOURCE.json')) else None
    json.dump({'ide': os.path.basename(app), 'build': build}, open(os.path.join(dst, 'SOURCE.json'), 'w'), indent=2)
    print(f'jetbrains: theme chain from {os.path.basename(app)} {build} (previous: {prev or "unknown"})')
    # colour keys whose only default is hardcoded in IDE code (repainted too; see codekeys.py)
    import codekeys
    apps = codekeys.installed()
    out = codekeys.scan(apps)
    json.dump(out, open(os.path.join(dst, 'code_defaults.json'), 'w'), indent=1)
    print(f'jetbrains: {len(out)} colour keys with a hardcoded default in the code of {len(apps)} installed IDEs')

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tag'); ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()
    for tool in ('node', 'npm'):
        if not shutil.which(tool): die(f'{tool} is required')

    refresh_jetbrains()
    tag = args.tag or latest_tag()
    info_path = os.path.join(VSC, 'UPSTREAM.json')
    prev = json.load(open(info_path)) if os.path.exists(info_path) else {}
    print(f'upstream {REPO}: {tag} (current: {prev.get("tag", "unknown")})')

    tmp = tempfile.mkdtemp(prefix='gh-vscode-theme-')
    try:
        root = fetch(tag, tmp)
        pkg = json.load(open(os.path.join(root, 'package.json')))
        prim = pkg.get('devDependencies', {}).get('@primer/primitives') or pkg.get('dependencies', {}).get('@primer/primitives')
        if not prim: die('upstream package.json has no @primer/primitives')
        prim = prim.lstrip('^~')
        print(f'  @primer/primitives {prim}')
        check_variants(root)

        # pin primitives to the release's exact version
        lp = os.path.join(VSC, 'package.json'); local = json.load(open(lp))
        local['dependencies']['@primer/primitives'] = prim
        json.dump(local, open(lp, 'w'), indent=2); open(lp, 'a').write('\n')
        subprocess.run(['npm', 'install', '--ignore-scripts', '--no-audit', '--no-fund'], cwd=VSC, check=True,
                       stdout=subprocess.DEVNULL)

        # reference build from the unpatched release (inside vsc/ so it resolves vsc/node_modules)
        ref_src = os.path.join(VSC, 'src_upstream')
        shutil.rmtree(ref_src, ignore_errors=True)
        shutil.copytree(os.path.join(root, 'src'), ref_src, ignore=shutil.ignore_patterns('index.js'))
        ref_out = os.path.join(tmp, 'reference.json')
        try:
            subprocess.run(['node', 'gen.js', 'src_upstream', ref_out, '--upstream-only'], cwd=VSC, check=True)
        finally:
            shutil.rmtree(ref_src, ignore_errors=True)

        # patched build: replace vsc/src with the release's src + tritanopia patch
        dst = os.path.join(VSC, 'src')
        shutil.rmtree(dst)
        shutil.copytree(os.path.join(root, 'src'), dst, ignore=shutil.ignore_patterns('index.js'))
        patch_tritanopia(dst)
        subprocess.run(['node', 'gen.js'], cwd=VSC, check=True)

        # the patch may only add tritanopia: every upstream variant must be identical
        ref = json.load(open(ref_out)); built = json.load(open(os.path.join(VSC, 'vscode.json')))
        bad = [n for n in ref if ref[n] != built.get(n)]
        if bad: die('tritanopia patch changed upstream variants: ' + ', '.join(bad))
        print(f'  patched build matches the unpatched upstream build for all {len(ref)} upstream variants')
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    json.dump({'repo': REPO, 'tag': tag, 'primitives': prim}, open(info_path, 'w'), indent=2)
    open(info_path, 'a').write('\n')

    out = tempfile.mkdtemp(prefix='gh-themes-out-')
    try:
        subprocess.run([sys.executable, os.path.join(HERE, 'gen_themes.py'), out], check=True, stdout=subprocess.DEVNULL)
        audit = subprocess.run([sys.executable, os.path.join(HERE, 'audit2.py'), out], cwd=HERE, capture_output=True, text=True)
        print(audit.stdout.strip())
        if 'ALL CHECKS PASS' not in audit.stdout: die('audit failed; resources/theme left untouched')
        cmp = filecmp.dircmp(out, RESOURCES)
        changed = cmp.diff_files + [f'scheme/{f}' for f in filecmp.dircmp(os.path.join(out, 'scheme'), os.path.join(RESOURCES, 'scheme')).diff_files]
        print(f'changed files vs resources/theme: {len(changed)}' + (''.join(f'\n  {c}' for c in changed)))
        if args.apply and changed:
            for c in changed: shutil.copy(os.path.join(out, c), os.path.join(RESOURCES, c))
            print('applied to resources/theme/ (rebuild the jar before releasing)')
        elif changed:
            print('run with --apply to copy them into resources/theme/')
    finally:
        shutil.rmtree(out, ignore_errors=True)

if __name__ == '__main__':
    main()
