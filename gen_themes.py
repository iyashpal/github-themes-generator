#!/usr/bin/env python3
"""Generate the 11 IntelliJ UI themes + editor schemes from GitHub's VS Code theme
source (primer/github-vscode-theme + @primer/primitives; versions in vsc/UPSTREAM.json,
refreshed by update.py).

Inputs : vsc/vscode.json   (VS Code colors + tokenColors + flattened Primer palette)
         vsc/UPSTREAM.json (upstream release tag and Primer version)
         orig/scheme/      (pre-generator schemes: used only as the attribute-name template)
Outputs: <out>/<variant>.theme.json, <out>/scheme/<variant>.xml
"""
import json, os, re, sys, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import islands_map
import xml.etree.ElementTree as ET
from xml.sax.saxutils import quoteattr

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'out')
VS = json.load(open(os.path.join(HERE, 'vsc/vscode.json')))
ORIG = os.path.join(HERE, 'orig')
sys.path.insert(0, HERE)
import syntax  # noqa: E402  IntelliJ key -> VS Code scope map (see syntax/__init__.py)
# every key JetBrains' bundled Default/Darcula schemes (plus plugin additions) set: all must be
# overridden, or JetBrains colours show through (parity/inventory.py)
INVENTORY = json.load(open(os.path.join(HERE, 'parity/inventory.json')))
UPSTREAM = json.load(open(os.path.join(HERE, 'vsc/UPSTREAM.json')))
SOURCE = f"github-vscode-theme {UPSTREAM['tag'].lstrip('v')} / @primer/primitives {UPSTREAM['primitives']}"

VARIANTS = {  # file stem: (display name, dark?)
    'dark':               ('Github - Dark', True),
    'dark-default':       ('Github - Dark Default', True),
    'dark-dimmed':        ('Github - Dark Dimmed', True),
    'dark-colorblind':    ('Github - Dark Colorblind', True),
    'dark-tritanopia':    ('Github - Dark Tritanopia', True),
    'dark-high-contrast': ('Github - Dark High Contrast', True),
    'light':              ('Github - Light', False),
    'light-default':      ('Github - Light Default', False),
    'light-colorblind':   ('Github - Light Colorblind', False),
    'light-tritanopia':   ('Github - Light Tritanopia', False),
    'light-high-contrast':('Github - Light High Contrast', False),
}

# ---------------------------------------------------------------- color math
def parse(c):
    c = c.lstrip('#').lower()
    if len(c) == 3: c = ''.join(x * 2 for x in c)
    if len(c) == 4: c = ''.join(x * 2 for x in c)
    rgb = tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))
    a = int(c[6:8], 16) / 255 if len(c) == 8 else 1.0
    return rgb, a

def full(c):
    """Normalise any #rgb / #rgba / #rrggbb / #rrggbbaa to lowercase #rrggbb or #rrggbbaa."""
    if not isinstance(c, str) or not re.fullmatch(r'#?[0-9a-fA-F]{3,8}', c): return c
    rgb, a = parse(c)
    return hx(rgb) + ('' if a >= 1 else '%02x' % round(a * 255))

def hx(rgb): return '#' + ''.join('%02x' % max(0, min(255, round(v))) for v in rgb)

def over(c, bg):
    """Precompose a (possibly translucent) color over an opaque background."""
    (r, a), (b, _) = parse(c), parse(bg)
    return hx([r[i] * a + b[i] * (1 - a) for i in range(3)])

def alpha(c, a):
    rgb, _ = parse(c)
    return hx(rgb) + '%02x' % round(a * 255)

def lum(c):
    rgb, _ = parse(c)
    v = [x / 255 for x in rgb]
    v = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in v]
    return 0.2126 * v[0] + 0.7152 * v[1] + 0.0722 * v[2]

def contrast(a, b):
    la, lb = lum(a), lum(b)
    return (max(la, lb) + .05) / (min(la, lb) + .05)

ADJUSTED = []
def ensure(fg, bg, ratio, label='', alts=()):
    """Return fg unchanged if it meets `ratio` on bg; else the first alternative that
    does; else the closest mix toward white/black that does (keeps hue)."""
    fg, bg = over(fg, bg), over(bg, '#000000')
    if contrast(fg, bg) >= ratio: return fg
    for a in alts:
        a = over(a, bg)
        if contrast(a, bg) >= ratio:
            ADJUSTED.append((label, fg, a, round(contrast(fg, bg), 2), round(contrast(a, bg), 2)))
            return a
    target = '#ffffff' if lum(bg) < 0.18 else '#000000'
    rgb, _ = parse(fg); t, _ = parse(target)
    for i in range(1, 101):
        f = i / 100
        c = hx([rgb[k] + (t[k] - rgb[k]) * f for k in range(3)])
        if contrast(c, bg) >= ratio:
            ADJUSTED.append((label, fg, c, round(contrast(fg, bg), 2), round(contrast(c, bg), 2)))
            return c
    return target

def ensure_bg(bg, fg, ratio, label=''):
    """Darken/lighten a fill (keeping its hue) until `fg` text on it meets `ratio`."""
    if contrast(fg, bg) >= ratio: return bg
    target = '#000000' if lum(fg) > 0.18 else '#ffffff'
    rgb, _ = parse(bg); t, _ = parse(target)
    for i in range(1, 101):
        c = hx([rgb[k] + (t[k] - rgb[k]) * i / 100 for k in range(3)])
        if contrast(fg, c) >= ratio:
            ADJUSTED.append((label, bg, c, round(contrast(fg, bg), 2), round(contrast(fg, c), 2)))
            return c
    return target

# ---------------------------------------------------------------- palettes
CLASSIC = json.load(open(os.path.join(HERE, 'vsc/src/classic/colors.json')))

def classic_palette(dark):
    """Semantic palette for the classic (2020) GitHub themes, built from the same
    primer v2 scale the classic VS Code theme uses (reversed for dark)."""
    s = {k: (list(reversed(v)) if dark and isinstance(v, list) else v) for k, v in CLASSIC.items()}
    g, b, gr, y, o, r, p, pk = (s[k] for k in ('gray', 'blue', 'green', 'yellow', 'orange', 'red', 'purple', 'pink'))
    vc = VS['dark' if dark else 'light']['colors']
    if dark:
        P = dict(fg=vc['editor.foreground'], fgMuted=vc['descriptionForeground'], fgSubtle=g[5],
                 fgOnEmphasis='#ffffff', canvas=vc['editor.background'], inset=vc['sideBar.background'],
                 overlay=vc['editorWidget.background'], subtle=g[1], border=vc['sideBar.border'], borderMuted=g[1],
                 accentFg=b[6], accentEmphasis=b[4], successFg=gr[5], successEmphasis=gr[3],
                 attentionFg=y[6], attentionEmphasis=y[2], dangerFg=r[6], dangerEmphasis=r[4],
                 severeFg=o[6], severeEmphasis=o[4], doneFg=p[6], doneEmphasis=p[4],
                 sponsorsEmphasis=pk[4], neutralEmphasis=g[4], neutralEmphasisPlus=g[6],
                 neutralMuted=vc['list.activeSelectionBackground'], neutralSubtle=vc['list.hoverBackground'],
                 btnBg=g[2], btnText=g[8], btnBorder=vc['sideBar.border'], btnHoverBg=g[3],
                 primaryBg=vc['button.background'], primaryText=vc['button.foreground'],
                 primaryHoverBg=vc['button.hoverBackground'], primaryBorder=vc['button.background'],
                 activeBorder=vc['tab.activeBorderTop'])
    else:
        P = dict(fg=vc['editor.foreground'], fgMuted=g[6], fgSubtle=g[5], fgOnEmphasis='#ffffff',
                 canvas=vc['editor.background'], inset=vc['sideBar.background'], overlay=vc['editorWidget.background'],
                 subtle=g[0], border=vc['sideBar.border'], borderMuted='#eaecef',
                 accentFg=b[5], accentEmphasis=b[5], successFg=gr[6], successEmphasis=gr[5],
                 attentionFg=y[8], attentionEmphasis=y[7], dangerFg=r[6], dangerEmphasis=r[5],
                 severeFg=o[6], severeEmphasis=o[5], doneFg=p[5], doneEmphasis=p[5],
                 sponsorsEmphasis=pk[5], neutralEmphasis=g[5], neutralEmphasisPlus=g[9],
                 neutralMuted=vc['list.activeSelectionBackground'], neutralSubtle=vc['list.hoverBackground'],
                 btnBg=g[0], btnText=g[9], btnBorder='#1b1f2326', btnHoverBg=g[1],
                 primaryBg=vc['button.background'], primaryText='#ffffff', primaryHoverBg=vc['button.hoverBackground'],
                 primaryBorder='#1b1f2326', activeBorder=vc['tab.activeBorderTop'])
    for k in ('accent', 'success', 'attention', 'danger', 'severe', 'done'):
        P[k + 'Muted'] = alpha(P[k + 'Emphasis'], .4)
        P[k + 'Subtle'] = alpha(P[k + 'Emphasis'], .15 if dark else .1)
    P['scale'] = {k: s[k] for k in ('gray', 'blue', 'green', 'yellow', 'orange', 'red', 'purple', 'pink')}
    P['scale']['red_'] = s['red']
    return P

def primer_palette(name):
    p = VS[name]['primer']
    P = dict(fg=p['fg.default'], fgMuted=p['fg.muted'], fgSubtle=p['fg.subtle'], fgOnEmphasis=p['fg.onEmphasis'],
             canvas=p['canvas.default'], inset=p['canvas.inset'], overlay=p['canvas.overlay'], subtle=p['canvas.subtle'],
             border=p['border.default'], borderMuted=p['border.muted'],
             neutralEmphasis=p['neutral.emphasis'], neutralEmphasisPlus=p['neutral.emphasisPlus'],
             neutralMuted=p['neutral.muted'], neutralSubtle=p['neutral.subtle'], sponsorsEmphasis=p['sponsors.emphasis'],
             btnBg=p['btn.bg'], btnText=p['btn.text'], btnBorder=p['btn.border'], btnHoverBg=p['btn.hoverBg'],
             primaryBg=p['btn.primary.bg'], primaryText=p['btn.primary.text'], primaryHoverBg=p['btn.primary.hoverBg'],
             primaryBorder=p['btn.primary.border'], activeBorder=p['primer.border.active'])
    for k in ('accent', 'success', 'attention', 'danger', 'severe', 'done'):
        for lvl in ('fg', 'emphasis', 'muted', 'subtle'):
            P[k + lvl[0].upper() + lvl[1:]] = p[f'{k}.{lvl}']
    P['scale'] = {c: [p[f'scale.{c}.{i}'] for i in range(10)] for c in
                  ('gray', 'blue', 'green', 'yellow', 'orange', 'red', 'purple', 'pink')}
    return P

# ---------------------------------------------------------------- token roles
def token(vs, *scopes):
    """Foreground of the last tokenColors rule whose scope list contains one of `scopes`."""
    hit = None
    for t in vs['tokenColors']:
        sc = t['scope'] if isinstance(t['scope'], list) else [t['scope']]
        if any(s in sc for s in scopes) and 'foreground' in t['settings']:
            hit = t['settings']['foreground']
    return hit

def roles(name):
    vs = VS[name]; c = vs['colors']
    R = dict(
        fg=c['editor.foreground'],
        comment=token(vs, 'comment'),
        keyword=token(vs, 'keyword'),
        string=token(vs, 'string'),
        constant=token(vs, 'constant'),
        entity=token(vs, 'entity.name') if name not in ('dark', 'light') else token(vs, 'entity.name'),
        variable=token(vs, 'variable'),
        function=token(vs, 'entity.name.function') or token(vs, 'entity'),
        tag=token(vs, 'entity.name.tag'),
        invalid=token(vs, 'invalid.illegal'),
        heading=token(vs, 'markup.heading'),
        quote=token(vs, 'markup.quote'),
        escape=token(vs, 'constant.character', 'constant.other.placeholder') or token(vs, 'keyword'),
        regexEscape=token(vs, 'string.regexp constant.character.escape'),
        support=token(vs, 'support'),
        property=token(vs, 'meta.property-name'),
        jsonKey=token(vs, 'support.type.property-name.json') or token(vs, 'entity.name.tag'),
        link=token(vs, 'constant.other.reference.link', 'string.other.link') or token(vs, 'string'),
        listMarker=token(vs, 'punctuation.definition.list.begin.markdown'),
        raw=token(vs, 'markup.inline.raw'),
        inserted=token(vs, 'markup.inserted'), deleted=token(vs, 'markup.deleted'),
        changed=token(vs, 'markup.changed'), diffRange=token(vs, 'meta.diff.range'),
        diffHeader=token(vs, 'meta.diff.header'),
    )
    # classic themes have no separate orange "entity.name": classes are purple there
    if name in ('dark', 'light'):
        R['entity'] = token(vs, 'entity')
    R = {k: (v.lower() if v else R['fg']) for k, v in R.items()}
    bg = c['editor.background']
    for k in list(R):  # syntax text must meet WCAG AA on the editor background
        R[k] = ensure(R[k], bg, 4.5, f'{name}:syntax.{k}')
    return R

# ---------------------------------------------------------------- UI theme
def ui_theme(name, display, dark):
    P = classic_palette(dark) if name in ('dark', 'light') else primer_palette(name)
    vc = VS[name]['colors']
    hc = 'high-contrast' in name
    # JetBrains Islands structure: the editor and tool windows are islands on one surface
    # (canvas.default = VS Code editor background); the frame (toolbar, stripes, status bar)
    # is a distinct surface (lighter canvas.subtle in dark, darker canvas.inset in light),
    # so islands are separated by colour, not by border lines.
    cv, ovl = P['canvas'], P['overlay']
    ins = cv
    frame = next((over(P[k], cv) for k in (('subtle', 'overlay', 'inset') if dark else ('inset', 'subtle', 'neutralSubtle'))
                  if contrast(over(P[k], cv), cv) >= 1.05), over(P['neutralSubtle'], cv))
    o = lambda c, bg=None: over(c, bg or cv)
    oi = lambda c: over(c, ins)
    oo = lambda c: over(c, ovl)

    # editor/text selection: GitHub themes leave editor.selectionBackground unset outside
    # high contrast, so VS Code falls back to its defaults; we use the same values.
    if hc:
        sel_bg, sel_fg = P['neutralEmphasisPlus'], P['fgOnEmphasis']
    else:  # theme.js: "editor.selectionBackground": alpha(color.accent.fg, 0.2)
        sel_bg, sel_fg = o(alpha(P['accentFg'], .2)), P['fg']

    P['primaryBg'] = ensure_bg(P['primaryBg'], P['primaryText'], 4.5, f'{name}:primaryButton')
    P['accentEmphasis'] = ensure(P['accentEmphasis'], cv, 3.0, f'{name}:focusRing')
    # Active-tab underline: Primer accent blue (as Islands' brand-blue selected tab), not GitHub's
    # coral border.active, which reads oddly in the IDE and fails 3:1 on light themes.
    P['activeBorder'] = P['accentEmphasis']
    # secondary text sits on every surface (islands, frame, popups, inline chips): AA on each
    # (Primer's dimmed fg.muted is 3.3-3.9:1 there)
    for surf in (cv, frame, ovl, over(P['subtle'], cv)):
        P['fgMuted'] = ensure(P['fgMuted'], surf, 4.5, f'{name}:mutedForeground')
    colors = {
        'foreground': P['fg'], 'mutedForeground': P['fgMuted'], 'subtleForeground': P['fgSubtle'],
        'onEmphasisForeground': P['fgOnEmphasis'],
        'background': cv, 'frameBackground': frame, 'overlayBackground': ovl, 'subtleBackground': o(P['subtle']),
        'borderColor': o(P['border']), 'mutedBorderColor': o(P['borderMuted']),
        'accentColor': P['accentFg'], 'accentEmphasis': P['accentEmphasis'],
        'successColor': P['successFg'], 'warningColor': P['attentionFg'], 'dangerColor': P['dangerFg'],
        'selectionBackground': oi(P['neutralMuted']), 'hoverBackground': oi(P['neutralSubtle']),
        'primaryColor': P['primaryBg'], 'primaryForeground': P['primaryText'],
        'activeBorderColor': P['activeBorder'],
    }
    if contrast(colors['selectionBackground'], ins) <= contrast(colors['hoverBackground'], ins) * 1.08:
        for a in range(20, 80, 2):
            cand = oi(alpha(P['neutralEmphasis'], a / 100))
            if contrast(cand, ins) > contrast(colors['hoverBackground'], ins) * 1.15:
                colors['selectionBackground'] = cand; break
    # placeholder text: fg.subtle, faded (not high contrast) toward the canvas down to 2.5:1
    placeholder = 'subtleForeground'
    if not hc:
        for a in range(100, 29, -2):
            cand = over(alpha(P['fgSubtle'], a / 100), cv)
            if contrast(cand, cv) < 2.5: break
            placeholder = cand
    C = colors
    fg, mfg, sfg = 'foreground', 'mutedForeground', 'subtleForeground'
    sel, hov = 'selectionBackground', 'hoverBackground'
    # popup/menu selection: its text is the default foreground (AA)
    sel_ovl = ensure_bg(oo(P['neutralMuted']), P['fg'], 4.5, f'{name}:popupSelection')
    tint = lambda k, kind='Subtle', bg=None: over(P[k + kind], bg or cv)
    fill08, fill12 = o(alpha(P['fg'], .08)), o(alpha(P['fg'], .12))
    frame08, frame12 = over(alpha(P['fg'], .08), frame), over(alpha(P['fg'], .12), frame)
    clear = '#00000000'  # Islands: frame/stripe/status-bar/toolbar borders are transparent
    feedback_border = 'overlayBackground' if dark else 'borderColor'
    # text that must stay readable: Primer value unless it fails AA on its surface
    t = lambda c, bg, r=4.5, lbl='', alts=(): ensure(C.get(c, c), C.get(bg, bg), r, f'{name}:{lbl}', alts)
    sc = P['scale']
    filecolor = lambda c: over(alpha(sc[c][5], .22 if dark else .16), ins)

    ui = {
        '*': {
            'foreground': fg, 'background': 'background',
            'hoverBackground': hov, 'selectionBackground': sel, 'selectionForeground': fg,
            'selectionInactiveBackground': sel, 'selectionInactiveForeground': fg,
            'lightSelectionBackground': tint('accent', bg=ins),
            'disabledText': sfg, 'disabledForeground': sfg, 'inactiveForeground': sfg,
            'inactiveBackground': 'subtleBackground', 'disabledBackground': 'subtleBackground',
            'disabledBorderColor': 'mutedBorderColor',
            'separatorColor': 'borderColor', 'separatorForeground': mfg,
            'borderColor': 'mutedBorderColor', 'focusColor': 'accentEmphasis',
        },
        # translucent so they read the same on islands and on the frame: pressed is also the stripe button
        # of an open but unfocused tool window (SquareStripeButtonLook), so it must show on frameBackground
        'ActionButton.hoverBackground': full(alpha(P['fg'], .08)), 'ActionButton.hoverBorderColor': clear,
        'ActionButton.pressedBackground': full(alpha(P['fg'], .16)), 'ActionButton.pressedBorderColor': clear,
        'ActionButton.separatorColor': 'borderColor',
        'alt.Island.borderColor': 'background', 'alt.MainWindow.background': 'frameBackground',
        'alt.MainToolbar.background': 'frameBackground', 'alt.StatusBar.background': 'frameBackground',
        'alt.ToolWindow.Stripe.background': 'frameBackground', 'alt.ToolWindow.background': 'background',
        'alt.ToolWindow.Header.inactiveBackground': 'background',
        'Banner.infoBackground': tint('accent'), 'Banner.infoBorderColor': tint('accent', 'Muted'),
        'Banner.successBackground': tint('success'), 'Banner.successBorderColor': tint('success', 'Muted'),
        'Banner.warningBackground': tint('attention'), 'Banner.warningBorderColor': tint('attention', 'Muted'),
        'Banner.errorBackground': tint('danger'), 'Banner.errorBorderColor': tint('danger', 'Muted'),
        'BigSpinner.background': 'background',
        'Bookmark.Mnemonic.iconForeground': fg, 'Bookmark.MnemonicAvailable.borderColor': 'borderColor',
        'Bookmark.MnemonicAssigned.background': tint('attention'),
        'Bookmark.MnemonicAssigned.foreground': fg,
        'Bookmark.MnemonicCurrent.background': P['accentEmphasis'],
        'Bookmark.MnemonicCurrent.foreground': None,  # filled below with an AA check
        'Borders.color': 'mutedBorderColor', 'Borders.ContrastBorderColor': 'mutedBorderColor', 'Breakpoint.iconHoverAlpha': 0.35,
        'Button.foreground': P['btnText'], 'Button.loadingForeground': mfg,
        'Button.startBackground': o(P['btnBg']), 'Button.endBackground': o(P['btnBg']),
        'Button.startBorderColor': o(P['btnBorder']), 'Button.endBorderColor': o(P['btnBorder']),
        'Button.focusedBorderColor': o(P['btnBg']),
        'Button.default.foreground': 'primaryForeground', 'Button.default.loadingForeground': 'primaryForeground',
        'Button.default.startBackground': 'primaryColor', 'Button.default.endBackground': 'primaryColor',
        'Button.default.startBorderColor': 'primaryColor', 'Button.default.endBorderColor': 'primaryColor',
        'Button.default.focusedBorderColor': 'background', 'Button.default.focusColor': 'accentColor',
        'CheckBox.background': 'background', 'CheckBox.foreground': fg, 'CheckBox.disabledText': sfg,
        'CheckBoxMenuItem.foreground': fg, 'CheckBoxMenuItem.background': 'overlayBackground',
        'CheckBoxMenuItem.selectionForeground': fg, 'CheckBoxMenuItem.selectionBackground': sel_ovl,
        'CheckBoxMenuItem.disabledForeground': sfg, 'CheckBoxMenuItem.disabledBackground': 'overlayBackground',
        'CheckBoxMenuItem.acceleratorForeground': None, 'CheckBoxMenuItem.acceleratorSelectionForeground': fg,
        'ColorChooser.background': 'background', 'ColorChooser.foreground': fg,
        'ColorChooser.swatchesDefaultRecentColor': 'borderColor',
        'ComboBox.background': 'background', 'ComboBox.foreground': fg,
        'ComboBox.nonEditableBackground': 'overlayBackground',
        'ComboBox.ArrowButton.background': 'background', 'ComboBox.ArrowButton.iconColor': mfg,
        'ComboBox.ArrowButton.disabledIconColor': sfg, 'ComboBox.ArrowButton.nonEditableBackground': 'overlayBackground',
        'ComboBoxButton.background': 'overlayBackground',
        'ComboPopup.border': '1,1,1,1,' + o(P['border']),
        'CompletionPopup.foreground': fg, 'CompletionPopup.matchForeground': None,
        'CompletionPopup.Advertiser.foreground': None, 'CompletionPopup.Advertiser.background': 'overlayBackground',
        'CompletionPopup.Advertiser.borderInsets': '4,12,3,8',
        'ComplexPopup.Header.background': 'overlayBackground',
        'CompletionPopup.background': 'overlayBackground', 'CompletionPopup.selectionBackground': sel_ovl,
        'CompletionPopup.selectionInactiveBackground': sel_ovl,
        'ParameterInfo.background': 'overlayBackground', 'ParameterInfo.currentOverloadBackground': sel_ovl,
        'Tooltip.Learning.background': 'overlayBackground', 'Tooltip.Learning.borderColor': feedback_border,
        'Tooltip.Learning.spanBackground': o(P['neutralMuted'], ovl),
        'ToolWindow.HeaderTab.selectedBackground': 'background', 'ToolWindow.HeaderTab.selectedInactiveBackground': 'background',
        'Table.lightSelectionBackground': tint('accent'), 'Table.lightSelectionInactiveBackground': sel,
        'Plugins.lightSelectionBackground': tint('accent'),
        'Component.borderColor': 'borderColor', 'Component.focusedBorderColor': 'background',
        'Component.focusColor': 'accentEmphasis',
        # editor placeholders (commit message, etc.) paint with this; VS Code's input.placeholderForeground = fg.subtle
        'Component.infoForeground': placeholder,
        'Component.errorFocusColor': 'dangerColor', 'Component.inactiveErrorFocusColor': tint('danger', 'Muted'),
        'Component.warningFocusColor': 'warningColor', 'Component.inactiveWarningFocusColor': tint('attention', 'Muted'),
        'Counter.background': 'accentEmphasis', 'Counter.foreground': None,
        'Debugger.Variables.valueForeground': vc.get('debugTokenExpression.value', P['accentFg']),
        'Debugger.Variables.collectingDataForeground': mfg, 'Debugger.Variables.evaluatingExpressionForeground': mfg,
        'Debugger.Variables.changedValueForeground': 'warningColor', 'Debugger.Variables.modifyingValueForeground': mfg,
        'Debugger.Variables.errorMessageForeground': 'dangerColor', 'Debugger.Variables.exceptionForeground': 'dangerColor',
        'Debugger.Variables.typeForeground': mfg, 'Debugger.EvaluateExpression.background': 'background',
        'DebuggerPopup.borderColor': 'borderColor', 'DebuggerTabs.underlineHeight': 2,
        'DebuggerTabs.underlinedTabBackground': 'background',
        'DefaultTabs.background': 'background', 'DefaultTabs.hoverBackground': hov,
        'DefaultTabs.borderColor': 'mutedBorderColor', 'DefaultTabs.underlineColor': 'activeBorderColor',
        'DefaultTabs.underlineHeight': 2, 'DefaultTabs.underlinedTabBackground': 'background',
        'DefaultTabs.inactiveUnderlineColor': 'borderColor', 'DefaultTabs.underlinedTabForeground': fg,
        'DragAndDrop.borderColor': 'accentEmphasis', 'DragAndDrop.rowBackground': tint('accent', 'Muted', ins),
        'Editor.SearchField.borderInsets': '7,10,7,8', 'Editor.SearchField.background': 'background',
        'Editor.Toolbar.borderColor': 'mutedBorderColor', 'EditorPane.splitBorder': 'mutedBorderColor',
        # Islands draws the selected editor tab as a pill: accent fill + accent border (focused group),
        # neutral fill + border (unfocused group). Height/arc are left to Islands.
        'EditorTabs.background': 'background', 'EditorTabs.hoverBackground': fill08,
        'EditorTabs.hoverInactiveBackground': fill08,
        'EditorTabs.underlineColor': 'activeBorderColor',
        'EditorTabs.underlinedTabBackground': tint('accent'), 'EditorTabs.selectedBackground': tint('accent'),
        'EditorTabs.underlinedBorderColor': tint('accent', 'Muted'),
        'EditorTabs.inactiveUnderlinedTabBackground': o(P['neutralSubtle']),
        'EditorTabs.inactiveUnderlinedTabBorderColor': 'borderColor',
        'EditorTabs.inactiveUnderlineColor': 'borderColor', 'EditorTabs.borderColor': 'mutedBorderColor', 'EditorTabs.underTabsBorderColor': 'mutedBorderColor',
        'EditorTabs.underlinedTabForeground': fg,
        'FileColor.Yellow': filecolor('yellow'), 'FileColor.Green': filecolor('green'),
        'FileColor.Gray': filecolor('gray'), 'FileColor.Blue': filecolor('blue'),
        'FileColor.Orange': filecolor('orange'), 'FileColor.Rose': filecolor('pink'),
        'FileColor.Violet': filecolor('purple'),
        'FormattedTextField.foreground': fg, 'FormattedTextField.background': 'background',
        'FormattedTextField.caretForeground': vc.get('editorCursor.foreground', P['accentFg']),
        'FormattedTextField.selectionForeground': sel_fg, 'FormattedTextField.selectionBackground': sel_bg,
        'FormattedTextField.inactiveBackground': 'subtleBackground', 'FormattedTextField.inactiveForeground': sfg,
        'GotItTooltip.background': 'overlayBackground', 'GotItTooltip.foreground': fg,
        'GotItTooltip.borderColor': feedback_border, 'GotItTooltip.shortcutForeground': mfg,
        'GotItTooltip.linkForeground': 'accentColor',
        'Group.separatorColor': 'mutedBorderColor', 'Group.disabledSeparatorColor': 'mutedBorderColor',
        'GutterTooltip.infoForeground': mfg, 'GutterTooltip.lineSeparatorColor': 'mutedBorderColor',
        'HelpTooltip.borderColor': 'borderColor',
        'IconBadge.borderWidth': 1.5, 'IconBadge.warningBackground': P['attentionEmphasis'],
        'IconBadge.infoBackground': P['accentEmphasis'], 'IconBadge.successBackground': P['successEmphasis'],
        'IconBadge.errorBackground': P['dangerEmphasis'], 'IconBadge.dotRadius': 3.5,
        'IconBadge.dotX': 16.5, 'IconBadge.dotY': 3.5,
        'InformationHint.borderColor': 'borderColor', 'InplaceRefactoringPopup.borderColor': 'borderColor',
        'Island.borderColor': 'background',
        'Label.errorForeground': None, 'Label.successForeground': None, 'Label.infoForeground': mfg,
        'Lesson.shortcutBackground': 'subtleBackground',
        'Link.activeForeground': None, 'Link.hoverForeground': None, 'Link.pressedForeground': None,
        'Link.visitedForeground': None, 'Link.secondaryForeground': mfg,
        'List.Button.separatorColor': 'borderColor', 'List.Button.separatorInset': 4,
        'List.Button.hoverBackground': sel, 'List.Button.leftRightInset': 8,
        'List.Tag.background': 'subtleBackground', 'List.Tag.foreground': mfg,
        'List.selectionBackground': sel, 'List.selectionInactiveBackground': sel, 'List.hoverBackground': hov,
        'MainMenu.background': 'overlayBackground',
        'MainToolbar.separatorColor': 'borderColor', 'MainToolbar.borderColor': clear, 'MainToolbar.background': 'frameBackground',
        'MainToolbar.inactiveBackground': 'frameBackground', 'MainToolbar.Icon.background': 'frameBackground',
        'MainToolbar.Icon.hoverBackground': frame08, 'MainToolbar.Icon.pressedBackground': frame12,
        'MainToolbar.Dropdown.background': 'frameBackground', 'MainToolbar.Dropdown.hoverBackground': frame08,
        'MainToolbar.Dropdown.pressedBackground': frame12,
        'MainWindow.background': 'frameBackground',
        'MemoryIndicator.allocatedBackground': 'subtleBackground',
        'MemoryIndicator.usedBackground': o(alpha(P['neutralEmphasis'], .5), o(P['subtle'])),
        'Menu.separatorColor': 'mutedBorderColor', 'Menu.borderColor': 'borderColor',
        'Menu.borderInsets': '6,1,6,1', 'Menu.Selection.innerInsets': '0,6,0,6',
        'Menu.background': 'overlayBackground', 'MenuBar.borderColor': 'mutedBorderColor',
        'MenuItem.selectionBackground': sel_ovl, 'MenuItem.acceleratorForeground': None,
        'PopupMenu.background': 'overlayBackground',
        'NavBar.borderColor': 'mutedBorderColor',
        'Notification.errorForeground': None, 'Notification.errorBackground': tint('danger', bg=ovl),
        'Notification.errorBorderColor': tint('danger', 'Muted', ovl),
        'Notification.background': 'overlayBackground', 'Notification.borderColor': feedback_border,
        'Notification.linkForeground': None, 'Notification.borderInsets': '4,4,4,0',
        'Notification.Button.background': o(P['btnBg'], ovl), 'Notification.Button.borderColor': o(P['btnBorder'], ovl),
        'Notification.Button.foreground': P['btnText'],
        'Notification.MoreButton.background': 'overlayBackground',
        'Notification.MoreButton.innerBorderColor': feedback_border, 'Notification.MoreButton.foreground': mfg,
        'Notification.ToolWindow.informativeForeground': fg,
        'Notification.ToolWindow.informativeBackground': tint('accent', bg=ins),
        'Notification.ToolWindow.informativeBorderColor': tint('accent', 'Muted', ins),
        'Notification.ToolWindow.errorForeground': fg,
        'Notification.ToolWindow.errorBackground': tint('danger', bg=ins),
        'Notification.ToolWindow.errorBorderColor': tint('danger', 'Muted', ins),
        'Notification.ToolWindow.warningForeground': fg,
        'Notification.ToolWindow.warningBackground': tint('attention', bg=ins),
        'Notification.ToolWindow.warningBorderColor': tint('attention', 'Muted', ins),
        'NotificationsToolwindow.newNotification.background': tint('accent', bg=ins),
        'NotificationsToolwindow.newNotification.hoverBackground': hov,
        'NotificationsToolwindow.Notification.hoverBackground': hov,
        'OnePixelDivider.background': 'mutedBorderColor',
        'Panel.background': 'background',
        'Plugins.background': 'background', 'Plugins.borderColor': 'mutedBorderColor', 'Plugins.hoverBackground': hov,
        'Plugins.tagBackground': 'subtleBackground', 'Plugins.tagForeground': mfg,
        'Plugins.eapTagBackground': tint('attention'), 'Plugins.disabledForeground': sfg,
        'Plugins.Button.installForeground': 'primaryForeground', 'Plugins.Button.installBackground': 'primaryColor',
        'Plugins.Button.installBorderColor': 'primaryColor',
        'Plugins.Button.installFillBackground': 'primaryColor', 'Plugins.Button.installFillForeground': 'primaryForeground',
        'Plugins.Button.installFocusedBackground': o(P['primaryHoverBg']),
        'Plugins.Button.updateBackground': 'primaryColor',
        'Plugins.Button.updateBorderColor': 'primaryColor',
        'Plugins.Button.updateForeground': 'primaryForeground',
        'Plugins.SearchField.background': 'background', 'Plugins.SectionHeader.background': 'background',
        'Plugins.SectionHeader.foreground': mfg, 'Plugins.Tab.hoverBackground': hov,
        'Plugins.Tab.selectedBackground': sel, 'Plugins.Tab.selectedForeground': fg,
        'Popup.borderWidth': 1, 'Popup.paintBorder': True, 'Popup.borderColor': 'borderColor',
        'Popup.inactiveBorderColor': 'borderColor',
        'Popup.Advertiser.foreground': None, 'Popup.Advertiser.background': 'overlayBackground',
        'Popup.Advertiser.borderColor': 'overlayBackground',
        'Popup.Header.activeBackground': 'overlayBackground', 'Popup.Header.inactiveBackground': 'overlayBackground',
        'Popup.Header.inactiveForeground': None, 'Popup.background': 'overlayBackground',
        'PopupMenu.Selection.innerInsets': '0,6,0,6',
        'ProblemsView.projectAnalysisButtonBackground': o(P['btnBg']),
        'ProgressBar.trackColor': o(P['neutralMuted']),
        'ProgressBar.progressColor': 'accentEmphasis', 'ProgressBar.indeterminateStartColor': 'accentEmphasis',
        'ProgressBar.indeterminateEndColor': 'accentColor',
        'ProgressBar.passedColor': P['successEmphasis'], 'ProgressBar.passedEndColor': P['successFg'],
        'ProgressBar.failedColor': P['dangerEmphasis'], 'ProgressBar.failedEndColor': P['dangerFg'],
        'RunWidget.foreground': fg, 'RunWidget.runningBackground': tint('success', 'Muted', frame),
        'RunWidget.hoverBackground': frame08, 'RunWidget.pressedBackground': frame12,
        'ScrollBar.background': 'background', 'ScrollPane.background': 'background',
        'ScrollBar.thumbColor': vc['scrollbarSlider.background'], 'ScrollBar.hoverThumbColor': vc['scrollbarSlider.hoverBackground'],
        'ScrollBar.Mac.thumbColor': vc['scrollbarSlider.background'], 'ScrollBar.Mac.hoverThumbColor': vc['scrollbarSlider.hoverBackground'],
        'ScrollBar.Transparent.thumbColor': vc['scrollbarSlider.background'],
        'ScrollBar.Transparent.hoverThumbColor': vc['scrollbarSlider.hoverBackground'],
        'ScrollBar.Mac.Transparent.thumbColor': vc['scrollbarSlider.background'],
        'ScrollBar.Mac.Transparent.hoverThumbColor': vc['scrollbarSlider.hoverBackground'],
        **{f'ScrollBar.{p}{s}ThumbBorderColor'.replace('.hoverThumb', '.hoverThumb').replace('.Thumb', '.thumb'):
           vc['scrollbarSlider.' + ('hoverBackground' if s else 'background')]
           for p in ('', 'Transparent.', 'Mac.', 'Mac.Transparent.') for s in ('', 'hover')},
        'SearchEverywhere.List.settingsBackground': 'overlayBackground',
        'SearchEverywhere.Header.background': 'overlayBackground',
        'SearchEverywhere.Tab.selectedBackground': sel_ovl, 'SearchEverywhere.Tab.selectedForeground': fg,
        'SearchEverywhere.Advertiser.foreground': None, 'SearchEverywhere.Advertiser.background': 'overlayBackground',
        'SearchEverywhere.Advertiser.borderInsets': '6,20,6,20',
        'SearchField.errorForeground': None, 'SearchField.errorBackground': tint('danger'),
        'SearchMatch.startBackground': o(vc['editor.findMatchBackground']),
        'SearchMatch.endBackground': o(vc['editor.findMatchBackground']),
        'SearchOption.selectedBackground': o(alpha(P['accentEmphasis'], .4)),
        'SearchOption.selectedHoveredBackground': o(alpha(P['accentEmphasis'], .5)),
        'SearchOption.selectedPressedBackground': o(alpha(P['accentEmphasis'], .6)),
        'SegmentedButton.selectedStartBorderColor': 'borderColor', 'SegmentedButton.selectedEndBorderColor': 'borderColor',
        'SegmentedButton.selectedButtonColor': o(P['btnBg']),
        'SegmentedButton.focusedSelectedButtonColor': tint('accent'),
        'SidePanel.background': 'background',
        'SpeedSearch.foreground': fg, 'SpeedSearch.background': 'overlayBackground',
        'SpeedSearch.borderColor': 'borderColor', 'SpeedSearch.errorForeground': None,
        'StatusBar.background': 'frameBackground', 'StatusBar.borderColor': clear,
        'StatusBar.Widget.hoverBackground': frame08, 'StatusBar.Widget.pressedBackground': frame12,
        'TabbedPane.background': 'background', 'TabbedPane.tabSelectionArc': 4,
        'TabbedPane.hoverColor': hov, 'TabbedPane.contentAreaColor': 'mutedBorderColor',
        'TabbedPane.focusColor': 'accentEmphasis', 'TabbedPane.underlineColor': 'activeBorderColor',
        'Table.gridColor': 'mutedBorderColor', 'Table.stripeColor': o(alpha(P['neutralSubtle'], parse(P['neutralSubtle'])[1] * .6)) if len(P['neutralSubtle']) == 9 else o(P['subtle']),
        'Table.selectionBackground': sel, 'Table.selectionInactiveBackground': sel, 'Table.hoverBackground': hov,
        'TableHeader.background': 'subtleBackground',
        'TableHeader.bottomSeparatorColor': 'mutedBorderColor', 'TableHeader.separatorColor': 'mutedBorderColor',
        'Tag.background': 'subtleBackground',
        'TextArea.selectionForeground': sel_fg, 'TextArea.selectionBackground': sel_bg,
        'TextField.selectionForeground': sel_fg, 'TextField.selectionBackground': sel_bg,
        'TextField.background': 'background',
        'TextPane.selectionForeground': sel_fg, 'TextPane.selectionBackground': sel_bg, 'TextPane.background': 'background',
        'TipOfTheDay.Image.borderColor': 'mutedBorderColor',
        'TitlePane.Button.hoverBackground': frame08, 'TitlePane.background': 'frameBackground',
        'ToolBar.verticalToolbarInsets': '7,4,7,4', 'ToolBar.horizontalToolbarInsets': '4,7,4,7',
        'ToolBar.background': 'background', 'ToolBar.separatorColor': 'borderColor', 'Separator.separatorColor': 'borderColor',
        'ToolTip.background': 'overlayBackground', 'ToolTip.borderColor': feedback_border, 'ToolTip.foreground': fg,
        'ToolTip.infoForeground': None, 'ToolTip.shortcutForeground': None,
        'ToolTip.Actions.background': 'overlayBackground',
        'ToolWindow.background': 'background', 'ToolWindow.Header.background': 'background',
        'ToolWindow.Header.inactiveBackground': 'background',
        'ToolWindow.HeaderTab.underlinedTabBackground': 'background',
        'ToolWindow.HeaderTab.underlineColor': 'activeBorderColor',
        'ToolWindow.HeaderTab.inactiveUnderlineColor': 'borderColor',
        'ToolWindow.HeaderTab.hoverBackground': hov, 'ToolWindow.HeaderTab.hoverInactiveBackground': hov,
        'ToolWindow.Button.selectedForeground': fg, 'ToolWindow.Button.selectedBackground': over(alpha(P['fg'], .24), frame),  # focused; stronger than pressed
        'ToolWindow.Button.hoverBackground': over(P['neutralSubtle'], frame),
        'ToolWindow.Header.borderColor': 'mutedBorderColor', 'ToolWindow.borderColor': clear, 'ToolWindow.Stripe.borderColor': clear, 'ToolWindow.Stripe.separatorColor': 'borderColor', 'ToolWindow.Stripe.background': 'frameBackground',
        'Tree.rowHeight': 24, 'Tree.hash': 'mutedBorderColor', 'Tree.background': 'background',
        'Tree.selectionBackground': sel, 'Tree.selectionInactiveBackground': sel, 'Tree.hoverBackground': hov,
        'Tree.hoverInactiveBackground': hov,
        'UnattendedHostStatus.warningBackground': P['attentionEmphasis'], 'UnattendedHostStatus.warningForeground': None,
        'UnattendedHostStatus.dangerBackground': P['dangerEmphasis'],
        'ValidationTooltip.errorBackground': tint('danger', bg=ovl), 'ValidationTooltip.errorBorderColor': tint('danger', 'Muted', ovl),
        'ValidationTooltip.warningBackground': tint('attention', bg=ovl),
        'ValidationTooltip.warningBorderColor': tint('attention', 'Muted', ovl),
        'VersionControl.Log.Commit.currentBranchBackground': tint('accent', bg=ins),
        'VersionControl.Log.Commit.unmatchedForeground': sfg,
        'VersionControl.Log.Commit.hoveredBackground': hov,
        'VersionControl.FileHistory.Commit.selectedBranchBackground': tint('accent', bg=ins),
        'VersionControl.MarkerPopup.borderInsets': '6,8,6,10', 'VersionControl.MarkerPopup.borderColor': 'borderColor',
        'WelcomeScreen.background': 'background', 'WelcomeScreen.borderColor': 'mutedBorderColor',
        'WelcomeScreen.footerBackground': 'background', 'WelcomeScreen.footerForeground': mfg,
        'WelcomeScreen.headerBackground': 'background', 'WelcomeScreen.headerForeground': fg,
        'WelcomeScreen.separatorColor': 'mutedBorderColor', 'WelcomeScreen.groupIconBorderColor': 'mutedBorderColor',
        'WelcomeScreen.Projects.background': 'background', 'WelcomeScreen.Projects.selectionBackground': sel,
        'WelcomeScreen.Projects.selectionInactiveBackground': sel,
        'WelcomeScreen.Projects.actions.background': 'background',
        'WelcomeScreen.Projects.actions.selectionBackground': sel,
        'WelcomeScreen.Details.background': 'background', 'WelcomeScreen.SidePanel.background': 'frameBackground',
    }
    if len(P['neutralSubtle']) != 9:  # classic: opaque hover colour
        ui['Table.stripeColor'] = o(P['subtle'])

    # keys no JetBrains theme sets; IDE code falls back to a hardcoded JetBrains colour
    # (jetbrains/code_defaults.json). The rest of them snap to the nearest Primer colour below.
    ui.update({
        'EditorTabs.underlinedTabInactiveForeground': fg,  # selected tab text while the editor is unfocused
        'ProgressIcon.color': mfg,  # loading spinner
        'ProgressBar.warningColor': P['attentionEmphasis'], 'ProgressBar.warningEndColor': 'warningColor',
        'Toolbar.Floating.borderColor': 'borderColor',
        'IconBadge.newUiBackground': P['doneEmphasis'],
        'VersionControl.RefLabel.bookmarkBackground': P['attentionEmphasis'],
        'VersionControl.Merge.Badge.infoBackground': o(P['neutralMuted']),
        'VersionControl.Merge.Badge.modifiedItemBackground': tint('accent'),
        'Review.LineFrame.BorderColor': 'accentEmphasis', 'Review.Reaction.Background': o(P['neutralMuted']),
        'Review.AI.Background': P['doneEmphasis'],
        'Plugins.suggestedLabelBackground': tint('success'), 'Plugins.ultimateTagForeground': fg,
        'Plugins.ScreenshotPagination.CurrentImage.fillColor': mfg,
        'RunToolbar.Run.activeBackground': tint('success', 'Muted', frame),
        'RunToolbar.Debug.activeBackground': tint('attention', 'Muted', frame),
        'RunToolbar.Profile.activeBackground': tint('accent', 'Muted', frame),
        'AIA.Elicitation.choice.focusedBorderColor': 'accentEmphasis',
        'AIA.Elicitation.choice.selectedBackground': tint('accent'),
        'AIA.Elicitation.choice.selectedBorderColor': 'accentEmphasis',
        'AIA.Elicitation.choice.numberForeground': mfg,
        'AIAssistant.Chat.StepCard.Default.background.color': 'subtleBackground',
        'AIAssistant.Chat.StepCard.Default.border.color': 'mutedBorderColor',
        'WelcomeScreen.captionBackground': 'subtleBackground', 'WelcomeScreen.captionForeground': fg,
        # Primer ToggleSwitch (expUI/Islands stopped styling toggles in 2026.3; IntelliJ Light's green would show)
        'ToggleButton.onBackground': P['successEmphasis'], 'ToggleButton.offBackground': o(P['neutralMuted']),
        'ToggleButton.offForeground': mfg, 'ToggleButton.buttonColor': P['fgMuted'],
        'ToggleButton.borderColor': o(P['neutralEmphasis']),
    })

    # CodeWithMe avatars: Primer emphasis fills with on-emphasis text
    for i, k in enumerate(('success', 'sponsors', 'severe', 'done', 'attention', 'accent'), 1):
        bg = P[k + 'Emphasis'] if k != 'sponsors' else P['sponsorsEmphasis']
        ui[f'CodeWithMe.Users.{i}.Background'] = bg
        ui[f'CodeWithMe.Users.{i}.Foreground'] = None
    # text colors resolved with an AA guarantee against the surface they sit on
    text = {
        'Bookmark.MnemonicCurrent.foreground': (P['fgOnEmphasis'], P['accentEmphasis'], 4.5),
        'CheckBoxMenuItem.acceleratorForeground': (mfg, 'overlayBackground', 4.5),
        'CompletionPopup.matchForeground': ('accentColor', 'overlayBackground', 4.5),
        'CompletionPopup.Advertiser.foreground': (mfg, 'overlayBackground', 4.5),
        'Counter.foreground': (P['fgOnEmphasis'], P['accentEmphasis'], 4.5),
        'Label.errorForeground': ('dangerColor', 'background', 4.5),
        'Label.successForeground': ('successColor', 'background', 4.5),
        'Link.activeForeground': ('accentColor', 'background', 4.5),
        'Link.hoverForeground': ('accentColor', 'background', 4.5),
        'Link.pressedForeground': ('accentColor', 'background', 4.5),
        'Link.visitedForeground': ('accentColor', 'background', 4.5),
        'MenuItem.acceleratorForeground': (mfg, 'overlayBackground', 4.5),
        'Notification.errorForeground': ('dangerColor', ui['Notification.errorBackground'], 4.5),
        'Notification.linkForeground': ('accentColor', 'overlayBackground', 4.5),
        'Popup.Advertiser.foreground': (mfg, 'overlayBackground', 4.5),
        'Popup.Header.inactiveForeground': (mfg, 'overlayBackground', 4.5),
        'SearchEverywhere.Advertiser.foreground': (mfg, 'overlayBackground', 4.5),
        'SearchField.errorForeground': ('dangerColor', ui['SearchField.errorBackground'], 4.5),
        'SpeedSearch.errorForeground': ('dangerColor', 'overlayBackground', 4.5),
        'ToolTip.infoForeground': (mfg, 'overlayBackground', 4.5),
        'ToolTip.shortcutForeground': (mfg, 'overlayBackground', 4.5),
        'UnattendedHostStatus.warningForeground': (P['fgOnEmphasis'] if dark else P['fg'], P['attentionEmphasis'], 4.5),
        'VersionControl.Merge.Badge.infoForeground': (mfg, ui['VersionControl.Merge.Badge.infoBackground'], 4.5),
        'VersionControl.Merge.Badge.modifiedItemForeground': ('accentColor', ui['VersionControl.Merge.Badge.modifiedItemBackground'], 4.5),
        'AIA.Elicitation.choice.selectedNumberForeground': ('accentColor', ui['AIA.Elicitation.choice.selectedBackground'], 4.5),
        'ToggleButton.onForeground': (P['fgOnEmphasis'], P['successEmphasis'], 4.5),
    }
    for i in range(1, 7):
        text[f'CodeWithMe.Users.{i}.Foreground'] = (P['fgOnEmphasis'], ui[f'CodeWithMe.Users.{i}.Background'], 4.5)
    on_emph = {k for k in text if k.endswith(('MnemonicCurrent.foreground', 'Counter.foreground', 'UnattendedHostStatus.warningForeground',
                                              'ToggleButton.onForeground'))
               or k.startswith('CodeWithMe')}
    for k, (f, b, r) in text.items():
        val = t(f, b, r, k, (P['fg'], P['fgOnEmphasis'], P['canvas']) if k in on_emph else ())
        # keep the token reference when the Primer value already passes
        ui[k] = f if (f in C and val == over(C[f], '#000000')) else val

    # checkbox icon palette
    sfx = '.Dark' if dark else ''
    icons = {'ColorPalette': {
        'Tree.iconColor': P['fgMuted'],
        'Checkbox.Background.Default' + sfx: o(P['subtle']),
        'Checkbox.Border.Default' + sfx: P['neutralEmphasis'],
        'Checkbox.Background.Selected' + sfx: P['accentEmphasis'],
        'Checkbox.Border.Selected' + sfx: P['accentEmphasis'],
        'Checkbox.Foreground.Selected' + sfx: P['fgOnEmphasis'],
        'Checkbox.Background.Disabled' + sfx: o(P['subtle']),
        'Checkbox.Border.Disabled' + sfx: o(P['borderMuted']),
        'Checkbox.Foreground.Disabled' + sfx: P['fgSubtle'],
        'Checkbox.Focus.Wide' + sfx: P['accentFg'],
        'Checkbox.Focus.Thin.Default' + sfx: P['accentFg'],
        'Checkbox.Focus.Thin.Selected' + sfx: P['accentFg'],
    }}
    # Fill every colour key the JetBrains Islands chain would otherwise supply, repainted into
    # the GitHub palette (see islands_map.py). Keys set above always win.
    S = {'P': P, 'over': lambda c, bg=None: over(c, bg or cv), 'alpha': alpha, 'canvas': cv, 'frame': frame, 'overlay': ovl,
         'subtle': o(P['subtle']), 'border': o(P['border']), 'borderMuted': o(P['borderMuted']),
         'selection': colors['selectionBackground'], 'hover': colors['hoverBackground'],
         'findMatch': o(vc['editor.findMatchBackground']), 'scale': P['scale'],
         'grays': [cv, frame, ovl, o(P['subtle']), o(P['border']), o(P['borderMuted']), P['fg'], P['fgMuted'],
                   P['fgSubtle'], o(P['neutralEmphasis'])] + [c for c in P['scale']['gray'] if len(c) == 7]}
    star = ui['*']
    lower = {k.lower(): k for k in ui} | {('*.' + k).lower(): '*.' + k for k in star}
    resolved = lambda v: C.get(v, v) if isinstance(v, str) else v
    inh = islands_map.inherited(dark, S)
    def own_background(k):
        # a text colour with a sibling "...Background" key sits on that background (badges, tags, ...)
        for fk, bk in (('Foreground', 'Background'), ('foreground', 'background')):
            if k.endswith(fk):
                sib = k[:-len(fk)] + bk
                val = ui.get(sib, inh.get(sib))
                if isinstance(val, str):
                    val = C.get(val, val)
                    if re.fullmatch(r'#[0-9a-fA-F]{6}', val): return val
                    if re.fullmatch(r'#[0-9a-fA-F]{8}', val): return over(val, cv)  # translucent fill on the island
        return None
    # JBColor.namedColor falls back to "*" keys matched as name suffixes before its hardcoded default,
    # so a code-default key our "*" block covers (e.g. *.hoverBackground) already follows the theme
    code = set(islands_map.code_defaults())
    stars = set(star) | {k[2:] for k in inh if k.startswith('*.')}
    for k, v in inh.items():
        if k in code and k.lower() not in lower and any(k.endswith(s) for s in stars):
            continue
        if k.lower() in lower:
            src = lower[k.lower()]
            if src != k and not k.startswith('*.'):  # case variant of a key we set: mirror our value
                ui[k] = ui[src] if not src.startswith('*.') else star[src[2:]]
            continue
        if k.startswith('*.'):
            star[k[2:]] = v
            continue
        if re.search(r'foreground$', k, re.I) and not re.search(r'disabled|inactive|placeholder', k, re.I) and len(v) == 7:
            surf = frame if k.startswith(('StatusBar', 'MainToolbar', 'MainWindow', 'ToolWindow.Button', 'TitlePane', 'RunWidget')) else \
                   ovl if k.startswith(('Popup', 'Editor.ToolTip', 'ParameterInfo', 'GotItTooltip', 'Tooltip', 'ToolTip',
                                        'Notification', 'MenuItem', 'Menu.', 'PopupMenu', 'CompletionPopup', 'SearchEverywhere')) else cv
            own = own_background(k)
            surf = own or surf
            # status colours (warning/error/success) and coloured text on a translucent chip of its own
            # (badges, drop areas) keep their hue; other neutral text may fall back to fg
            status = re.search(r'warning|error|success', k, re.I) and not own
            chip = own and len(resolved(ui.get(k[:-10] + ('Background' if k.endswith('Foreground') else 'background'),
                                             inh.get(k[:-10] + ('Background' if k.endswith('Foreground') else 'background'), ''))) or '') == 9
            v = ensure(v, surf, 4.5, f'{name}:{k}', () if status or chip else (P['fg'], P['fgOnEmphasis'], cv))
        ui[k] = v
    # text on fills that only exist after inheritance: AA on the fill it is drawn on
    for pre in ('Bookmark.Mnemonic.icon', 'GotItTooltip.shortcut', 'ToolWindow.Button.selected'):
        fk, bk = pre + 'Foreground', pre + 'Background'
        b = resolved(ui[bk])
        b = over(b, frame if pre.startswith('ToolWindow') else ovl if pre.startswith('GotIt') else cv)
        val = t(ui[fk], b, 4.5, fk)
        ui[fk] = ui[fk] if (ui[fk] in C and val == over(C[ui[fk]], '#000000')) else val
    star = ui.pop('*')
    body = {'*': star}
    body.update(dict(sorted(ui.items(), key=lambda kv: kv[0].lower())))
    return {
        'name': display, 'dark': dark, 'author': 'Yash Pal <iyashpal.dev@gmail.com>',
        'parentTheme': 'Islands Dark' if dark else 'Islands Light',
        'editorScheme': f'/theme/scheme/{name}.xml',
        'colors': colors, 'ui': body, 'icons': icons,
    }, P, sel_bg, sel_fg

# ---------------------------------------------------------------- editor scheme
def load_scheme(path):
    r = ET.parse(path).getroot()
    attrs = {}
    for o in r.find('attributes'):
        v = o.find('value')
        attrs.setdefault(o.get('name'),
                         {x.get('name'): (x.get('value') or '') for x in v} if v is not None else {'BASE': o.get('baseAttributes')})
    return attrs

def norm(v): return ('#' + v.lstrip('#').lower().rjust(6, '0')) if v else v

# Template: union of all attributes across the previous schemes, with dark-default first.
TEMPLATE = {}
ORIGIN = {}
for n in ['dark-default'] + [k for k in VARIANTS if k != 'dark-default']:
    for k, v in load_scheme(os.path.join(ORIG, 'scheme', n + '.xml')).items():
        if k not in TEMPLATE:
            TEMPLATE[k] = v; ORIGIN[k] = n

ROLE_NAMES = ['comment', 'keyword', 'string', 'constant', 'function', 'tag', 'entity', 'variable', 'invalid', 'fg']

def infer_role(attr, color, src):
    """Map an attribute's colour in its source scheme back to a VS Code token role."""
    R = roles(src)
    c = norm(color)
    for rn in ROLE_NAMES + ['heading', 'quote', 'support', 'regexEscape']:
        if R.get(rn) == c: return rn
    n = attr.upper()
    for pat, role in (('COMMENT', 'comment'), ('STRING|REGEX|HEREDOC|VALUE', 'string'), ('KEYWORD|SIGN|OPERATOR', 'keyword'),
                      ('NUMBER|CONST|BOOLEAN', 'constant'), ('FUNC|METHOD', 'function'), ('TAG', 'tag'),
                      ('CLASS|TYPE', 'entity'), ('PARAM|VAR', 'variable')):
        if re.search(pat, n): return role
    return 'fg'

# VS Code semantics (semantic tokens fall back to these TextMate scopes)
OVERRIDE_ROLES = {
    # plain variables / fields / properties render in the default foreground
    **{k: 'fg' for k in ('DEFAULT_LOCAL_VARIABLE', 'DEFAULT_GLOBAL_VARIABLE', 'DEFAULT_INSTANCE_FIELD',
                         'DEFAULT_STATIC_FIELD', 'DEFAULT_IDENTIFIER', 'DEFAULT_DOC_COMMENT_TAG_VALUE',
                         'DEFAULT_REASSIGNED_LOCAL_VARIABLE', 'JS.LOCAL_VARIABLE', 'JS.GLOBAL_VARIABLE',
                         'INSTANCE_FIELD_ATTRIBUTES', 'STATIC_FIELD_ATTRIBUTES', 'IMPLICIT_ANONYMOUS_CLASS_PARAMETER_ATTRIBUTES',
                         'RUBY_IDENTIFIER', 'RUBY_LOCAL_VAR_ID', 'PHP_VAR', 'OC.STRUCT_FIELD', 'LOCAL_VARIABLE_ATTRIBUTES',
                         'GO_BUILTIN_VARIABLE', 'GO_METHOD_RECEIVER', 'XML_TAG_DATA', 'DEFAULT_TEMPLATE_LANGUAGE_COLOR',
                         'DEFAULT_TAG', 'XML_TAG', 'HTML_TAG', 'MACRO_PARAMETER', 'DEFAULT_BRACES', 'DEFAULT_BRACKETS',
                         'DEFAULT_COMMA', 'DEFAULT_DOT', 'DEFAULT_PARENTHS', 'DEFAULT_SEMICOLON', 'XML_PROLOGUE')},
    # parameters: variable.parameter -> orange
    **{k: 'variable' for k in ('DEFAULT_PARAMETER', 'DEFAULT_REASSIGNED_PARAMETER', 'JS.PARAMETER', 'PHP_PARAMETER',
                               'RUBY_PARAMETER_ID', 'PARAMETER_ATTRIBUTES')},
    # functions, calls and decorators: entity.name.function -> purple
    **{k: 'function' for k in ('DEFAULT_FUNCTION_CALL', 'DEFAULT_FUNCTION_DECLARATION', 'DEFAULT_INSTANCE_METHOD',
                               'DEFAULT_STATIC_METHOD', 'STATIC_METHOD_ATTRIBUTES', 'GO_EXPORTED_FUNCTION_CALL',
                               'GO_LOCAL_FUNCTION_CALL', 'DEFAULT_METADATA', 'PY.DECORATOR')},
    # types: entity.name.type -> orange (purple in classic)
    **{k: 'entity' for k in ('DEFAULT_CLASS_NAME', 'DEFAULT_CLASS_REFERENCE', 'DEFAULT_INTERFACE_NAME', 'CLASS_REFERENCE',
                             'CLASS_NAME_ATTRIBUTES', 'DEFAULT_LABEL', 'GO_TYPE_REFERENCE', 'GO_BUILTIN_TYPE_REFERENCE',
                             'PY.CLASS_DEFINITION', 'TYPE_PARAMETER_NAME_ATTRIBUTES')},
    **{k: 'keyword' for k in ('DEFAULT_KEYWORD', 'DEFAULT_OPERATION_SIGN', 'DEFAULT_VALID_STRING_ESCAPE',
                              'DEFAULT_DOC_COMMENT_TAG', 'JAVA_DOC_TAG', 'DEFAULT_ENTITY', 'CUSTOM_KEYWORD1_ATTRIBUTES')},
    **{k: 'constant' for k in ('DEFAULT_CONSTANT', 'DEFAULT_NUMBER', 'DEFAULT_PREDEFINED_SYMBOL', 'DEFAULT_ATTRIBUTE',
                               'CUSTOM_KEYWORD2_ATTRIBUTES', 'CSS.PROPERTY_VALUE', 'CSS.PROPERTY_NAME')},
    **{k: 'string' for k in ('DEFAULT_STRING', 'CSS.URL', 'REST.INTERPRETED', 'COFFEESCRIPT.LOCAL_VARIABLE')},
    **{k: 'invalid' for k in ('DEFAULT_INVALID_STRING_ESCAPE', 'JAVA_INVALID_STRING_ESCAPE',
                              'CUSTOM_INVALID_STRING_ESCAPE_ATTRIBUTES', 'PY.INVALID_STRING_ESCAPE')},
    **{k: 'comment' for k in ('DEFAULT_LINE_COMMENT', 'DEFAULT_BLOCK_COMMENT', 'DEFAULT_DOC_COMMENT', 'DEFAULT_DOC_MARKUP',
                              'JAVA_DOC_MARKUP', 'NOT_USED_ELEMENT_ATTRIBUTES_')},
    'CUSTOM_KEYWORD3_ATTRIBUTES': 'entity', 'CUSTOM_KEYWORD4_ATTRIBUTES': 'function',
    'DEFAULT_FUNCTION_DECLARATION': 'function',
    **{f'MARKDOWN_HEADER_LEVEL_{i}': 'heading' for i in range(1, 7)},
    'MARKDOWN_CODE_SPAN': 'raw', 'MARKDOWN_CODE_BLOCK': 'raw', 'MARKDOWN_BLOCK_QUOTE': 'quote',
    'MARKDOWN_LINK_TEXT': 'link', 'MARKDOWN_LINK_DESTINATION': 'link', 'MARKDOWN_LIST_ITEM': 'listMarker',
    'MARKDOWN_BOLD': 'fg', 'MARKDOWN_ITALIC': 'fg', 'JSON.PROPERTY_KEY': 'jsonKey', 'YAML_SCALAR_KEY': 'tag',
}
BOLD = {f'MARKDOWN_HEADER_LEVEL_{i}' for i in range(1, 7)} | {'MARKDOWN_BOLD'}
ITALIC = {'MARKDOWN_ITALIC'}
# extra attributes worth pinning so Darcula/Default colours never leak through
EXTRA = ['DEFAULT_CLASS_REFERENCE', 'DEFAULT_DOC_COMMENT_TAG_VALUE', 'DEFAULT_REASSIGNED_LOCAL_VARIABLE',
         'DEFAULT_REASSIGNED_PARAMETER', 'TYPE_PARAMETER_NAME_ATTRIBUTES', 'JSON.PROPERTY_KEY', 'MARKDOWN_LIST_ITEM',
         'MARKDOWN_LINK_DESTINATION', 'WEAK_WARNING_ATTRIBUTES', 'CTRL_CLICKABLE', 'FOLDED_TEXT_ATTRIBUTES',
         'LIVE_TEMPLATE_ATTRIBUTES', 'LOG_INFO_OUTPUT', 'LOG_DEBUG_OUTPUT', 'LOG_VERBOSE_OUTPUT', 'LOG_EXPIRED_ENTRY',
         'INLAY_TEXT_WITHOUT_BACKGROUND', 'DIFF_INSERTED_IGNORED', 'MARKED_FOR_REMOVAL_ATTRIBUTES']
DROP = {'TAB_SELECTED', 'TAB_SELECTED_INACTIVE'}
UNMAPPED = {}  # variant -> keys still on the legacy role heuristic (reported)

def scheme(name, display, dark, P, sel_bg, sel_fg):
    vs = VS[name]; vc = vs['colors']; R = roles(name)
    hc = 'high-contrast' in name
    bg, fg = vc['editor.background'].lower(), vc['editor.foreground'].lower()
    o = lambda c, b=None: over(c, b or bg)
    g = lambda k, d=None: vc.get(k, d)
    term_bg = bg  # the console sits in a tool-window island, which shares the editor canvas
    # faded text (unused symbols, inactive breadcrumbs, expired log entries): fg.subtle, at least 3:1
    faded = ensure(P['fgSubtle'], bg, 3.0, f'{name}:fadedText')
    cons_err = ensure(vc.get('debugConsole.errorForeground', P['dangerFg']), term_bg, 4.5, f'{name}:CONSOLE_ERROR')
    # weak warnings: the quietest Primer yellow that still reads as yellow (>= 3:1, 4.5:1 in high contrast),
    # a step below the warning colour; the IDE also tints the weak-warning icon and stripe marks with it
    warn_c, weak_min = contrast(o(P['attentionFg']), bg), (4.5 if hc else 3.0)
    yellows = [o(c) for c in P['scale']['yellow']]
    quiet = [c for c in yellows if weak_min <= contrast(c, bg) < warn_c - .3]
    weak_warn = (min(quiet, key=lambda c: contrast(c, bg)) if quiet else
                 ensure(max((c for c in yellows if contrast(c, bg) < weak_min), key=lambda c: contrast(c, bg)),
                        bg, weak_min, f'{name}:WEAK_WARNING'))
    cons_warn = ensure(vc.get('debugConsole.warningForeground', P['attentionFg']), term_bg, 4.5, f'{name}:CONSOLE_WARN')
    ansi = lambda k: ensure(vc['terminal.' + k], term_bg, 4.5, f'{name}:{k}') if k not in ('ansiBlack', 'ansiWhite', 'ansiBrightBlack', 'ansiBrightWhite') else vc['terminal.' + k]
    find_hl = o(g('editor.findMatchHighlightBackground'))
    word = g('editor.wordHighlightBackground', '#00000000'); word_s = g('editor.wordHighlightStrongBackground', '#00000000')
    if parse(word)[1] < .05: word = alpha(P['neutralEmphasis'], .25)
    if parse(word_s)[1] < .05: word_s = alpha(P['neutralEmphasis'], .35)
    gutter = lambda k, d: o(g(k, d))
    ins_line = o(g('diffEditor.insertedLineBackground', P['successSubtle']))
    del_line = o(g('diffEditor.removedLineBackground', P['dangerSubtle']))
    indent = o(g('editorIndentGuide.background', P['borderMuted']))
    indent_a = o(g('editorIndentGuide.activeBackground', P['border']))
    lineno = o(g('editorLineNumber.foreground'))
    lineno = ensure(lineno, bg, 3.0, f'{name}:LINE_NUMBERS')  # WCAG non-text minimum for gutter numbers
    line_hl = o(g('editor.lineHighlightBackground'))

    colors = {
        'ADDED_LINES_COLOR': gutter('editorGutter.addedBackground', P['successFg']),
        'ANNOTATIONS_COLOR': P['fgMuted'], 'BORDER_LINES_COLOR': o(P['borderMuted']),
        'CARET_COLOR': g('editorCursor.foreground', P['accentFg']), 'CARET_ROW_COLOR': line_hl,
        'CHANGED_LINES_POPUP': o(P['overlay']), 'CONSOLE_BACKGROUND_KEY': term_bg,
        'DELETED_LINES_COLOR': gutter('editorGutter.deletedBackground', P['dangerFg']),
        'DIFF_SEPARATOR_WAVE': o(P['border']), 'DOCUMENTATION_COLOR': o(P['overlay']),
        'ERROR_HINT': over(P['dangerSubtle'], P['overlay']),
        'GUTTER_BACKGROUND': bg, 'HINT_BORDER': o(P['border']),
        'IGNORED_ADDED_LINES_BORDER_COLOR': gutter('editorGutter.addedBackground', P['successFg']),
        'IGNORED_DELETED_LINES_BORDER_COLOR': gutter('editorGutter.deletedBackground', P['dangerFg']),
        'IGNORED_MODIFIED_LINES_BORDER_COLOR': gutter('editorGutter.modifiedBackground', P['attentionFg']),
        'INDENT_GUIDE': indent, 'INFORMATION_HINT': o(P['overlay']),
        'LINE_NUMBERS_COLOR': lineno, 'LINE_NUMBER_ON_CARET_ROW_COLOR': g('editorLineNumber.activeForeground', fg),
        'LOOKUP_COLOR': o(P['overlay']), 'MATCHED_BRACES_INDENT_GUIDE_COLOR': indent_a,
        'METHOD_SEPARATORS_COLOR': o(P['borderMuted']),
        'MODIFIED_LINES_COLOR': gutter('editorGutter.modifiedBackground', P['attentionFg']),
        'NOTIFICATION_BACKGROUND': o(P['overlay']), 'PREVIEW_BACKGROUND': bg,
        'PROMOTION_PANE': over(P['accentSubtle'], P['overlay']), 'RECENT_LOCATIONS_SELECTION': o(P['neutralMuted']),
        'RIGHT_MARGIN_COLOR': o(P['borderMuted']), 'SELECTED_INDENT_GUIDE': indent_a,
        'SELECTION_BACKGROUND': sel_bg, 'TAB_UNDERLINE': P['activeBorder'], 'TAB_UNDERLINE_INACTIVE': o(P['border']),
        'TOOLTIP': o(P['overlay']), 'VISUAL_INDENT_GUIDE': o(P['borderMuted']),
        'WHITESPACES': o(g('editorWhitespace.foreground', P['fgSubtle'])),
        'WHITESPACES_MODIFIED_LINES_COLOR': o(P['attentionMuted']),
        'SOFT_WRAP_SIGN_COLOR': o(g('editorWhitespace.foreground', P['fgSubtle'])),
        'FILESTATUS_ADDED': g('gitDecoration.addedResourceForeground'),
        'FILESTATUS_UNKNOWN': g('gitDecoration.untrackedResourceForeground'),
        'FILESTATUS_COPIED': g('gitDecoration.addedResourceForeground'),
        'FILESTATUS_addedOutside': g('gitDecoration.addedResourceForeground'),
        'FILESTATUS_MODIFIED': g('gitDecoration.modifiedResourceForeground'),
        'FILESTATUS_RENAMED': g('gitDecoration.modifiedResourceForeground'),
        'FILESTATUS_HIJACKED': g('gitDecoration.modifiedResourceForeground'),
        'FILESTATUS_modifiedOutside': g('gitDecoration.modifiedResourceForeground'),
        'FILESTATUS_DELETED': g('gitDecoration.deletedResourceForeground'),
        'FILESTATUS_IDEA_FILESTATUS_DELETED_FROM_FILE_SYSTEM': g('gitDecoration.ignoredResourceForeground'),
        'FILESTATUS_IDEA_FILESTATUS_IGNORED': g('gitDecoration.ignoredResourceForeground'),
        'FILESTATUS_OBSOLETE': g('gitDecoration.ignoredResourceForeground'),
        'FILESTATUS_SUPPRESSED': g('gitDecoration.ignoredResourceForeground'),
        'FILESTATUS_MERGED': P['doneFg'], 'FILESTATUS_SWITCHED': P['doneFg'],
        'FILESTATUS_NOT_CHANGED_IMMEDIATE': P['accentFg'], 'FILESTATUS_NOT_CHANGED_RECURSIVE': P['accentFg'],
        **{k: g('gitDecoration.conflictingResourceForeground') for k in (
            'FILESTATUS_IDEA_FILESTATUS_MERGED_WITH_CONFLICTS', 'FILESTATUS_IDEA_FILESTATUS_MERGED_WITH_BOTH_CONFLICTS',
            'FILESTATUS_IDEA_FILESTATUS_MERGED_WITH_PROPERTY_CONFLICTS', 'FILESTATUS_changelistConflict')},
        **{f'VCS_ANNOTATIONS_COLOR_{i}': o(alpha(P['accentEmphasis'], .05 + .05 * i)) for i in range(1, 6)},
    }
    # JetBrains' Default scheme paints selected text white (SELECTION_FOREGROUND ffffff); VS Code keeps
    # syntax colours under the selection, so clear it (empty = keep token colours) outside high contrast.
    colors['SELECTION_FOREGROUND'] = sel_fg if hc else ''
    # unfocused-editor selection: VS Code's editor.inactiveSelectionBackground, else half the accent tint
    # (replaces JetBrains' grey B5B7BD / 4c4f56)
    colors['SELECTION_BACKGROUND_INACTIVE'] = o(g('editor.inactiveSelectionBackground', alpha(P['accentFg'], .1)))
    colors = {k: (v.lower() if isinstance(v, str) else v) for k, v in colors.items()}

    A = lambda **kw: {k: v for k, v in kw.items() if v is not None}
    inlay_fg = g('editorInlayHint.foreground', P['fgMuted']); inlay_bg = o(g('editorInlayHint.background', P['neutralSubtle']))
    sp = {
        'TEXT': A(FOREGROUND=fg, BACKGROUND=bg),
        'INLAY_DEFAULT': A(FOREGROUND=inlay_fg, BACKGROUND=inlay_bg),
        'INLINE_PARAMETER_HINT': A(FOREGROUND=inlay_fg, BACKGROUND=inlay_bg),
        'INLAY_TEXT_WITHOUT_BACKGROUND': A(FOREGROUND=inlay_fg),
        'EXECUTIONPOINT_ATTRIBUTES': A(BACKGROUND=o(g('editor.stackFrameHighlightBackground')), ERROR_STRIPE_COLOR=P['attentionFg']),
        'TYPO': A(EFFECT_COLOR=P['accentFg'], EFFECT_TYPE='2'),
        'DIFF_INSERTED': A(BACKGROUND=ins_line, ERROR_STRIPE_COLOR=P['successFg']),
        'DIFF_DELETED': A(BACKGROUND=del_line, ERROR_STRIPE_COLOR=P['dangerFg']),
        'DIFF_MODIFIED': A(BACKGROUND=o(P['attentionSubtle']), ERROR_STRIPE_COLOR=P['attentionFg']),
        'DIFF_CONFLICT': A(BACKGROUND=o(P['severeSubtle']), ERROR_STRIPE_COLOR=P['severeFg']),
        'DIFF_INSERTED_IGNORED': A(BACKGROUND=o(alpha(P['successEmphasis'], .08))),
        'BAD_CHARACTER': A(FOREGROUND=R['invalid'], BACKGROUND=o(P['dangerSubtle'])),
        'BREAKPOINT_ATTRIBUTES': A(BACKGROUND=o(P['dangerSubtle']), ERROR_STRIPE_COLOR=P['dangerFg']),
        'DEPRECATED_ATTRIBUTES': A(EFFECT_TYPE='3', EFFECT_COLOR=P['fgMuted']),
        'MARKED_FOR_REMOVAL_ATTRIBUTES': A(EFFECT_TYPE='3', EFFECT_COLOR=P['dangerFg']),
        'DUPLICATE_FROM_SERVER': A(BACKGROUND=o(P['neutralSubtle'])),
        'ERRORS_ATTRIBUTES': A(EFFECT_TYPE='2', EFFECT_COLOR=P['dangerFg'], ERROR_STRIPE_COLOR=P['dangerFg']),
        'WARNING_ATTRIBUTES': A(EFFECT_TYPE='2', EFFECT_COLOR=P['attentionFg'], ERROR_STRIPE_COLOR=P['attentionFg']),
        'WEAK_WARNING_ATTRIBUTES': A(EFFECT_TYPE='2', EFFECT_COLOR=weak_warn, ERROR_STRIPE_COLOR=weak_warn),
        'GENERIC_SERVER_ERROR_OR_WARNING': A(EFFECT_TYPE='2', EFFECT_COLOR=P['severeFg'], ERROR_STRIPE_COLOR=P['severeFg']),
        'INFO_ATTRIBUTES': A(EFFECT_TYPE='2', EFFECT_COLOR=P['accentFg'], ERROR_STRIPE_COLOR=P['accentFg']),
        'NOT_USED_ELEMENT_ATTRIBUTES': A(FOREGROUND=faded),
        'HYPERLINK_ATTRIBUTES': A(FOREGROUND=g('textLink.foreground'), EFFECT_TYPE='1', EFFECT_COLOR=g('textLink.foreground')),
        'FOLLOWED_HYPERLINK_ATTRIBUTES': A(FOREGROUND=g('textLink.foreground'), EFFECT_TYPE='1', EFFECT_COLOR=g('textLink.foreground')),
        'CTRL_CLICKABLE': A(FOREGROUND=g('textLink.foreground'), EFFECT_TYPE='1', EFFECT_COLOR=g('textLink.foreground')),
        'IDENTIFIER_UNDER_CARET_ATTRIBUTES': A(BACKGROUND=o(word), ERROR_STRIPE_COLOR=P['fgMuted']),
        'WRITE_IDENTIFIER_UNDER_CARET_ATTRIBUTES': A(BACKGROUND=o(word_s), ERROR_STRIPE_COLOR=P['attentionFg']),
        'SEARCH_RESULT_ATTRIBUTES': A(BACKGROUND=find_hl, ERROR_STRIPE_COLOR=P['attentionFg']),
        'TEXT_SEARCH_RESULT_ATTRIBUTES': A(BACKGROUND=find_hl, ERROR_STRIPE_COLOR=P['attentionFg']),
        'WRITE_SEARCH_RESULT_ATTRIBUTES': A(BACKGROUND=find_hl, ERROR_STRIPE_COLOR=P['attentionFg']),
        'INJECTED_LANGUAGE_FRAGMENT': {},
        'JAVA_DOC_MARKUP': A(FOREGROUND=R['comment']),
        'JAVA_DOC_TAG': A(FOREGROUND=R['keyword']),
        'MATCHED_BRACE_ATTRIBUTES': A(BACKGROUND=o(g('editorBracketMatch.background')), EFFECT_TYPE='0',
                                      EFFECT_COLOR=o(g('editorBracketMatch.border', g('editorBracketMatch.background')))),
        'UNMATCHED_BRACE_ATTRIBUTES': A(FOREGROUND=R['invalid'], BACKGROUND=o(P['dangerSubtle'])),
        'FOLDED_TEXT_ATTRIBUTES': A(FOREGROUND=P['fgMuted'], BACKGROUND=o(g('editor.foldBackground', P['neutralSubtle']))),
        'LIVE_TEMPLATE_ATTRIBUTES': A(EFFECT_TYPE='0', EFFECT_COLOR=P['accentFg']),
        'REST.FIXED': A(FOREGROUND=R['raw'], BACKGROUND=o(P['neutralMuted'])),
        'REST.INLINE': A(FOREGROUND=R['raw']),
        'SPY-JS.EXCEPTION': A(BACKGROUND=o(P['dangerSubtle'])), 'SPY-JS.FUNCTION_SCOPE': A(BACKGROUND=o(P['attentionSubtle'])),
        'SPY-JS.PATH_LEVEL_ONE': A(BACKGROUND=o(P['successSubtle'])), 'SPY-JS.PATH_LEVEL_TWO': A(EFFECT_TYPE='1', EFFECT_COLOR=P['fgMuted']),
        'SPY-JS.PROGRAM_SCOPE': A(BACKGROUND=o(P['neutralSubtle'])),
        'TODO_DEFAULT_ATTRIBUTES': A(FOREGROUND=ensure(P['attentionFg'], bg, 4.5, f'{name}:TODO'), FONT_TYPE='3', ERROR_STRIPE_COLOR=P['attentionFg']),
        'BREADCRUMBS_CURRENT': A(FOREGROUND=fg, BACKGROUND=bg), 'BREADCRUMBS_DEFAULT': A(FOREGROUND=ensure(P['fgMuted'], bg, 4.5, f'{name}:BREADCRUMBS')),
        'BREADCRUMBS_HOVERED': A(FOREGROUND=fg, BACKGROUND=o(P['neutralSubtle'])),
        'BREADCRUMBS_INACTIVE': A(FOREGROUND=faded),
        'CODE_LENS_BORDER_COLOR': A(EFFECT_COLOR=o(P['borderMuted'])),
        'TERMINAL_COMMAND_TO_RUN_USING_IDE': A(FOREGROUND=P['fgMuted'], BACKGROUND=bg),
        'CONSOLE_NORMAL_OUTPUT': A(FOREGROUND=g('terminal.foreground', fg)),
        'CONSOLE_ERROR_OUTPUT': A(FOREGROUND=cons_err),
        'CONSOLE_SYSTEM_OUTPUT': A(FOREGROUND=ensure(P['fgMuted'], term_bg, 4.5, f'{name}:CONSOLE_SYSTEM')),
        'CONSOLE_USER_INPUT': A(FOREGROUND=ensure(P['successFg'], term_bg, 4.5, f'{name}:CONSOLE_USER_INPUT')),
        'LOG_ERROR_OUTPUT': A(FOREGROUND=cons_err), 'LOG_WARNING_OUTPUT': A(FOREGROUND=cons_warn),
        'LOG_INFO_OUTPUT': A(FOREGROUND=g('terminal.foreground', fg)),
        'LOG_DEBUG_OUTPUT': A(FOREGROUND=ensure(P['fgMuted'], term_bg, 4.5, f'{name}:LOG_DEBUG')),
        'LOG_VERBOSE_OUTPUT': A(FOREGROUND=ensure(P['fgMuted'], term_bg, 4.5, f'{name}:LOG_VERBOSE')),
        'LOG_EXPIRED_ENTRY': A(FOREGROUND=faded),
        'CONSOLE_BLACK_OUTPUT': A(FOREGROUND=ansi('ansiBlack')), 'CONSOLE_RED_OUTPUT': A(FOREGROUND=ansi('ansiRed')),
        'CONSOLE_GREEN_OUTPUT': A(FOREGROUND=ansi('ansiGreen')), 'CONSOLE_YELLOW_OUTPUT': A(FOREGROUND=ansi('ansiYellow')),
        'CONSOLE_BLUE_OUTPUT': A(FOREGROUND=ansi('ansiBlue')), 'CONSOLE_MAGENTA_OUTPUT': A(FOREGROUND=ansi('ansiMagenta')),
        'CONSOLE_CYAN_OUTPUT': A(FOREGROUND=ansi('ansiCyan')), 'CONSOLE_GRAY_OUTPUT': A(FOREGROUND=ansi('ansiWhite')),
        'CONSOLE_DARKGRAY_OUTPUT': A(FOREGROUND=ansi('ansiBrightBlack')),
        'CONSOLE_RED_BRIGHT_OUTPUT': A(FOREGROUND=ansi('ansiBrightRed')),
        'CONSOLE_GREEN_BRIGHT_OUTPUT': A(FOREGROUND=ansi('ansiBrightGreen')),
        'CONSOLE_YELLOW_BRIGHT_OUTPUT': A(FOREGROUND=ansi('ansiBrightYellow')),
        'CONSOLE_BLUE_BRIGHT_OUTPUT': A(FOREGROUND=ansi('ansiBrightBlue')),
        'CONSOLE_MAGENTA_BRIGHT_OUTPUT': A(FOREGROUND=ansi('ansiBrightMagenta')),
        'CONSOLE_CYAN_BRIGHT_OUTPUT': A(FOREGROUND=ansi('ansiBrightCyan')),
        'CONSOLE_WHITE_OUTPUT': A(FOREGROUND=ansi('ansiBrightWhite')),
    }
    # coverage gutter markers (no VS Code theme colours exist): Primer status emphasis colours
    sp['LINE_FULL_COVERAGE'] = A(FOREGROUND=ensure(P['successEmphasis'], bg, 3.0, f'{name}:COVERAGE_FULL'), FONT_TYPE='1')
    sp['LINE_PARTIAL_COVERAGE'] = A(FOREGROUND=ensure(P['attentionEmphasis'], bg, 3.0, f'{name}:COVERAGE_PARTIAL'), FONT_TYPE='1')
    sp['LINE_NONE_COVERAGE'] = A(FOREGROUND=ensure(P['dangerEmphasis'], bg, 3.0, f'{name}:COVERAGE_NONE'), FONT_TYPE='1')
    for i in range(5):  # rainbow brackets = VS Code bracket pair colorization
        sp[f'RAINBOW_COLOR{i}'] = A(FOREGROUND=ensure(g(f'editorBracketHighlight.foreground{i + 1}', P['accentFg']), bg, 4.5, f'{name}:RAINBOW{i}'))
    for c in ('Black', 'Red', 'Green', 'Yellow', 'Blue', 'Magenta', 'Cyan', 'White'):
        sp[f'BLOCK_TERMINAL_{c.upper()}'] = A(FOREGROUND=ansi('ansi' + c), BACKGROUND=vc['terminal.ansi' + c])
        sp[f'BLOCK_TERMINAL_{c.upper()}_BRIGHT'] = A(FOREGROUND=ansi('ansiBright' + c), BACKGROUND=vc['terminal.ansiBright' + c])
    for i, k in enumerate(('success', 'accent', 'done', 'danger', 'severe', 'attention'), 1):
        sp[f'CodeWithMe.USER_{i}_MARKER'] = A(BACKGROUND=P[k + 'Emphasis'])
        sp[f'CodeWithMe.USER_{i}_SELECTION'] = A(BACKGROUND=o(alpha(P[k + 'Emphasis'], .25)))

    names = [k for k in TEMPLATE if k not in DROP] + [k for k in EXTRA if k not in TEMPLATE]
    names += [k for k in sp if k not in names]
    names += sorted(k for k in SYN_SCOPES if k not in names)
    names += sorted(k for k in LEGACY_ALL if k not in names and k not in DROP)
    inv = INVENTORY['dark' if dark else 'light']; inv_other = INVENTORY['light' if dark else 'dark']
    names += sorted(k for k in set(inv) | set(inv_other) if k not in names and k not in DROP)
    cands = sorted({o(c) for c in [fg, P['fgMuted'], P['fgSubtle'], P['border'], P['borderMuted'], P['subtle'],
                                   P['neutralMuted'], P['neutralSubtle'], P['neutralEmphasis']] +
                    [P[k + s_] for k in ('accent', 'success', 'attention', 'danger', 'severe', 'done')
                     for s_ in ('Fg', 'Emphasis', 'Muted', 'Subtle')]} | {bg})
    out = {}
    UNMAPPED.setdefault(name, [])
    for n in names:
        # syntax keys always come from the syntax design, even if a UI special exists for them
        if n in sp and not (n in ('JAVA_DOC_MARKUP', 'JAVA_DOC_TAG', 'REST.FIXED', 'REST.INLINE')
                            and (n in SYN_SCOPES if SYNTAX_DESIGN == 'vscode' else n in LEGACY_ALL)):
            out[n] = sp[n]; continue
        if SYNTAX_DESIGN == 'v010' and (n in SYN_SCOPES or n in LEGACY_ALL):  # editor token keys: v0.1.0 design
            if n in LEGACY[name]:
                v = dict(LEGACY[name][n])
                if v.get('FOREGROUND') and 'BACKGROUND' not in v:  # minimal AA nudge, printed
                    comment = 'COMMENT' in n.upper() or 'DOC' in n.upper()
                    f = ensure(v['FOREGROUND'], bg, 3.0 if comment else 4.5, f'{name}:legacy.{n}')
                    if not hc and n in ('DEFAULT_KEYWORD', 'DEFAULT_STRING', 'DEFAULT_CONSTANT',
                                        'DEFAULT_FUNCTION_DECLARATION', 'DEFAULT_LINE_COMMENT'):
                        f = ensure(f, sel_bg, 3.0, f'{name}:legacy.{n}@selection')  # readable when selected
                    v['FOREGROUND'] = f
                out[n] = v; continue
            if n in LEGACY_BASE:
                out[n] = {'BASE': LEGACY_BASE[n]}; continue
            if n in LEGACY_ALL or n in inv or n in inv_other:  # parity gap / JetBrains would leak
                if n in SYN_SCOPES:
                    out[n] = syntax_attrs(name, n, bg); continue
            else:
                continue  # never set in v0.1.0: IntelliJ's own fallback, as before
        if n in SYN_SCOPES:  # editor token keys: VS Code scope resolution
            out[n] = syntax_attrs(name, n, bg); continue
        if n not in TEMPLATE and n not in EXTRA:  # a UI key only JetBrains set
            src = inv.get(n) or inv_other.get(n) or {}
            out[n] = {'BASE': src['baseAttributes']} if 'baseAttributes' in src else snap_attrs(src, cands, bg)
            continue
        UNMAPPED[name].append(n)
        src = TEMPLATE.get(n, {})
        if n in OVERRIDE_ROLES:
            role = OVERRIDE_ROLES[n]
        elif 'BASE' in src:
            out[n] = {'BASE': src['BASE']}; continue
        elif src.get('FOREGROUND'):
            role = infer_role(n, src['FOREGROUND'], ORIGIN.get(n, 'dark-default'))
        else:
            role = infer_role(n, None, ORIGIN.get(n, 'dark-default')) if n not in TEMPLATE else 'fg'
        v = {'FOREGROUND': R[role]}
        if n in BOLD or role == 'heading': v['FONT_TYPE'] = '1'
        if n in ITALIC: v['FONT_TYPE'] = '2'
        if role == 'invalid': v['FONT_TYPE'] = '2'
        if role == 'regexEscape': v['FONT_TYPE'] = '1'
        if n in ('MARKDOWN_LINK_TEXT', 'MARKDOWN_LINK_DESTINATION'):
            v.update(EFFECT_TYPE='1', EFFECT_COLOR=R['link'])
        out[n] = v
    # break BASE cycles / references to dropped attributes
    for n, v in out.items():
        if 'BASE' in v and (v['BASE'] not in out and v['BASE'] not in ('TEXT',) or v['BASE'] == n):
            out[n] = {'FOREGROUND': fg}
    seen = set()
    for n in list(out):
        chain, cur = [], n
        while cur in out and 'BASE' in out[cur] and cur not in chain:
            chain.append(cur); cur = out[cur]['BASE']
        if cur in chain: out[n] = {'FOREGROUND': fg}

    L = [f'<scheme name={quoteattr(display)} version="142" parent_scheme="{"Darcula" if dark else "Default"}">',
         '    <metaInfo>', f'        <property name="generator">{SOURCE}</property>',
         '    </metaInfo>', '    <colors>']
    for k in sorted(colors):
        L.append(f'        <option name="{k}" value="{full(colors[k]).lstrip("#")}" />')
    L += ['    </colors>', '    <attributes>']
    for n in sorted(out, key=str.lower):
        v = out[n]
        if 'BASE' in v:
            L.append(f'        <option name={quoteattr(n)} baseAttributes="{v["BASE"]}" />'); continue
        L.append(f'        <option name={quoteattr(n)}>')
        if not v:
            L.append('            <value />')
        else:
            L.append('            <value>')
            for kk in ('FOREGROUND', 'BACKGROUND', 'FONT_TYPE', 'EFFECT_COLOR', 'EFFECT_TYPE', 'ERROR_STRIPE_COLOR'):
                if kk in v:
                    val = full('#' + v[kk].lstrip('#')).lstrip('#') if kk not in ('FONT_TYPE', 'EFFECT_TYPE') else v[kk]
                    L.append(f'                <option name="{kk}" value="{val}" />')
            L.append('            </value>')
        L.append('        </option>')
    L += ['    </attributes>', '</scheme>', '']
    return '\n'.join(L)

# ---------------------------------------------------------------- syntax (VS Code scope resolution)
SYN_SCOPES, SYN_ORIGIN, SYN_NOTES, SYN_ERRORS = syntax.load()
SYN = syntax.resolve(SYN_SCOPES, {n: {'fg': VS[n]['colors']['editor.foreground'], 'bg': VS[n]['colors']['editor.background'],
                                      'tokenColors': VS[n]['tokenColors']} for n in VARIANTS})

# Editor syntax tokens are restored from the v0.1.0 schemes (the user's preferred token design),
# snapshotted in snapshots/v0.1.0/. Keys v0.1.0 never set stay unset (IntelliJ falls back exactly as in
# v0.1.0), except keys JetBrains' own schemes set: those inherit from the matching DEFAULT_* key
# (LEGACY_BASE, IntelliJ's own fallback) or, failing that, use the VS Code-mapped value.
def _legacy(v):
    out = {}
    for k, a in load_scheme(os.path.join(HERE, 'snapshots', 'v0.1.0', v + '.xml')).items():
        if 'BASE' in a: out[k] = {'BASE': a['BASE']}; continue
        out[k] = {o: (norm(x) if o in ('FOREGROUND', 'BACKGROUND', 'EFFECT_COLOR', 'ERROR_STRIPE_COLOR') else x)
                  for o, x in a.items() if x not in (None, '')}
    return out
LEGACY = {v: _legacy(v) for v in VARIANTS}
# 'vscode': syntax keys resolved from VS Code scopes (syntax/); 'v010': the v0.1.0 token design.
# The user compared both against VS Code and wants VS Code's colours (2026-11-05).
SYNTAX_DESIGN = 'vscode'
LEGACY_ALL = set().union(*LEGACY.values())
LEGACY_BASE = {
    'DEFAULT_CLASS_REFERENCE': 'DEFAULT_CLASS_NAME', 'DEFAULT_REASSIGNED_LOCAL_VARIABLE': 'DEFAULT_LOCAL_VARIABLE',
    'DEFAULT_REASSIGNED_PARAMETER': 'DEFAULT_PARAMETER', 'DEFAULT_DOC_COMMENT_TAG_VALUE': 'DEFAULT_DOC_COMMENT',
    'PHP_CONSTANT': 'DEFAULT_CONSTANT', 'PHP_NAMED_ARGUMENT': 'DEFAULT_PARAMETER', 'PHP_ALIAS_REFERENCE': 'DEFAULT_CLASS_NAME',
    'STATIC_FINAL_FIELD_ATTRIBUTES': 'DEFAULT_CONSTANT', 'JS.GLOBAL_FUNCTION': 'DEFAULT_FUNCTION_DECLARATION',
    'KOTLIN_CLOSURE_DEFAULT_PARAMETER': 'DEFAULT_PARAMETER', 'KOTLIN_CONTEXT_ARGUMENT': 'DEFAULT_PARAMETER',
    'KOTLIN_NAMED_ARGUMENT': 'DEFAULT_PARAMETER', 'KOTLIN_MUTABLE_VARIABLE': 'DEFAULT_LOCAL_VARIABLE',
    'KOTLIN_PACKAGE_FUNCTION_CALL': 'DEFAULT_FUNCTION_CALL', 'KOTLIN_DYNAMIC_FUNCTION_CALL': 'DEFAULT_FUNCTION_CALL',
    'KOTLIN_DYNAMIC_PROPERTY_CALL': 'DEFAULT_INSTANCE_FIELD', 'KOTLIN_BACKING_FIELD_VARIABLE': 'DEFAULT_INSTANCE_FIELD',
    'KOTLIN_LABEL': 'DEFAULT_LABEL', 'ANNOTATION_NAME_ATTRIBUTES': 'DEFAULT_METADATA',
    'Groovy method declaration': 'DEFAULT_FUNCTION_DECLARATION', 'GROOVY_KEYWORD': 'DEFAULT_KEYWORD',
}

def syntax_attrs(name, key, bg):
    r = SYN[name][key]
    v = {'FOREGROUND': ensure(r['fg'], bg, 4.5, f'{name}:syntax.{key}')}
    st = r['fontStyle'].split()
    ft = (1 if 'bold' in st else 0) | (2 if 'italic' in st else 0)
    if ft: v['FONT_TYPE'] = str(ft)
    if 'underline' in st: v.update(EFFECT_TYPE='1', EFFECT_COLOR=v['FOREGROUND'])
    elif 'strikethrough' in st: v.update(EFFECT_TYPE='3', EFFECT_COLOR=v['FOREGROUND'])
    return v

def snap_attrs(src, cands, bg):
    """Keep a JetBrains attribute's shape, repaint each colour with the nearest Primer colour."""
    def near(c):
        c = c.lstrip('#')
        c = over('#' + (c if len(c) in (6, 8) else c.rjust(6, '0')), bg)
        (r1, _), = [parse(c)]
        return min(cands, key=lambda k: sum((a - b) ** 2 for a, b in zip(parse(k)[0], r1)))
    v = {}
    for k, val in src.items():
        if val in (None, ''): continue
        v[k] = near(val) if k in ('FOREGROUND', 'BACKGROUND', 'EFFECT_COLOR', 'ERROR_STRIPE_COLOR') else val
    if 'FOREGROUND' in v:  # text stays AA on whatever it sits on
        v['FOREGROUND'] = ensure(v['FOREGROUND'], v.get('BACKGROUND', bg), 4.5)
    return v

# ---------------------------------------------------------------- main
def main():
    os.makedirs(os.path.join(OUT, 'scheme'), exist_ok=True)
    for name, (display, dark) in VARIANTS.items():
        theme, P, sel_bg, sel_fg = ui_theme(name, display, dark)
        norm_hex = lambda o: {k: norm_hex(v) for k, v in o.items()} if isinstance(o, dict) else (full(o) if isinstance(o, str) and o.startswith('#') else o)
        theme = norm_hex(theme)
        with open(os.path.join(OUT, f'{name}.theme.json'), 'w') as f:
            json.dump(theme, f, indent=2); f.write('\n')
        with open(os.path.join(OUT, 'scheme', f'{name}.xml'), 'w') as f:
            f.write(scheme(name, display, dark, P, sel_bg, sel_fg))
    with open(os.path.join(OUT, 'parity.txt'), 'w') as f:
        f.write('# IntelliJ key -> VS Code scope (resolved per variant by vscode-textmate)\n')
        for e in SYN_ERRORS: f.write(f'ERROR {e}\n')
        for k in sorted(SYN_SCOPES):
            f.write(f'{k}\t{SYN_ORIGIN[k]}\t{SYN_SCOPES[k]}' + (f'\t# {SYN_NOTES[k]}' if k in SYN_NOTES else '') + '\n')
        f.write('# keys still on the legacy role heuristic (no VS Code scope mapped)\n')
        for k in UNMAPPED.get('dark-default', []): f.write(f'UNMAPPED {k}\n')
    if SYN_ERRORS: print(f'syntax map: {len(SYN_ERRORS)} errors (see parity.txt)')
    print(f"syntax map: {len(SYN_SCOPES)} keys mapped, {len(UNMAPPED.get('dark-default', []))} legacy keys unmapped")
    print('AA adjustments (label, primer value, adjusted, before, after):')
    for a in ADJUSTED: print('  ', *a)

if __name__ == '__main__':
    main()
