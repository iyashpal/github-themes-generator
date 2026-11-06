"""Repaint every colour key a GitHub theme inherits from JetBrains' Islands themes.

Our themes set parentTheme to "Islands Dark"/"Islands Light", so any key they do not set
falls through the JetBrains chain and shows JetBrains' own palette:

  dark : Darcula -> expUI_dark (ExperimentalDark) -> ManyIslandsDark
  light: Darcula -> intellijlaf (IntelliJ) -> expUI_light -> expUI_light_with_light_header -> ManyIslandsLight

`inherited(dark, S)` resolves that chain (jetbrains/*.theme.json, copied from the IDE) and returns
{key: colour} for every colour-valued key, repainted into the GitHub palette:
  * Islands semantic tokens (popup-bg, text-muted, control-brand-bg, ...) map to their Primer
    equivalent explicitly (SEMANTIC below);
  * any other colour (expUI/Darcula palette or literal hex) snaps to the nearest Primer colour:
    greys to our surfaces/text greys by luminance, chromatic colours to the same-hue Primer scale.
"""
import colorsys, json, math, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
JB = os.path.join(HERE, 'jetbrains')
CHAINS = {
    True: ['darcula', 'expUI_dark', 'ManyIslandsDark'],
    False: ['darcula', 'intellijlaf', 'expUI_light', 'expUI_light_with_light_header', 'ManyIslandsLight'],
}
HEX = re.compile(r'#?[0-9a-fA-F]{6}([0-9a-fA-F]{2})?')
INSETS_COLOR = re.compile(r'((?:\d+,){4})(#?[0-9a-fA-F]{6,8}|[A-Za-z][\w.-]*)')


def _load(name):
    s = re.sub(r'(?m)^\s*//.*$', '', open(os.path.join(JB, name + '.theme.json')).read())
    return json.loads(s)


def _flat(o, p=''):
    for k, v in o.items():
        kk = f'{p}.{k}' if p else k
        if isinstance(v, dict):
            yield from _flat(v, kk)
        else:
            yield kk, v


def chain(dark):
    """Effective {key: (raw value, merged colour table)} after applying the JetBrains chain."""
    eff, colors = {}, {}
    for name in CHAINS[dark]:
        d = _load(name)
        colors = {**colors, **d.get('colors', {})}
        for k, v in _flat(d.get('ui', {})):
            eff[k] = (v, colors)
    return eff


# ------------------------------------------------------------------ colour helpers
def _rgba(c):
    c = c.lstrip('#')
    if len(c) in (3, 4):
        c = ''.join(x * 2 for x in c)
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4)), (int(c[6:8], 16) / 255 if len(c) == 8 else 1.0)


def _lum(rgb):
    v = [x / 255 for x in rgb]
    v = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in v]
    return 0.2126 * v[0] + 0.7152 * v[1] + 0.0722 * v[2]


def _hex(rgb, a=1.0):
    return '#' + ''.join('%02x' % v for v in rgb) + ('' if a >= 1 else '%02x' % round(a * 255))


def _family(rgb):
    h, l, s = colorsys.rgb_to_hls(*[x / 255 for x in rgb])
    if s < 0.15 or l < 0.06 or l > 0.97:
        return 'gray'
    h *= 360
    for lim, fam in ((15, 'red'), (40, 'orange'), (65, 'yellow'), (165, 'green'), (255, 'blue'),
                     (290, 'purple'), (335, 'pink'), (361, 'red')):
        if h < lim:
            return fam


def snap(c, S):
    """Nearest GitHub-palette colour (alpha preserved). Neutral translucent overlays stay as-is."""
    if not HEX.fullmatch(c):
        return None
    rgb, a = _rgba(c)
    fam = _family(rgb)
    if a < 1 and (min(rgb) >= 250 or max(rgb) <= 5):
        return _hex(rgb, a)  # pure white/black overlays are palette-neutral
    pool = S['grays'] if fam == 'gray' else S['scale'][fam]
    target = math.log(_lum(rgb) + .05)
    best = min(pool, key=lambda x: abs(math.log(_lum(_rgba(x)[0]) + .05) - target))
    brgb, _ = _rgba(best)
    return _hex(brgb, a)


# ------------------------------------------------------------------ semantic tokens
SEMANTIC_NAMES = set()


def semantic(S, dark):
    """Islands token -> GitHub colour. S holds the resolved surfaces/palette of one variant."""
    P, ov = S['P'], S['over']
    cv, frame, ovl = S['canvas'], S['frame'], S['overlay']
    sub = lambda k, bg=None: ov(P[k + 'Subtle'], bg or cv)
    mut = lambda k, bg=None: ov(P[k + 'Muted'], bg or cv)
    border, muted_b = S['border'], S['borderMuted']
    hover, press = S['alpha'](P['fg'], .08), S['alpha'](P['fg'], .12)
    m = {
        'transparent': '#00000000',
        # text
        'text-default': P['fg'], 'editor-text': P['fg'], 'text-muted': P['fgMuted'], 'text-secondary': P['fgMuted'],
        'text-disabled': P['fgSubtle'], 'text-link': P['accentFg'], 'text-success': P['successFg'],
        'text-warning': P['attentionFg'], 'text-error': P['dangerFg'], 'text-over-accent': P['fgOnEmphasis'],
        'text-over-accent-inverted': P['fg'], 'popup-completion-match-text': P['accentFg'],
        'got-it-text-link': P['accentFg'], 'got-it-text-step': P['fgMuted'],
        # surfaces: islands share the editor canvas; the frame is separate; popups use the overlay
        'editor-bg': cv, 'tool-window-bg': cv, 'tool-window-bg-alt': cv, 'dialog-bg': cv,
        'control-bg': cv, 'control-bg-disabled': cv, 'feedback-bg-inline': cv,
        'editor-bg-inline': S['subtle'], 'tool-window-bg-inline': S['subtle'], 'dialog-bg-inline': S['subtle'],
        'popup-bg-inline': S['subtle'],
        'main-window-bg': frame, 'main-window-bg-alt': frame,
        'popup-bg': ovl, 'feedback-bg': ovl, 'editor-floating-toolbar-bg': ovl, 'got-it-bg': ovl,
        'control-bg-raised': ov(P['btnBg']), 'got-it-contrast-button-bg': ov(P['btnBg']),
        'control-bg-small': ov(P['neutralMuted']), 'control-bg-small-disabled': S['subtle'],
        'got-it-shortcut-bg': ov(P['neutralMuted'], ovl), 'inlay-bg': ov(P['neutralMuted']),
        'tab-file-color-mask-bg': cv + '80',
        # borders: faint inside islands, regular for controls/popups
        'editor-border': muted_b, 'editor-border-inline': muted_b, 'editor-border-alt': muted_b,
        'tool-window-border': muted_b, 'tool-window-border-inline': muted_b, 'dialog-border': muted_b,
        'tree-indent-guide-border': muted_b, 'control-border-disabled': muted_b,
        'popup-border': border, 'popup-border-inline': border, 'popup-border-windows': border,
        'main-window-border': border, 'control-border': border, 'inlay-border': border, 'got-it-code-border': border,
        'control-border-raised': ov(P['neutralEmphasis']), 'control-border-small': ov(P['neutralEmphasis']),
        'feedback-border': ovl if dark else border, 'got-it-border': ovl if dark else border,
        'feedback-control-border': border,
        # interaction overlays
        'core-bg-transparent-hovered': hover, 'toolbar-bg-hovered': hover, 'tab-bg-hovered': hover,
        'core-bg-transparent-pressed': press, 'toolbar-bg-pressed': press,
        'core-border-transparent': border, 'toolbar-border': border,
        'selection-bg-active': S['selection'], 'selection-bg-active-muted': S['selection'],
        'selection-bg-inactive': S['selection'], 'selection-bg-hovered': S['hover'],
        'toolbar-selected-bg': mut('accent'), 'toolbar-selected-bg-hovered': mut('accent'),
        'toolbar-selected-bg-active': P['accentEmphasis'],
        'toolbar-run-bg': P['successEmphasis'], 'toolbar-run-bg-hovered': P['successFg'],
        'toolbar-stop-bg': P['dangerEmphasis'], 'toolbar-stop-bg-hovered': P['dangerFg'],
        # tabs (VS Code: active tab = canvas with the orange active border)
        'tab-selected-bg-active': sub('accent'), 'tab-selected-bg-inactive': ov(P['neutralSubtle']),
        'tab-selected-border-active': mut('accent'), 'tab-selected-border-inactive': border,
        # toggles (Primer ToggleSwitch: accent when on)
        'toggle-off-bg': ov(P['neutralMuted']), 'toggle-button-bg': P['fgMuted'], 'toggle-border': ov(P['neutralEmphasis']),
        # icons
        'icon-default-stroke': P['fgMuted'], 'icon-over-accent': P['fgOnEmphasis'], 'icon-green-stroke': P['successFg'],
        'control-border-over-accent': S['alpha'](P['fgOnEmphasis'], .25),
        # search
        'search-match-bg': S['findMatch'],
        'presentation-assistant-bg': P['accentEmphasis'],
        # accents: emphasis / subtle (secondary bg) / muted (secondary border)
        'accent-neutral-bg': P['neutralEmphasis'],
        'accent-ai-bg': sub('done'), 'accent-ai-border': mut('done'),
        'feedback-ai-bg': sub('done', ovl), 'feedback-ai-border': mut('done', ovl),
    }
    for jb, pk in (('brand', 'accent'), ('success', 'success'), ('warning', 'attention'), ('error', 'danger')):
        m[f'accent-{jb}-bg'] = m[f'accent-{jb}-border'] = P[pk + 'Emphasis']
        m[f'accent-{jb}-bg-secondary'] = sub(pk)
        m[f'accent-{jb}-border-secondary'] = mut(pk)
        m[f'control-{jb}-bg'] = m[f'control-{jb}-border'] = P[pk + 'Emphasis']
        m[f'control-{jb}-border-secondary'] = mut(pk)
        m[f'feedback-{jb}-bg'] = sub(pk, ovl)
        m[f'feedback-{jb}-border'] = mut(pk, ovl)
    # layer tokens are theme-relative in Islands (dark: layer-0 = islands; light: layer-0 = frame)
    if dark:
        m.update({'layer-0-bg': cv, 'layer-0-bg-inline': S['subtle'], 'layer-0-border': muted_b, 'layer-0-border-inline': muted_b,
                  'layer-1-bg': frame, 'layer-1-bg-inline': ovl, 'layer-1-border': border, 'layer-1-border-inline': border,
                  'layer-2-bg': ovl, 'layer-2-bg-inline': ovl, 'layer-2-border': border, 'layer-2-border-inline': border})
    else:
        m.update({'layer-0-bg': frame, 'layer-0-bg-inline': cv, 'layer-0-border': border, 'layer-0-border-inline': muted_b,
                  'layer-1-bg': cv, 'layer-1-bg-inline': cv, 'layer-1-border': muted_b, 'layer-1-border-inline': muted_b,
                  'layer-2-bg': cv, 'layer-2-bg-inline': S['subtle'], 'layer-2-border': muted_b, 'layer-2-border-inline': muted_b})
    SEMANTIC_NAMES.update(m)
    return m


def _flip_value(v, colors):
    """Resolve aliases until a semantic token or raw colour; flip raw colours."""
    seen = set()
    while isinstance(v, str) and v not in seen:
        seen.add(v)
        if v in SEMANTIC_NAMES:
            return v
        if v in colors:
            v = colors[v]; continue
        if HEX.fullmatch(v):
            return _flip(v)
        m = INSETS_COLOR.fullmatch(v)
        if m:
            inner = _flip_value(m.group(2), colors)
            return m.group(1) + inner if inner else None
        return None
    return None


def resolve(value, colors, S, sem):
    """Follow a value through the colour table; return the GitHub colour or None if not a colour."""
    v, seen = value, set()
    while isinstance(v, str) and v not in seen:
        seen.add(v)
        if v in sem:
            return sem[v]
        if v in colors:
            v = colors[v]
            continue
        if HEX.fullmatch(v):
            return snap(v if v.startswith('#') else '#' + v, S)
        return None
    return None


def _flip(c):
    """Mirror a raw colour's lightness (light-theme value -> dark-theme counterpart, and back)."""
    rgb, a = _rgba(c if c.startswith('#') else '#' + c)
    h, l, s = colorsys.rgb_to_hls(*[x / 255 for x in rgb])
    return _hex([round(x * 255) for x in colorsys.hls_to_rgb(h, 1 - l, s)], a)


def _by_role(key, S):
    k = key.lower()
    if re.search(r'(foreground|fg|textcolor)$', k): return S['P']['fg']
    if re.search(r'(border|bordercolor|separatorcolor|separator)$', k): return S['borderMuted']
    if re.search(r'(background|backgroundbase|bg|color)$', k): return S['canvas']
    return None


def code_defaults(own=None, other=None):
    """{key: {'light', 'dark'}} for colour keys no JetBrains theme file sets but IDE code reads with a
    hardcoded default (jetbrains/code_defaults.json, see codekeys.py)."""
    p = os.path.join(JB, 'code_defaults.json')
    if not os.path.exists(p):
        return {}
    known = {k.lower() for k in (own if own is not None else chain(True))} | \
            {k.lower() for k in (other if other is not None else chain(False))}
    return {k: v for k, v in json.load(open(p)).items() if k.lower() not in known}


def inherited(dark, S):
    """{key: GitHub colour} for every colour key either JetBrains chain supplies. Keys only the
    opposite chain defines are included too (with raw colours lightness-flipped), so dark and
    light variants share one key set. Keys whose only default is hardcoded in IDE code are
    included with that default (or by role when it is not a literal)."""
    sem = semantic(S, dark)
    own, other = chain(dark), chain(not dark)
    items = list(own.items()) + [(k, (v, c, True)) for k, (v, c) in other.items() if k not in own]
    out = {}
    for k, d in code_defaults(own, other).items():
        c = d['dark' if dark else 'light']
        c = snap(c, S) if c else _by_role(k, S)
        if c:
            out[k] = c
    for k, val in items:
        v, colors = val[0], val[1]
        if len(val) == 3 and isinstance(v, str):  # from the opposite chain
            v = _flip_value(v, colors)
            if v is None:
                continue
        if not isinstance(v, str):
            continue
        m = INSETS_COLOR.fullmatch(v)
        if m:  # e.g. "1,1,1,1,#5A5D63": insets followed by a border colour
            c = resolve(m.group(2), colors, S, sem)
            if c:
                out[k] = m.group(1) + c[:7]
            continue
        c = resolve(v, colors, S, sem)
        if not c and isinstance(v, str) and re.fullmatch(r'[A-Za-z][\w-]*', v):
            c = _by_role(k, S)  # colour name this chain can't resolve (e.g. "panel"): fall back by role
        if c:
            out[k] = c
    return out
