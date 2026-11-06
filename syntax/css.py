"""CSS family: CSS, SCSS/Sass, Less, PostCSS, HTML, XML, XPath, Haml, Slim.

CSS, SCSS, Less, HTML and XML are tokenised with VS Code's bundled grammars. IntelliJ's Sass keys
(SASS_*) serve both indented Sass and SCSS; VS Code has no indented-Sass grammar, so the SCSS
grammar stands in. PostCSS has no VS Code grammar either; its keys alias the CSS ones (PostCSS files
are opened as CSS in VS Code). XPath is not tokenised by VS Code's XSL grammar: it stays the
attribute string. Haml and Slim have no grammar installed: explicit stacks
modelled on the de-facto extensions (vscode-haml `text.haml`, vscode-slim `text.slim`).
"""

SAMPLES = {
    'css': ('source.css', r'''@import url("theme.css");
/* Block comment */
@font-face {
  font-family: "Droid Sans";
  src: url(DroidSans.ttf);
  unicode-range: U+000-5FF, U+1e00-1fff;
}
@media screen and (max-width: 600px) {
  #header > div.nav-item:hover, ul li ~ p, input[type="radio"]::before {
    color: #ff0000 !important;
    margin: 0 auto;
    width: calc(100% - 2em);
  }
}
.btn {
  display: block;
  &:hover { opacity: 0.5; }
}
.card { color: var(--main-color); }
'''),
    'scss': ('source.css.scss', r'''@use "sass:math";
@import 'variables';
// Silent comment
/* Loud comment */
$padding: 1% !default;
$grid-width: 10px !global;
@mixin with-shadow($color: black) {
  box-shadow: $color, 1px, 2px, 3px;
}
@function grid-width($n) {
  @return $n * $grid-width + ($n - 1) * 10px;
}
#main a.button:visited span[lang="en"] {
  @extend .shadow !optional;
  @include with-shadow(blue);
  color: #00ddcc !important;
  display: block;
  width: math.div(100%, 3);
  background: url(img/bg.png);
  font-family: "Droid Sans", sans-serif;
  &:hover { width: 97%; }
  unicode-range: U+000-5FF;
}
@for $i from 1 through 3 {
  .item-#{$i} { width: 2em * $i; }
}
@media screen and (min-width: 1px) { }
'''),
    'less': ('source.css.less', r'''@import 'mixins'; // external mixins
@the-border: 1px;
@base-color: #111;
#header {
  color: @base-color * 3;
  &:after {
    border-right: @the-border * 2;
  }
}
.colored(@c) when (iscolor(@c)) {
  color: (@base-color + #111) * 1.5;
  margin: 0 auto;
}
@var: `"hello".toUpperCase() + '!'`;
@font-face {
  font-family: "Droid Sans";
  src: url(DroidSans.ttf);
  unicode-range: U+000-5FF, U+1e00-1fff;
}
div.class > p, p ~ ul, input[type="radio"]:hover {
  color: green !important;
  width: percentage(0.5);
}
@media screen and (min-width: 1px) { }
'''),
    'html': ('text.html.basic', r'''<!DOCTYPE html>
<!-- Sample comment -->
<html lang="en">
<body>
<h1 class="title">Hello</h1>
<p>What is it? &#x00B7; &Alpha; &amp;</p>
<custom-tag data-id="1">hello</custom-tag>
</body>
</html>
'''),
    'xml': ('text.xml', r'''<?xml version="1.0" encoding="ISO-8859-1"?>
<!-- Some xml example -->
<index version="1.0" xmlns:pf="http://test">
   <name>Main Index</name>
   <indexitem text="rename" target="refactoring.rename"/>
   <someTextWithEntityRefs>&amp; &#x00B7;</someTextWithEntityRefs>
   <pf:foo pf:bar="bar"/>
</index>
'''),
    'xsl': ('text.xml.xsl', r'''<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:value-of select="//prefix:*[ext:name() = 'changes']/element[(position() mod 2) = $pos + 1]/parent::*"/>
</xsl:stylesheet>
'''),
}

MAP = {
    # ---- CSS (CssHighlighter, external names CSS.*) ----
    'CSS.AMPERSAND':        ('css', '&:hover'),
    'CSS.ATTRIBUTE_NAME':   ('css', 'type='),
    'CSS.BAD_CHARACTER':    'source.css invalid.illegal.bad-identifier.css',
    'CSS.BRACES':           ('css', '{'),
    'CSS.BRACKETS':         ('css', '[type'),
    'CSS.CLASS_NAME':       ('css', 'nav-item'),
    'CSS.COLON':            ('css', ': "Droid'),
    'CSS.COLOR':            ('css', 'ff0000'),
    'CSS.COMMA':            ('css', ', U+1e00'),
    'CSS.COMMENT':          ('css', 'Block comment'),
    'CSS.DOT':              ('css', '.nav-item'),
    'CSS.FUNCTION':         ('css', 'calc'),
    'CSS.HASH':             ('css', 'header'),
    'CSS.IDENT':            ('css', '--main-color'),
    'CSS.IMPORTANT':        ('css', '!important'),
    'CSS.KEYWORD':          ('css', 'media'),
    'CSS.NUMBER':           ('css', '600'),
    'CSS.OPERATORS':        ('css', '> div'),
    'CSS.PARENTHESES':      ('css', '(100%'),
    'CSS.PROPERTY_NAME':    ('css', 'color'),
    'CSS.PROPERTY_VALUE':   ('css', 'block'),
    'CSS.PSEUDO':           ('css', 'hover'),
    'CSS.SEMICOLON':        ('css', ';\n  src'),
    'CSS.STRING':           ('css', 'Droid Sans'),
    'CSS.TAG_NAME':         ('css', 'div.'),
    'CSS.UNICODE.RANGE':    ('css', 'U+000'),
    'CSS.UNIT':             ('css', 'px'),
    'CSS.URL':              ('css', 'DroidSans.ttf'),

    # ---- PostCSS: no VS Code grammar; PostCSS files are CSS there ----
    'POST_CSS_AMPERSAND':       ('=', 'CSS.AMPERSAND'),
    'POST_CSS_ATTRIBUTE_NAME':  ('=', 'CSS.ATTRIBUTE_NAME'),
    'POST_CSS_BAD_CHARACTER':   ('=', 'CSS.BAD_CHARACTER'),
    'POST_CSS_BRACES':          ('=', 'CSS.BRACES'),
    'POST_CSS_BRACKETS':        ('=', 'CSS.BRACKETS'),
    'POST_CSS_CLASS_NAME':      ('=', 'CSS.CLASS_NAME'),
    'POST_CSS_COLON':           ('=', 'CSS.COLON'),
    'POST_CSS_COLOR':           ('=', 'CSS.COLOR'),
    'POST_CSS_COMMA':           ('=', 'CSS.COMMA'),
    'POST_CSS_COMMENT':         ('=', 'CSS.COMMENT'),
    'POST_CSS_DOT':             ('=', 'CSS.DOT'),
    'POST_CSS_FUNCTION':        ('=', 'CSS.FUNCTION'),
    'POST_CSS_IDENT':           ('=', 'CSS.IDENT'),
    'POST_CSS_ID_SELECTOR':     ('=', 'CSS.HASH'),
    'POST_CSS_IMPORTANT':       ('=', 'CSS.IMPORTANT'),
    'POST_CSS_KEYWORD':         ('=', 'CSS.KEYWORD'),
    'POST_CSS_NUMBER':          ('=', 'CSS.NUMBER'),
    'POST_CSS_OPERATORS':       ('=', 'CSS.OPERATORS'),
    'POST_CSS_PARENTHESES':     ('=', 'CSS.PARENTHESES'),
    'POST_CSS_PROPERTY_NAME':   ('=', 'CSS.PROPERTY_NAME'),
    'POST_CSS_PROPERTY_VALUE':  ('=', 'CSS.PROPERTY_VALUE'),
    'POST_CSS_PSEUDO':          ('=', 'CSS.PSEUDO'),
    'POST_CSS_SEMICOLON':       ('=', 'CSS.SEMICOLON'),
    'POST_CSS_STRING':          ('=', 'CSS.STRING'),
    'POST_CSS_TAG_NAME':        ('=', 'CSS.TAG_NAME'),
    'POST_CSS_UNICODE_RANGE':   ('=', 'CSS.UNICODE.RANGE'),
    'POST_CSS_UNIT':            ('=', 'CSS.UNIT'),
    'POST_CSS_URL':             ('=', 'CSS.URL'),

    # ---- Sass / SCSS (SassScssHighlightingColors) ----
    'SASS_ATTRIBUTE_NAME':  ('scss', 'lang='),
    'SASS_BAD_CHARACTER':   'source.css.scss invalid.illegal.bad-identifier.scss',
    'SASS_BRACES':          ('scss', '{'),
    'SASS_BRACKETS':        ('scss', '[lang'),
    'SASS_CLASS_NAME':      ('scss', 'button'),
    'SASS_COLON':           ('scss', ': #00ddcc'),
    'SASS_COLOR':           ('scss', '00ddcc'),
    'SASS_COMMA':           ('scss', ', 3)'),
    'SASS_COMMENT':         ('scss', 'Silent comment'),
    'SASS_DEFAULT':         ('scss', '!default'),
    'SASS_DOT':             ('scss', '.button'),
    'SASS_EXTEND':          ('scss', 'extend'),
    'SASS_FUNCTION':        ('scss', 'div('),
    'SASS_GLOBAL':          ('scss', '!global'),
    'SASS_IDENTIFIER':      ('scss', 'screen'),
    'SASS_ID_SELECTOR':     ('scss', 'main'),
    'SASS_IMPORTANT':       ('scss', '!important'),
    'SASS_INTERPOLATION':   ('scss', '#{'),
    'SASS_KEYWORD':         ('scss', 'include'),
    'SASS_MIXIN':           ('scss', 'mixin with'),
    'SASS_NUMBER':          ('scss', '97'),
    'SASS_OPERATORS':       ('scss', '* $grid'),
    'SASS_OPTIONAL':        ('scss', '!optional'),
    'SASS_PARENTHESES':     ('scss', '($n - 1)'),
    'SASS_PARENT_SELECTOR': ('scss', '&:hover'),
    'SASS_PROPERTY_NAME':   ('scss', 'color: #00ddcc'),
    'SASS_PROPERTY_VALUE':  ('scss', 'block'),
    'SASS_PSEUDO':          ('scss', 'visited'),
    'SASS_SEMICOLON':       ('scss', ';\n$grid'),
    'SASS_STRING':          ('scss', 'Droid Sans'),
    'SASS_TAG_NAME':        ('scss', 'span'),
    'SASS_UNICODE_RANGE':   ('scss', '000-5FF'),
    'SASS_UNIT':            ('scss', 'px'),
    'SASS_URL':             ('scss', 'img/bg.png'),
    'SASS_VARIABLE':        ('scss', '$padding'),
    # legacy keys still set by the bundled Default/Darcula schemes
    'SASS_ATTRIBUTE':       ('=', 'SASS_PROPERTY_NAME'),
    'SASS_CONSTANT':        ('=', 'SASS_VARIABLE'),
    'SASS_DIRECTIVE':       ('=', 'SASS_KEYWORD'),
    'SASS_RULE':            ('=', 'SASS_TAG_NAME'),

    # ---- Less (LESSSyntaxHighlighter) ----
    'LESS_ATTRIBUTE_NAME':  ('less', 'type='),
    'LESS_BAD_CHARACTER':   'source.css.less invalid.illegal.bad-identifier.less',
    'LESS_BRACES':          ('less', '{'),
    'LESS_BRACKETS':        ('less', '[type'),
    'LESS_CLASS_NAME':      ('less', 'colored'),
    'LESS_COLON':           ('less', ': 1px'),
    'LESS_COLOR':           ('less', '111;'),
    'LESS_COMMA':           ('less', ', U+1e00'),
    'LESS_COMMENT':         ('less', 'external mixins'),
    'LESS_DOT':             ('less', '.colored'),
    'LESS_FUNCTION':        ('less', 'percentage'),
    'LESS_IDENT':           ('less', 'screen'),
    'LESS_ID_SELECTOR':     ('less', 'header'),
    'LESS_IMPORTANT':       ('less', 'important'),
    'LESS_INJECTED_CODE':   ('less', 'toUpperCase'),
    'LESS_JS_CODE_DELIM':   ('less', '`'),
    'LESS_KEYWORD':         ('less', 'when'),
    'LESS_NUMBER':          ('less', '1.5'),
    'LESS_OPERATORS':       ('less', '* 3'),
    'LESS_PARENTHESES':     ('less', '(@base-color +'),
    'LESS_PARENT_SELECTOR': ('less', '&:after'),
    'LESS_PROPERTY_NAME':   ('less', 'border-right'),
    'LESS_PROPERTY_VALUE':  ('less', 'auto'),
    'LESS_PSEUDO':          ('less', 'hover'),
    'LESS_SEMICOLON':       ('less', ';\n@base'),
    'LESS_STRING':          ('less', "mixins'"),
    'LESS_TAG_NAME':        ('less', 'div.'),
    'LESS_UNICODE_RANGE':   ('less', 'U+000'),
    'LESS_UNIT':            ('less', 'px'),
    'LESS_URL':             ('less', 'DroidSans.ttf'),
    'LESS_VARIABLE':        ('less', 'base-color'),

    # ---- HTML (XmlHighlighterColors) ----
    'HTML_ATTRIBUTE_NAME':   ('html', 'class='),
    'HTML_ATTRIBUTE_VALUE':  ('html', 'title"'),
    'HTML_CODE':             ('html', 'Hello'),
    'HTML_COMMENT':          ('html', 'Sample comment'),
    'HTML_CUSTOM_TAG_NAME':  ('html', 'custom-tag'),
    'HTML_ENTITY_REFERENCE': ('html', 'amp;'),
    'HTML_TAG':              ('html', '<h1'),
    'HTML_TAG_NAME':         ('html', 'h1'),

    # ---- XML (XmlHighlighterColors) ----
    'XML_ATTRIBUTE_NAME':    ('xml', 'text='),
    'XML_ATTRIBUTE_VALUE':   ('xml', 'rename"'),
    'XML_COMMENT':           ('xml', 'Some xml'),
    'XML_CUSTOM_TAG_NAME':   ('=', 'XML_TAG_NAME'),
    'XML_ENTITY_REFERENCE':  ('xml', 'amp;'),
    'XML_NS_PREFIX':         ('xml', 'pf:foo'),
    'XML_PROLOGUE':          ('xml', '<?xml'),
    'XML_TAG':               ('xml', '<name>'),
    'XML_TAG_DATA':          ('xml', 'Main Index'),
    'XML_TAG_NAME':          ('xml', 'indexitem'),

    # ---- XPath: VS Code's XSL grammar leaves XPath expressions as the attribute string ----
    'XPATH.BRACKET':         ('xsl', "[ext:"),
    'XPATH.FUNCTION':        ('xsl', "position()"),
    'XPATH.KEYWORD':         ('xsl', " mod "),
    'XPATH.NUMBER':          ('xsl', "2)"),
    'XPATH.OPERATION_SIGN':  ('xsl', "+ 1"),
    'XPATH.PARENTH':         ('xsl', "(position"),
    'XPATH.STRING':          ('xsl', "'changes'"),
    'XPATH.XPATH_NAME':      ('xsl', "element["),
    'XPATH.XPATH_PREFIX':    ('xsl', "prefix:"),
    'XPATH.XPATH_TEXT':      ('xsl', "//prefix"),
    'XPATH.XPATH_VARIABLE':  ('xsl', "$pos"),

    # ---- Haml (no VS Code grammar installed; explicit, after vscode-haml text.haml) ----
    'HAML_CLASS':               'text.haml meta.tag.haml entity.other.attribute-name.class.haml',
    'HAML_COMMENT':             'text.haml comment.line.slash.haml',
    'HAML_FILTER':              'text.haml meta.embedded.filter.haml entity.name.function.filter.haml',
    'HAML_FILTER_CONTENT':      'text.haml meta.embedded.filter.haml',
    'HAML_ID':                  'text.haml meta.tag.haml entity.other.attribute-name.id.haml',
    'HAML_LINE_CONTINUATION':   'text.haml meta.line.ruby.haml punctuation.separator.continuation.haml',
    'HAML_PARENTHS':            'text.haml meta.tag.haml meta.section.attributes.haml punctuation.section.attributes.begin.haml',
    'HAML_RUBY_CODE':           'text.haml meta.line.ruby.haml source.ruby.embedded.haml',
    'HAML_RUBY_START':          'text.haml meta.line.ruby.haml punctuation.section.embedded.ruby',
    'HAML_STRING':              'text.haml meta.tag.haml meta.section.attributes.haml source.ruby.embedded.haml string.quoted.single.ruby',
    'HAML_STRING_INTERPOLATED': 'text.haml meta.tag.haml meta.section.attributes.haml source.ruby.embedded.haml string.quoted.double.interpolated.ruby',
    'HAML_TAG':                 'text.haml meta.tag.haml punctuation.definition.tag.haml',
    'HAML_TAG_NAME':            'text.haml meta.tag.haml entity.name.tag.haml',
    'HAML_TEXT':                'text.haml',
    'HAML_WS_REMOVAL':          'text.haml meta.tag.haml punctuation.definition.tag.haml',
    'HAML_XHTML':               'text.haml meta.prolog.haml punctuation.definition.prolog.haml',

    # ---- Slim (no VS Code grammar installed; explicit, after vscode-slim text.slim) ----
    'SLIM_BAD_CHARACTER':       'text.slim invalid.illegal.bad-character.slim',
    'SLIM_CALL':                'text.slim meta.line.ruby.slim punctuation.section.embedded.ruby',
    'SLIM_CLASS':               'text.slim meta.tag.slim entity.other.attribute-name.class.slim',
    'SLIM_COMMENT':             'text.slim comment.line.slash.slim',
    'SLIM_DOCTYPE_KWD':         'text.slim meta.prolog.slim keyword.other.doctype.slim',
    'SLIM_FILTER':              'text.slim constant.language.name.javascript.filter.slim',
    'SLIM_FILTER_CONTENT':      'text.slim source.js.filter.slim',
    'SLIM_ID':                  'text.slim meta.tag.slim entity.other.attribute-name.id.slim',
    'SLIM_INTERPOLATION':       'text.slim meta.embedded.line.ruby punctuation.section.embedded.begin.ruby',
    'SLIM_PARENTHS':            'text.slim meta.tag.slim meta.section.attributes.slim punctuation.section.attributes.begin.slim',
    'SLIM_RUBY_CODE':           'text.slim meta.line.ruby.slim source.ruby.embedded.slim',
    'SLIM_STATIC_CONTENT':      'text.slim',
    'SLIM_STRING_INTERPOLATED': 'text.slim meta.tag.slim source.ruby.embedded.slim string.quoted.double.interpolated.ruby',
    'SLIM_TAG':                 'text.slim meta.tag.slim entity.name.tag.slim',
    'SLIM_TAG_ATTR_KEY':        'text.slim meta.tag.slim entity.other.attribute-name.slim',
    'SLIM_TAG_START':           'text.slim meta.tag.slim punctuation.definition.tag.slim',
}

NOTES = {
    'CSS.BAD_CHARACTER': 'explicit: no sample produces a bad character; invalid.illegal like VS Code errors',
    'SASS_BAD_CHARACTER': 'explicit: invalid.illegal',
    'LESS_BAD_CHARACTER': 'explicit: invalid.illegal',
    'CSS.IDENT': 'CssHighlighterLexer leaves idents the lexer cannot classify: var(--x) arguments (most common; '
                 'variable.argument in VS Code), media-query `and`, :lang() args, @keyframes names. Keyword values are '
                 'CSS.PROPERTY_VALUE, selectors are annotated as tag/class',
    'CSS.PROPERTY_VALUE': 'keyword values (auto, block) are support.constant.property-value in VS Code; unknown idents are unscoped',
    'SASS_IDENTIFIER': 'residual CSS_IDENT (selectors are annotated as tag/class/attr): media types, :lang() args, var(--x); '
                       'chose the media type',
    'LESS_IDENT': 'residual CSS_IDENT (selectors are annotated as tag/class/attr): media types, :lang() args; chose the media type',
    'SASS_MIXIN': 'SCSS lexes `@mixin` as SCSS_MIXIN (the name is a FUNCTION token); in indented Sass it is the `=name` name',
    'SASS_FUNCTION': 'CSS_FUNCTION_TOKEN: function calls (support.function) and @mixin/@include names (entity.name.function); chose calls',
    'LESS_FUNCTION': 'CSS_FUNCTION_TOKEN: function calls (support.function) and .mixin( definitions; chose calls',
    'LESS_KEYWORD': '@import etc. are CSS.KEYWORD in Less; LESS_KEYWORD paints `when` / `and` guards',
    'CSS.DOT': 'the dot of a class selector is part of entity.other.attribute-name.class in VS Code',
    'CSS.HASH': 'CSS.HASH is the ID-selector key of plain CSS',
    'SASS_UNICODE_RANGE': 'SCSS grammar splits U+000-5FF into unscoped U, + operator and numeric 000; chose the numeric part',
    'SASS_GLOBAL': 'VS Code SCSS leaves !global unscoped (default foreground)',
    'SASS_ATTRIBUTE': 'legacy key (old Sass plugin), alias of property name',
    'SASS_CONSTANT': 'legacy key, alias of variable',
    'SASS_DIRECTIVE': 'legacy key, alias of @-rule keyword',
    'SASS_RULE': 'legacy key, alias of selector tag name',
    'LESS_INJECTED_CODE': 'backtick JS is string.unquoted.less in VS Code',
    'LESS_JS_CODE_DELIM': 'backtick is string.unquoted.less in VS Code',
    'HTML_TAG': 'whole tag incl. brackets: mapped to the bracket punctuation.definition.tag',
    'XML_TAG': 'whole tag incl. brackets: mapped to the bracket punctuation.definition.tag',
    'XML_PROLOGUE': '<?xml ... ?> mapped to its <? punctuation.definition.tag',
    'XML_CUSTOM_TAG_NAME': 'VS Code does not distinguish custom tags; alias of XML_TAG_NAME',
    'HTML_CODE': 'plain HTML text (default foreground)',
    'XML_TAG_DATA': 'plain text (default foreground)',
}
for _k in MAP:
    if _k.startswith(('HAML_', 'SLIM_')):
        NOTES.setdefault(_k, 'explicit stack: no VS Code grammar installed')
    elif _k.startswith('XPATH.'):
        NOTES.setdefault(_k, 'VS Code (XSL grammar) shows XPath in select/test attributes as a plain attribute string')
    elif False:
        NOTES.setdefault(_k, 'explicit stack: no VS Code grammar installed')
    elif _k.startswith('POST_CSS_'):
        NOTES.setdefault(_k, 'PostCSS has no VS Code grammar (opened as CSS): alias of the CSS key')
