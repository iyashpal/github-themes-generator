#!/usr/bin/env python3
"""Render a preview image of every theme.

Reads each generated `resources/theme/<variant>.theme.json` and its editor
scheme, draws an Islands-style IDE window (main toolbar, stripes, Project
tool window, editor with a Kotlin sample and a completion popup, status bar)
as HTML using only those colors, and screenshots it with headless Chrome.

    python3 preview.py [--out DIR] [--scale N] [variant ...]

Output: DIR/<variant>.png (default DIR: ../../public/images/previews) and
the intermediate HTML in out/previews/.
"""
import argparse
import html
import json
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
THEMES = os.path.join(ROOT, 'resources', 'theme')
CHROME = os.environ.get(
    'CHROME', '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')

VARIANTS = ['dark', 'dark-default', 'dark-dimmed', 'dark-colorblind',
            'dark-tritanopia', 'dark-high-contrast', 'light', 'light-default',
            'light-colorblind', 'light-tritanopia', 'light-high-contrast']

W, H = 1280, 800

# ---------------------------------------------------------------- colors

missing = set()


class Theme:
    def __init__(self, variant):
        with open(os.path.join(THEMES, f'{variant}.theme.json')) as f:
            t = json.load(f)
        self.name = t['name']
        self.dark = t['dark']
        self.named = t['colors']
        self.uimap = t['ui']
        self.star = t['ui'].get('*', {})
        self.icons = t.get('icons', {}).get('ColorPalette', {})
        scheme = ET.parse(os.path.join(ROOT, 'resources', t['editorScheme'].lstrip('/')))
        self.scolors = {o.get('name'): o.get('value')
                        for o in scheme.getroot().find('colors')}
        self.attrs = {}
        for o in scheme.getroot().find('attributes'):
            v = o.find('value')
            self.attrs[o.get('name')] = {} if v is None else {
                x.get('name'): x.get('value') for x in v}

    def _hex(self, v):
        v = str(v)
        if v in self.named:
            v = self.named[v]
        if not v.startswith('#'):
            v = '#' + v
        return v

    def ui(self, *keys):
        """First key that the theme sets; falls back to the "*" suffix block."""
        for k in keys:
            if k in self.uimap:
                return self._hex(self.uimap[k])
        for k in keys:
            suffix = k.split('.')[-1]
            if suffix in self.star:
                return self._hex(self.star[suffix])
        missing.add(keys[0])
        return '#ff00ff'

    def c(self, name):
        return self._hex(self.named[name])

    def scheme(self, key):
        v = self.scolors.get(key)
        if not v:
            missing.add(key)
            return '#ff00ff'
        return '#' + v

    def token(self, key):
        """CSS for a syntax attribute key."""
        a = self.attrs.get(key)
        if a is None:
            missing.add(key)
            a = {}
        fg = a.get('FOREGROUND') or self.attrs['TEXT']['FOREGROUND']
        css = [f'color:#{fg}']
        ft = int(a.get('FONT_TYPE', 0) or 0)
        if ft & 1:
            css.append('font-weight:700')
        if ft & 2:
            css.append('font-style:italic')
        if a.get('BACKGROUND') and key != 'TEXT':
            css.append(f"background:#{a['BACKGROUND']}")
        if a.get('EFFECT_COLOR') and a.get('EFFECT_TYPE') in ('1', '2'):
            css.append(f"text-decoration:underline #{a['EFFECT_COLOR']}")
        return ';'.join(css)


# ---------------------------------------------------------------- code

# «key:text» marks a token; key is an alias below or a scheme attribute key.
ALIAS = {
    'k': 'KOTLIN_KEYWORD', 'v': 'KOTLIN_KEYWORD_VAL', 'cls': 'KOTLIN_CLASS',
    'enum': 'KOTLIN_ENUM', 'data': 'KOTLIN_DATA_CLASS',
    'entry': 'KOTLIN_ENUM_ENTRY', 'prop': 'KOTLIN_INSTANCE_PROPERTY',
    'local': 'KOTLIN_LOCAL_VARIABLE', 'param': 'KOTLIN_PARAMETER',
    'named': 'KOTLIN_NAMED_ARGUMENT', 'fd': 'KOTLIN_FUNCTION_DECLARATION',
    'ctor': 'KOTLIN_CONSTRUCTOR', 'ext': 'KOTLIN_EXTENSION_FUNCTION_CALL',
    'pkgfn': 'KOTLIN_PACKAGE_FUNCTION_CALL', 'it': 'KOTLIN_CLOSURE_DEFAULT_PARAMETER',
    's': 'KOTLIN_STRING', 'n': 'KOTLIN_NUMBER', 'c': 'KOTLIN_LINE_COMMENT',
    'doc': 'KOTLIN_DOC_COMMENT', 'link': 'KDOC_LINK', 'tag': 'KDOC_TAG_NAME',
    'ann': 'KOTLIN_ANNOTATION', 'op': 'KOTLIN_OPERATION_SIGN',
    'br': 'KOTLIN_BRACES', 'lb': 'KOTLIN_FUNCTION_LITERAL_BRACES_AND_ARROW',
    'p': 'KOTLIN_PARENTHESIS', 'cm': 'KOTLIN_COMMA', 'dot': 'KOTLIN_DOT',
    'col': 'KOTLIN_COLON', 'semi': 'KOTLIN_SEMICOLON', 'id': 'TEXT',
}

CODE = r'''«k:package» «id:dev.yashpal.themes»

«k:import» «id:java.awt.»«cls:Color»

«doc:/**»
«doc: * A GitHub theme variant and its» «link:[Palette]»«doc:.»
«doc: * »«tag:@property»«doc: id the theme file name»
«doc: */»
«k:enum» «k:class» «enum:Variant»«p:(»«v:val» «prop:id»«col::» «cls:String»«cm:,» «v:val» «prop:dark»«col::» «cls:Boolean»«p:)» «br:{»
    «entry:DARK_DEFAULT»«p:(»«s:"dark-default"»«cm:,» «k:true»«p:)»«cm:,»
    «entry:DARK_DIMMED»«p:(»«s:"dark-dimmed"»«cm:,» «k:true»«p:)»«cm:,»
    «entry:LIGHT_DEFAULT»«p:(»«s:"light-default"»«cm:,» «k:false»«p:)»«semi:;»
«br:}»

«ann:@JvmInline»
«k:value» «k:class» «cls:Hex»«p:(»«v:val» «prop:rgb»«col::» «cls:Int»«p:)»

«k:data» «k:class» «data:Palette»«p:(»«v:val» «prop:canvas»«col::» «cls:Hex»«cm:,» «v:val» «prop:accent»«col::» «cls:Hex»«p:)»

«k:fun» «enum:Variant»«dot:.»«fd:palette»«p:()»«col::» «data:Palette» «br:{»
    «c:// Primer canvas.default and accent.fg»
    «v:val» «local:canvas» «op:=» «k:if» «p:(»«prop:dark»«p:)» «ctor:Hex»«p:(»«n:0x0d1117»«p:)» «k:else» «ctor:Hex»«p:(»«n:0xffffff»«p:)»
    «k:return» «ctor:Palette»«p:(»«named:canvas» «op:=» «local:canvas»«cm:,» «named:accent» «op:=» «ctor:Hex»«p:(»«n:0x2f81f7»«p:))»
«br:}»

«k:fun» «fd:main»«p:()» «br:{»
    «v:val» «local:dark» «op:=» «enum:Variant»«dot:.»«prop:entries»«dot:.»«ext:filter» «lb:{» «it:it»«dot:.»«prop:dark» «lb:}»
    «local:dark»«dot:.»«ext:forEach» «lb:{» «pkgfn:println»«p:(»«it:it»«dot:.»«prop:id» «op:+» «s:" has "» «op:+» «it:it»«dot:.»«ext:pal»'''

CARET_LINE = CODE.count('\n') + 1  # last line ends at the caret, with the completion popup
SELECT_LINE = 22  # line with a selection over `canvas`
ADDED_LINES = (15, 16)
MODIFIED_LINES = (22,)
SELECT_FROM, SELECT_TO = 8, 14


def render_code(t):
    lines = []
    tok = re.compile(r'«([^:»]+):(.*?)»')
    for i, raw in enumerate(CODE.split('\n'), 1):
        out, pos = [], 0
        col = 0
        for m in tok.finditer(raw):
            plain = raw[pos:m.start()]
            out.append(('TEXT', plain))
            key = ALIAS.get(m.group(1), m.group(1))
            out.append((key, m.group(2)))
            pos = m.end()
        out.append(('TEXT', raw[pos:]))
        # split the selection range into its own spans
        spans = []
        for key, text in out:
            for ch in text:
                sel = i == SELECT_LINE and SELECT_FROM <= col < SELECT_TO
                if spans and spans[-1][0] == key and spans[-1][1] == sel:
                    spans[-1][2] += ch
                else:
                    spans.append([key, sel, ch])
                col += 1
        h = []
        for key, sel, text in spans:
            style = t.token(key)
            if sel:
                style += f';background:{t.scheme("SELECTION_BACKGROUND")}'
                if t.scolors.get('SELECTION_FOREGROUND'):
                    style += f';color:#{t.scolors["SELECTION_FOREGROUND"]}'
            h.append(f'<span style="{style}">{html.escape(text)}</span>')
        if i == CARET_LINE:
            h.append('<span class="caret">{POPUP}</span>')
        # indent guides for 4-space blocks
        indent = len(raw) - len(raw.lstrip(' '))
        guides = ''.join(f'<i class="guide" style="left:{g * 4}ch"></i>'
                         for g in range(indent // 4))
        cls = 'line caret-row' if i == CARET_LINE else 'line'
        lines.append(f'<div class="{cls}">{guides}{"".join(h) or "&#8203;"}</div>')
    return ''.join(lines), len(lines)


# ---------------------------------------------------------------- icons

def svg(path, color, size=16, fill='none', sw=1.3):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 16 16" fill="{fill}" '
            f'stroke="{color}" stroke-width="{sw}" stroke-linecap="round" '
            f'stroke-linejoin="round">{path}</svg>')


I = {
    'folder': '<path d="M1.5 4.5v8a1 1 0 0 0 1 1h11a1 1 0 0 0 1-1v-6.5a1 1 0 0 0-1-1H8L6.5 3.5h-4a1 1 0 0 0-1 1z"/>',
    'file': '<path d="M4 1.5h5l3.5 3.5v9a.5.5 0 0 1-.5.5H4a.5.5 0 0 1-.5-.5v-12A.5.5 0 0 1 4 1.5z"/><path d="M9 1.5V5h3.5"/>',
    'chev': '<path d="M6 4l4 4-4 4"/>',
    'chevd': '<path d="M4 6l4 4 4-4"/>',
    'project': '<rect x="2" y="2.5" width="12" height="11" rx="1.5"/><path d="M2 6h12"/>',
    'commit': '<circle cx="8" cy="8" r="2.5"/><path d="M1.5 8h4M10.5 8h4"/>',
    'struct': '<rect x="2" y="2" width="5" height="5" rx="1"/><rect x="9" y="9" width="5" height="5" rx="1"/><path d="M4.5 7v4.5H9"/>',
    'more': '<circle cx="3.5" cy="8" r=".6"/><circle cx="8" cy="8" r=".6"/><circle cx="12.5" cy="8" r=".6"/>',
    'run': '<path d="M5 3.5v9l7-4.5z"/>',
    'debug': '<path d="M5.5 6.5a2.5 2.5 0 0 1 5 0V10a2.5 2.5 0 0 1-5 0z"/><path d="M2.5 8.5h3M10.5 8.5h3M3 5l2.5 1.5M13 5l-2.5 1.5M3 12.5l2.5-1.5M13 12.5l-2.5-1.5"/>',
    'search': '<circle cx="7" cy="7" r="4.5"/><path d="M10.5 10.5l3 3"/>',
    'gear': '<circle cx="8" cy="8" r="2"/><path d="M8 1.5v2M8 12.5v2M1.5 8h2M12.5 8h2M3.4 3.4l1.4 1.4M11.2 11.2l1.4 1.4M3.4 12.6l1.4-1.4M11.2 4.8l1.4-1.4"/>',
    'branch': '<circle cx="4.5" cy="3.5" r="1.5"/><circle cx="4.5" cy="12.5" r="1.5"/><circle cx="11.5" cy="5.5" r="1.5"/><path d="M4.5 5v6M11.5 7c0 2.5-7 1.5-7 4"/>',
    'terminal': '<rect x="1.5" y="2.5" width="13" height="11" rx="1.5"/><path d="M4.5 6l2 2-2 2M8.5 10.5h3"/>',
    'problems': '<circle cx="8" cy="8" r="6"/><path d="M8 4.8v3.7M8 11v.2"/>',
    'bell': '<path d="M4 11V7a4 4 0 0 1 8 0v4l1 1.5H3z"/><path d="M6.5 14h3"/>',
    'db': '<ellipse cx="8" cy="4" rx="5" ry="2"/><path d="M3 4v8c0 1.1 2.2 2 5 2s5-.9 5-2V4M3 8c0 1.1 2.2 2 5 2s5-.9 5-2"/>',
    'check': '<path d="M3.5 8.5l3 3 6-6.5"/>',
    'kt': None,
}


def kt_icon(color):
    return (f'<svg width="16" height="16" viewBox="0 0 16 16"><path d="M2.5 2.5h11L8 8l5.5 5.5h-11z" '
            f'fill="{color}" opacity=".9"/></svg>')


# ---------------------------------------------------------------- page

def page(variant):
    t = Theme(variant)
    C = t.c
    mono = "'JetBrains Mono', Menlo, monospace"

    tree_fg = t.ui('Tree.foreground')
    icon = t.icons.get('Tree.iconColor', C('mutedForeground'))
    kt = C('accentColor')
    stripe_fg = t.ui('ToolWindow.Button.foreground')

    def stripe(name, sel=False):
        bg = t.ui('ToolWindow.Button.selectedBackground') if sel else 'transparent'
        fg = t.ui('ToolWindow.Button.selectedForeground') if sel else stripe_fg
        return f'<div class="sbtn" style="background:{bg}">{svg(I[name], fg, 18)}</div>'

    tree = [
        (0, 'chevd', 'folder', 'github-themes', False, None),
        (1, 'chevd', 'folder', 'src', False, None),
        (2, 'chevd', 'folder', 'dev.yashpal.themes', False, None),
        (3, None, 'kt', 'Palette.kt', False, None),
        (3, None, 'kt', 'Variant.kt', True, t.ui('Tree.modifiedItemForeground', 'FileColor.Blue')),
        (3, None, 'kt', 'Main.kt', False, None),
        (1, 'chev', 'folder', 'resources', False, None),
        (1, 'chev', 'folder', 'build', False, t.scheme('FILESTATUS_IDEA_FILESTATUS_IGNORED')),
        (1, None, 'file', 'build.gradle.kts', False, None),
        (1, None, 'file', 'README.md', False, t.scheme('FILESTATUS_MODIFIED')),
        (0, 'chev', 'folder', 'External Libraries', False, None),
    ]
    rows = []
    for depth, chev, ic, label, sel, fg in tree:
        bg = f'background:{t.ui("Tree.selectionBackground")};' if sel else ''
        color = t.ui('Tree.selectionForeground') if sel and 'Tree.selectionForeground' in t.uimap else (fg or tree_fg)
        ch = svg(I[chev], icon, 14) if chev else '<span style="width:14px"></span>'
        ico = kt_icon(kt) if ic == 'kt' else svg(I[ic], icon, 16)
        rows.append(f'<div class="row" style="{bg}padding-left:{8 + depth * 18}px;color:{color}">'
                    f'{ch}{ico}<span>{html.escape(label)}</span></div>')

    tabs = [('Variant.kt', True), ('Palette.kt', False), ('Main.kt', False)]
    tab_html = []
    for label, sel in tabs:
        if sel:
            st = (f'background:{t.ui("EditorTabs.underlinedTabBackground", "EditorTabs.selectedBackground")};'
                  f'color:{t.ui("EditorTabs.underlinedTabForeground")};'
                  f'box-shadow:inset 0 -2px 0 {t.ui("EditorTabs.underlineColor")}')
        else:
            st = f'color:{C("foreground")}'
        tab_html.append(f'<div class="tab" style="{st}">{kt_icon(kt)}<span>{label}</span>'
                        f'<span class="x" style="color:{C("mutedForeground")}">×</span></div>')

    gutter = []
    for i in range(1, CARET_LINE + 1):
        col = t.scheme('LINE_NUMBER_ON_CARET_ROW_COLOR') if i == CARET_LINE else t.scheme('LINE_NUMBERS_COLOR')
        mark = ''
        if i in ADDED_LINES:
            mark = f'<i class="vcs" style="background:{t.scheme("ADDED_LINES_COLOR")}"></i>'
        elif i in MODIFIED_LINES:
            mark = f'<i class="vcs" style="background:{t.scheme("MODIFIED_LINES_COLOR")}"></i>'
        gutter.append(f'<div class="ln" style="color:{col}">{i}{mark}</div>')

    items = [('pal', 'ette()', 'Palette', 'fd'), ('pal', 'etteOrNull()', 'Palette?', 'fd'),
             ('pal', 'etteName', 'String', 'prop')]
    pop = []
    for n, (m, rest, typ, kind) in enumerate(items):
        sel = n == 0
        bg = f'background:{t.ui("CompletionPopup.selectionBackground")};' if sel else ''
        badge_c = C('accentColor') if kind == 'fd' else C('warningColor')
        badge = 'f' if kind == 'fd' else 'p'
        pop.append(
            f'<div class="item" style="{bg}"><span class="badge" style="color:{badge_c};border-color:{badge_c}">{badge}</span>'
            f'<span><b style="color:{t.ui("CompletionPopup.matchForeground")};font-weight:600">{m}</b>'
            f'<span style="color:{t.ui("CompletionPopup.foreground")}">{rest}</span></span>'
            f'<span class="type" style="color:{C("mutedForeground")}">{typ}</span></div>')

    code_html, nlines = render_code(t)
    code_html = code_html.replace('{POPUP}', '<div class="popup">' + ''.join(pop) + '<div class="adv">Press ⏎ to insert, → to replace</div></div>')
    caret_col = len(re.sub(r'«[^:»]+:(.*?)»', r'\1', CODE.split('\n')[-1])) + 1
    wtitle = t.ui('MainToolbar.Dropdown.foreground')
    tool_fg = t.ui('MainToolbar.foreground')
    status_fg = t.ui('StatusBar.Widget.foreground')
    crumbs = t.ui('StatusBar.Breadcrumbs.foreground')
    run_c = C('successColor')

    return f'''<!doctype html><html><head><meta charset="utf-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;700&display=block" rel="stylesheet">
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{width:{W}px;height:{H}px;overflow:hidden;background:{C('frameBackground')}}}
body{{font:13px/1 Inter,-apple-system,sans-serif;color:{C('foreground')};-webkit-font-smoothing:antialiased}}
.win{{position:absolute;inset:0;background:{t.ui('MainWindow.background')};display:grid;
  grid-template-rows:40px 1fr 30px;grid-template-columns:40px 1fr 40px}}
.toolbar{{grid-column:1/4;display:flex;align-items:center;gap:6px;padding:0 10px;color:{tool_fg}}}
.lights{{display:flex;gap:8px;margin-right:14px}}
.lights i{{width:12px;height:12px;border-radius:50%;display:block}}
.dd{{display:flex;align-items:center;gap:6px;padding:6px 8px;border-radius:6px;color:{wtitle};font-weight:500}}
.avatar{{width:20px;height:20px;border-radius:5px;display:grid;place-items:center;color:#fff;font-size:10px;font-weight:600;
  background:linear-gradient(135deg,{t.ui('RecentProject.Color5.Avatar.Start')},{t.ui('RecentProject.Color5.Avatar.End')})}}
.ib{{width:28px;height:28px;display:grid;place-items:center;border-radius:6px}}
.sp{{flex:1}}
.stripe{{display:flex;flex-direction:column;align-items:center;gap:4px;padding-top:4px}}
.sbtn{{width:30px;height:30px;border-radius:6px;display:grid;place-items:center}}
.sep{{width:18px;height:1px;background:{t.ui('ToolWindow.Stripe.separatorColor')};margin:4px 0}}
.main{{display:grid;grid-template-columns:264px 1fr;gap:4px;padding:0 0 0 0;min-height:0}}
.island{{background:{C('background')};border-radius:10px;overflow:hidden;position:relative;min-height:0}}
.thead{{height:38px;display:flex;align-items:center;gap:6px;padding:0 12px;font-weight:600;color:{C('foreground')};
  background:{t.ui('ToolWindow.Header.background')}}}
.row{{height:24px;display:flex;align-items:center;gap:5px;white-space:nowrap;margin:0 6px;border-radius:5px}}
.row svg{{flex:none}}
.tabs{{height:38px;display:flex;align-items:stretch;background:{t.ui('EditorTabs.background')};
  box-shadow:inset 0 -1px 0 {t.ui('EditorTabs.underTabsBorderColor', 'EditorTabs.borderColor')}}}
.tab{{display:flex;align-items:center;gap:6px;padding:0 12px}}
.tab .x{{font-size:15px;margin-left:2px}}
.editor{{position:absolute;top:38px;left:0;right:0;bottom:0;display:flex;background:#{t.attrs['TEXT']['BACKGROUND']};
  font:13px/20px {mono};font-variant-ligatures:contextual}}
.gutter{{width:58px;flex:none;text-align:right;padding:8px 18px 0 0;background:{t.scheme('GUTTER_BACKGROUND')};position:relative}}
.ln{{position:relative}}
.vcs{{position:absolute;right:-12px;top:2px;width:3px;height:16px;border-radius:1px}}
.code{{flex:1;padding:8px 0 0 8px;white-space:pre;position:relative;color:#{t.attrs['TEXT']['FOREGROUND']}}}
.line{{position:relative;margin-left:-8px;padding-left:8px}}
.caret-row{{background:{t.scheme('CARET_ROW_COLOR')}}}
.guide{{position:absolute;top:0;bottom:0;width:1px;margin-left:8px;background:{t.scheme('INDENT_GUIDE')}}}
.caret{{display:inline-block;position:relative;width:2px;height:17px;vertical-align:-4px;background:{t.scheme('CARET_COLOR')}}}
.popup{{position:absolute;left:-60px;top:21px;width:330px;white-space:nowrap;z-index:2;
  background:{t.ui('CompletionPopup.background')};border:1px solid {t.ui('Popup.borderColor')};border-radius:8px;
  box-shadow:0 8px 24px rgba(0,0,0,{0.45 if t.dark else 0.15});padding:4px;font:13px/1 {mono}}}
.item{{height:26px;display:flex;align-items:center;gap:8px;padding:0 8px;border-radius:5px}}
.badge{{width:16px;height:16px;border:1.3px solid;border-radius:50%;display:grid;place-items:center;font:600 9px/1 Inter,sans-serif}}
.type{{margin-left:auto}}
.adv{{font:11px/1 Inter,sans-serif;color:{t.ui('CompletionPopup.Advertiser.foreground')};padding:8px 8px 4px}}
.status{{grid-column:1/4;display:flex;align-items:center;gap:16px;padding:0 14px;color:{status_fg};font-size:12px}}
.crumbs{{display:flex;align-items:center;gap:4px;color:{crumbs}}}
</style></head><body><div class="win">
<div class="toolbar">
  <div class="lights"><i style="background:#ff5f57"></i><i style="background:#febc2e"></i><i style="background:#28c840"></i></div>
  <div class="dd"><span class="avatar">GT</span>github-themes{svg(I['chevd'], tool_fg, 12)}</div>
  <div class="dd" style="font-weight:400">{svg(I['branch'], tool_fg, 15)}main{svg(I['chevd'], tool_fg, 12)}</div>
  <div class="sp"></div>
  <div class="dd" style="font-weight:400">{kt_icon(kt)}MainKt{svg(I['chevd'], tool_fg, 12)}</div>
  <div class="ib">{svg(I['run'], run_c, 16, fill=run_c)}</div>
  <div class="ib">{svg(I['debug'], tool_fg, 16)}</div>
  <div class="ib">{svg(I['more'], tool_fg, 16, sw=2)}</div>
  <div class="ib" style="margin-left:10px">{svg(I['search'], tool_fg, 16)}</div>
  <div class="ib">{svg(I['gear'], tool_fg, 16)}</div>
</div>
<div class="stripe" style="background:{t.ui('ToolWindow.Stripe.background')}">
  {stripe('project', True)}{stripe('commit')}{stripe('struct')}{stripe('more')}
  <div class="sp"></div>{stripe('terminal')}{stripe('problems')}{stripe('branch')}<div style="height:6px"></div>
</div>
<div class="main">
  <div class="island">
    <div class="thead">Project{svg(I['chevd'], C('mutedForeground'), 12)}</div>
    {''.join(rows)}
  </div>
  <div class="island">
    <div class="tabs">{''.join(tab_html)}</div>
    <div class="editor"><div class="gutter">{''.join(gutter)}</div><div class="code">{code_html}</div></div>
  </div>
</div>
<div class="stripe" style="background:{t.ui('ToolWindow.Stripe.background')}">
  {stripe('bell')}{stripe('db')}
</div>
<div class="status">
  <div class="crumbs">github-themes{svg(I['chev'], crumbs, 10)}src{svg(I['chev'], crumbs, 10)}dev.yashpal.themes{svg(I['chev'], crumbs, 10)}{kt_icon(kt)}Variant.kt</div>
  <div class="sp"></div>
  <span>{CARET_LINE}:{caret_col}</span><span>LF</span><span>UTF-8</span><span>4 spaces</span>
  <span style="display:flex;gap:5px;align-items:center">{svg(I['check'], C('successColor'), 14)}{html.escape(t.name)}</span>
</div>
</div></body></html>'''


def shoot(html_path, png, scale, tries=3, size=(W, H)):
    """Screenshot with a fresh Chrome profile; headless Chrome is sometimes killed, so retry."""
    import tempfile
    for n in range(tries):
        with tempfile.TemporaryDirectory() as prof:
            r = subprocess.run([CHROME, f'--user-data-dir={prof}', '--headless=new', '--disable-gpu', '--hide-scrollbars',
                                f'--window-size={size[0]},{size[1]}', f'--force-device-scale-factor={scale}',
                                '--virtual-time-budget=5000', f'--screenshot={png}',
                                'file://' + html_path],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if r.returncode == 0 and os.path.exists(png):
            return
    raise SystemExit(f'Chrome failed to render {html_path}')


# ---------------------------------------------------------------- banner

BANNER_W, BANNER_H = 1600, 1000
# back to front: (variant, left, top, width)
BANNER_STACK = [('dark-dimmed', 1089, 160, 396), ('dark', 949, 333, 504),
                ('dark-default', 740, 437, 653), ('light-default', 178, 469, 762)]


def banner_page(previews):
    with open(os.path.join(ROOT, 'resources', 'META-INF', 'pluginIcon.svg')) as f:
        icon = f.read()
    wins = ''.join(
        f'<img class="w" src="file://{os.path.join(previews, v + ".png")}" '
        f'style="left:{x}px;top:{y}px;width:{w}px">'
        for v, x, y, w in BANNER_STACK)
    return f'''<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;700&display=block" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:{BANNER_W}px;height:{BANNER_H}px;overflow:hidden;background:#3d4450}}
body{{position:relative;font-family:Inter,-apple-system,sans-serif;color:#e6edf3;-webkit-font-smoothing:antialiased}}
.icon{{position:absolute;left:222px;top:106px;width:256px;height:256px;border-radius:50%;
  box-shadow:0 18px 40px rgba(0,0,0,.35)}}
.icon svg{{width:100%;height:100%}}
h1{{position:absolute;left:536px;top:150px;font-size:66px;line-height:84px;font-weight:300;letter-spacing:-.5px}}
h1 b{{font-weight:700}}
.w{{position:absolute;border-radius:8px;box-shadow:0 14px 40px rgba(0,0,0,.45),0 0 0 1px rgba(255,255,255,.06)}}
</style></head><body>
<div class="icon">{icon}</div>
<h1><b>GitHub</b> themes<br>for <b>IntelliJ</b></h1>
{wins}
</body></html>'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('variants', nargs='*', default=VARIANTS)
    ap.add_argument('--out', default=os.path.join(ROOT, 'public', 'images', 'previews'))
    ap.add_argument('--scale', type=int, default=2)
    ap.add_argument('--banner', action='store_true',
                    help='only compose OUT/../banner.png from existing previews')
    a = ap.parse_args()
    hdir = os.path.join(HERE, 'out', 'previews')
    os.makedirs(hdir, exist_ok=True)
    os.makedirs(a.out, exist_ok=True)
    if a.banner:
        hp = os.path.join(hdir, 'banner.html')
        with open(hp, 'w') as f:
            f.write(banner_page(os.path.abspath(a.out)))
        png = os.path.join(os.path.dirname(os.path.abspath(a.out)), 'banner.png')
        shoot(hp, png, a.scale, size=(BANNER_W, BANNER_H))
        print(f'banner: {os.path.relpath(png, ROOT)}')
        return
    for v in a.variants:
        hp = os.path.join(hdir, f'{v}.html')
        with open(hp, 'w') as f:
            f.write(page(v))
        png = os.path.join(a.out, f'{v}.png')
        shoot(hp, png, a.scale)
        print(f'{v}: {os.path.relpath(png, ROOT)}')
    if missing:
        print('missing keys (drawn magenta):', ', '.join(sorted(missing)), file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
