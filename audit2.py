import json,glob,os,sys
import xml.etree.ElementTree as ET
sys.path.insert(0,'.'); from gen_themes import over, contrast, VS, roles
D=sys.argv[1]
T={};S={}
for f in sorted(glob.glob(D+'/*.theme.json')):
    n=os.path.basename(f)[:-11]; d=json.load(open(f)); c=d['colors']
    r=lambda v:c.get(v,v) if isinstance(v,str) else v
    ui={('*.'+k):r(v) for k,v in d['ui']['*'].items()}; ui.update({k:r(v) for k,v in d['ui'].items() if k!='*'}); T[n]=ui
for f in sorted(glob.glob(D+'/scheme/*.xml')):
    n=os.path.basename(f)[:-4]; root=ET.parse(f).getroot()
    cols={o.get('name'):'#'+o.get('value') for o in root.find('colors')}
    at={}
    for o in root.find('attributes'):
        v=o.find('value'); at[o.get('name')]={x.get('name'):x.get('value') for x in v} if v is not None else {'BASE':o.get('baseAttributes')}
    S[n]=(cols,at)
fails=[]
def chk(no,desc,n,a,b,m):
    r=contrast(over(a,over(b,'#000000')),over(b,'#000000'))
    if r<m: fails.append(f"#{no} {n}: {desc} = {r:.2f} < {m}")
ks=[set(t) for t in T.values()]; print('UI key parity:',all(k==ks[0] for k in ks), len(ks[0]),'keys')
ak=[set(a) for c,a in S.values()]; print('scheme attr parity:',all(k==ak[0] for k in ak), len(ak[0]),'attrs')
ck=[set(c) for c,a in S.values()]; print('scheme color parity:',all(k==ck[0] for k in ck))
for n,t in T.items():
    bg=t['*.background']; ins=t['ToolWindow.background']; ov=t['Popup.background']
    cols,at=S[n]; ebg='#'+at['TEXT']['BACKGROUND']
    # 1 VCS hover subtle
    r=contrast(t['VersionControl.Log.Commit.hoveredBackground'],ins)
    if r>1.6: fails.append(f"#1 {n}: commit hover too strong {r:.2f}")
    # 2 settings bg is a surface
    r=contrast(t['SearchEverywhere.List.settingsBackground'],ov)
    if r>1.3: fails.append(f"#2 {n}: SE settings bg differs from popup {r:.2f}")
    # 3 editor selection readability: every syntax fg vs selection
    sb=cols['SELECTION_BACKGROUND']; sf=cols.get('SELECTION_FOREGROUND','#').lstrip('#')
    for an in ('TEXT','DEFAULT_KEYWORD','DEFAULT_STRING','DEFAULT_CONSTANT','DEFAULT_FUNCTION_DECLARATION','DEFAULT_LINE_COMMENT'):
        f='#'+(sf.lstrip('#') if sf else at[an]['FOREGROUND']); chk(3,f'{an} on selection',n,f,sb,4.5 if an=='TEXT' else 3.0)
    # 4 memory indicator
    chk(4,'memory used vs allocated',n,t['MemoryIndicator.usedBackground'],t['MemoryIndicator.allocatedBackground'],1.3)
    # 6 primary button + focus ring
    chk(6,'primary button text',n,t['Button.default.foreground'],t['Button.default.startBackground'],4.5)
    chk(6,'primary focus ring vs bg',n,t['Button.default.focusColor'],bg,3)
    # 7 text AA
    for a,b in [('Label.errorForeground','*.background'),('Link.hoverForeground','*.background'),('Link.activeForeground','*.background'),
                ('SearchField.errorForeground','SearchField.errorBackground'),('SpeedSearch.errorForeground','SpeedSearch.background'),
                ('Notification.ToolWindow.errorForeground','Notification.ToolWindow.errorBackground'),
                ('Notification.ToolWindow.warningForeground','Notification.ToolWindow.warningBackground'),
                ('Notification.ToolWindow.informativeForeground','Notification.ToolWindow.informativeBackground'),
                ('Notification.errorForeground','Notification.errorBackground'),
                ('MenuItem.acceleratorForeground','Popup.background'),('Bookmark.MnemonicAssigned.foreground','Bookmark.MnemonicAssigned.background'),
                ('Bookmark.MnemonicCurrent.foreground','Bookmark.MnemonicCurrent.background'),
                ('UnattendedHostStatus.warningForeground','UnattendedHostStatus.warningBackground'),
                ('*.foreground','*.background'),('*.foreground','ToolWindow.background'),('*.foreground','Popup.background'),
                ('*.selectionForeground','*.selectionBackground'),('Counter.foreground','Counter.background'),
                ('CompletionPopup.matchForeground','Popup.background'),('ToolTip.foreground','ToolTip.background'),
                ('TextField.selectionForeground','TextField.selectionBackground'),('Button.foreground','Button.startBackground'),
                ('Plugins.Button.installForeground','Plugins.Button.installBackground')]+[(f'CodeWithMe.Users.{i}.Foreground',f'CodeWithMe.Users.{i}.Background') for i in range(1,7)]:
        chk(7,f'{a} on {b}',n,t[a],t[b],4.5)
    # 8 syntax AA on editor bg
    for an,v in at.items():
        f=v.get('FOREGROUND')
        if f and 'BACKGROUND' not in v and not an.startswith(('CONSOLE_BLACK','CONSOLE_WHITE','CONSOLE_GRAY','CONSOLE_DARKGRAY','LOG_EXPIRED','NOT_USED','INLAY','BREADCRUMBS_INACTIVE','TERMINAL')) and 'CONSOLE' not in an and 'LOG_' not in an:
            chk(8,f'{an} on editor',n,'#'+f,ebg,4.5 if 'COMMENT' not in an.upper() and 'DOC' not in an.upper() and 'COVERAGE' not in an else 3.0)  # coverage = gutter marks (non-text)
        if f and (an.startswith('CONSOLE_') or an.startswith('LOG_')) and an not in ('CONSOLE_BLACK_OUTPUT','CONSOLE_WHITE_OUTPUT','CONSOLE_GRAY_OUTPUT','CONSOLE_DARKGRAY_OUTPUT','LOG_EXPIRED_ENTRY'):
            chk(8,f'{an} on console',n,'#'+f,cols['CONSOLE_BACKGROUND_KEY'],4.5)
    # 9 focus ring
    chk(9,'focus ring',n,t['Component.focusColor'],bg,3)
    # Islands structure: no frame borders, no island ring, islands share the editor canvas, frame distinct
    for k in ('StatusBar.borderColor','MainToolbar.borderColor','ToolWindow.borderColor','ToolWindow.Stripe.borderColor','ActionButton.hoverBorderColor'):
        if t[k].lower()!='#00000000': fails.append(f'#S {n}: {k} not transparent ({t[k]})')
    for k in ('Island.borderColor','ToolWindow.background','EditorTabs.background','Tree.background'):
        if t[k].lower()!=ebg.lower(): fails.append(f'#S {n}: {k} {t[k]} != editor {ebg}')
    fr=t['MainWindow.background']
    for k in ('MainToolbar.background','StatusBar.background','ToolWindow.Stripe.background'):
        if t[k]!=fr: fails.append(f'#S {n}: {k} not on frame')
    if contrast(fr,ebg)<1.05: fails.append(f'#S {n}: frame vs island indistinct {contrast(fr,ebg):.2f}')
    # 10 line numbers dimmer than text but >=3
    chk(10,'line numbers',n,cols['LINE_NUMBERS_COLOR'],ebg,3)
    if cols['LINE_NUMBERS_COLOR']=='#'+at['TEXT']['FOREGROUND']: fails.append(f'#10 {n}: line numbers same as text')
    if 'LINE_NUMBER_ON_CARET_ROW_COLOR' not in cols: fails.append(f'#10 {n}: no active line number')
    # 12 selection stronger than stripe/hover
    for a in ('Tree.selectionBackground','*.selectionBackground'):
        if contrast(t[a],ins) <= contrast(t['Table.stripeColor'],bg): fails.append(f'#12 {n}: {a} weaker than stripe')
        if contrast(t[a],ins) <= contrast(t['*.hoverBackground'],ins): fails.append(f'#12 {n}: {a} weaker than hover')
    # 13 completion match is accent
    if t['CompletionPopup.matchForeground']==t['*.disabledForeground']: fails.append(f'#13 {n}: match fg dim')
    # 14 states visible
    for a,b,m in [('CheckBoxMenuItem.selectionBackground','CheckBoxMenuItem.background',1.1),('WelcomeScreen.Projects.actions.selectionBackground','WelcomeScreen.Projects.actions.background',1.1),('ComboBox.ArrowButton.disabledIconColor','ComboBox.ArrowButton.background',1.5)]:
        chk(14,f'{a} vs {b}',n,t[a],t[b],m)
    # 5 colorblind: no red/green hues in status colors
    if 'colorblind' in n:
        import colorsys
        for k in ('Label.errorForeground','Component.errorFocusColor','Debugger.Variables.exceptionForeground','SearchField.errorForeground','ValidationTooltip.errorBorderColor','UnattendedHostStatus.dangerBackground','ProgressBar.failedColor'):
            rgb=[int(t[k][i:i+2],16)/255 for i in (1,3,5)]; h=colorsys.rgb_to_hsv(*rgb)[0]*360
            if h<20 or h>340 or 90<h<160: fails.append(f'#5 {n}: {k} hue {h:.0f}')
        for k in ('ERRORS_ATTRIBUTES','DIFF_INSERTED','DIFF_DELETED'):
            v=at[k]; c=v.get('EFFECT_COLOR') or v.get('ERROR_STRIPE_COLOR'); rgb=[int(c[i:i+2],16)/255 for i in (0,2,4)] if not c.startswith('#') else [int(c[i:i+2],16)/255 for i in (1,3,5)]
            h=colorsys.rgb_to_hsv(*rgb)[0]*360
            if h<20 or h>340 or 90<h<160: fails.append(f'#5 {n}: {k} hue {h:.0f}')
# no JetBrains palette leaks: every colour key the Islands chain supplies must be set by our theme
import islands_map, re as _re
for dk in (True, False):
    need = set()
    for k,(v,cols) in islands_map.chain(dk).items():
        if isinstance(v,str) and (islands_map.HEX.fullmatch(v) or v in cols or islands_map.INSETS_COLOR.fullmatch(v) or v=='transparent'):
            need.add(k.lower())
    for n in T:
        if ('dark' in n)!=dk: continue
        have={k.lower() for k in T[n]}
        miss=sorted(need-have)
        if miss: fails.append(f'#L {n}: {len(miss)} inherited JetBrains colour keys not overridden, e.g. {miss[:5]}')
# no hardcoded JetBrains defaults from IDE code: every such key is set or covered by a "*" suffix key
code = islands_map.code_defaults()
for n in T:
    have = {k.lower() for k in T[n]}; stars = [k[2:] for k in T[n] if k.startswith('*.')]
    miss = sorted(k for k in code if k.lower() not in have and not any(k.endswith(s) for s in stars))
    if miss: fails.append(f'#C {n}: {len(miss)} colour keys fall back to a hardcoded JetBrains default, e.g. {miss[:5]}')
# secondary text and chips (AA), faded editor text (3:1)
for n,t in T.items():
    cols,at=S[n]; ebg='#'+at['TEXT']['BACKGROUND']
    for a,b in [('Label.infoForeground','*.background'),('Label.infoForeground','MainWindow.background'),
                ('Label.infoForeground','Popup.background'),('List.Tag.foreground','List.Tag.background'),
                ('Plugins.tagForeground','Plugins.tagBackground'),('WelcomeScreen.footerForeground','WelcomeScreen.footerBackground'),
                ('Notification.MoreButton.foreground','Notification.MoreButton.background'),
                ('GotItTooltip.shortcutForeground','GotItTooltip.shortcutBackground'),
                ('Bookmark.Mnemonic.iconForeground','Bookmark.Mnemonic.iconBackground'),
                ('ToolWindow.Button.selectedForeground','ToolWindow.Button.selectedBackground'),
                ('SearchEverywhere.Tab.selectedForeground','SearchEverywhere.Tab.selectedBackground'),
                ('CheckBoxMenuItem.selectionForeground','CheckBoxMenuItem.selectionBackground'),
                ('MenuItem.selectionForeground','MenuItem.selectionBackground'),
                ('DragAndDrop.areaForeground','DragAndDrop.areaBackground'),
                ('VersionControl.Merge.Badge.infoForeground','VersionControl.Merge.Badge.infoBackground'),
                ('VersionControl.Merge.Badge.modifiedItemForeground','VersionControl.Merge.Badge.modifiedItemBackground')]+\
               [(f'Badge.{c}SecondaryForeground',f'Badge.{c}SecondaryBackground') for c in ('blue','green','gray','purple')]:
        star=lambda k: t.get(k) or next((v for s_,v in sorted(((s_[2:],v) for s_,v in t.items() if s_.startswith('*.')),key=lambda x:-len(x[0])) if k.endswith(s_)),None)
        f,bg=star(a),star(b)
        if not f or not bg: fails.append(f'#15 {n}: {a if not f else b} not set'); continue
        base=t['GotItTooltip.background'] if a.startswith('GotIt') else t['MainWindow.background'] if a.startswith('ToolWindow.Button') else t['*.background']
        chk(15,f'{a} on {b}',n,f,over(bg,base),4.5)
    for an in ('NOT_USED_ELEMENT_ATTRIBUTES','BREADCRUMBS_INACTIVE','LOG_EXPIRED_ENTRY'):
        chk(16,f'{an} on editor',n,'#'+at[an]['FOREGROUND'],ebg,3.0)
print('\n'.join(fails) if fails else 'ALL CHECKS PASS'); print(len(fails),'failures')
