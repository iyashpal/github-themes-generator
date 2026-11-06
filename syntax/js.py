"""JavaScript / TypeScript / JSX / JSON / JSONPath / CoffeeScript / Pug / GraphQL / Vue / Angular.

External key names: JS keys are "JS." + JavaScriptHighlightDescriptor name (BADCHARACTER, PARENTHS,
PRIMITIVE.TYPE, EXPORTED.* are the renamed ones); TS keys come from TypeScriptHighlighter /
TypeScriptHighlightDescriptor; NG.* from Angular2Html/Angular2HighlighterColors. The JS_*/TS_*/NG_*/
JSON_* names in the family list are Java field names, not keys.

JS/TS identifiers use VS Code's semantic-token fallback scopes (built-in TS server), not TextMate.
"""

SAMPLES = {
    'js': ('source.js', r'''import { readFile } from "fs";

/**
 * @description Validator
 * @param {string?} value - parameter description
 */
function globalFunction({ options = {} }) {
  const { minLength } = options;
  const localFunction = (value) => {
    let isValid = value?.length >= minLength ?? 3; // line comment
    /* Block comment */
    isValid = isValid && (/^\d.[A-F]+$/i).test(value);
    return { isValid };
  };
}

@defineElement("download-button")
class DownloadButton extends HTMLButtonElement {
  static STATIC_FIELD = `<span>${globalVariable}</span>`;

  static get observedAttributes() {
    return ['data-test', 2];
  }

  #field = { prop: 1 };

  method() {
    this.click();
    label:
      while (true) {
        break label;
      }
  }
}

const globalVariable = "chars\n\u11";
'''),
    'ts': ('source.ts', r'''import { readFile } from "fs";

interface ValidatorOptions {
  minLength?: number;
}

type ValidatorDescriptor = {
  options: ValidatorOptions,
};

enum Color { Red, Green }

namespace Shapes {
  export const unit = 1;
}

/**
 * @description Validator
 * @param {string?} value - parameter description
 */
function globalFunction({ options = {} }: ValidatorDescriptor) {
  const { minLength } = options;
  const localFunction = (value: string) => {
    let isValid = value?.length >= minLength ?? 3; // line comment
    /* Block comment */
    isValid = isValid && (/^\d.[A-F]+$/i).test(value);
    return { isValid };
  };
}

@defineElement("download-button")
class DownloadButton<T extends ButtonProps> extends HTMLButtonElement {
  static STATIC_FIELD = `<span>${globalVariable}</span>`;

  static get observedAttributes(): string[] {
    return ['data-test', 2];
  }

  public method(props: T) {
    this.click();
    label:
      while (true) {
        break label;
      }
  }
}

const globalVariable = "chars\n\u11";
'''),
    'tsx': ('source.tsx', r'''export function App() {
  return <JsxClientComponent title="x" />;
}
'''),
    'json': ('source.json.comments', r'''{
  // Line comments are not included in standard but nonetheless allowed.
  /* As well as block comments. */
  "the only keywords are": [true, false, null],
  "strings with": {
    "no escapes": "pseudopolinomiality",
    "valid escapes": "C-style\r\n and unicode!",
    "illegal escapes": "\0377\x"
  },
  "some numbers": [
    42,
    -0.0e-0,
    6.626e-34
  ]
}
'''),
    'coffee': ('source.coffee', r'''# line comment
###
block comment
###
class Animal extends Base
  constructor: (@name) ->

  move: (meters = 5) =>
    alert @name + " moved #{meters}m.\n"
    obj = {key: 1, other: 2}
    obj?.prop
    list = [1..10]
    rest = (args...) -> args
    re = /ab+c/gi
    hre = ///ab+c///
    alert list
    doc = """
      heredoc
    """
    js = `foo`
    s = 'single'
    Animal::move; yes; this

square = (x) -> x * x
document.title
'''),
    'pug': ('text.pug', r'''doctype html
include ./includes/head.pug
html
  body
    :markdown-it
      # Title
    - var items = [1, 2]
    if items.length
      each item in items
        p= item
'''),
    'graphql': ('source.graphql', r'''query GetUser($id: ID!) {
  user(id: $id, limit: 10, name: "x") {
    name
  }
}
'''),
    'vue': ('vue', r'''<template>
  <div>{{ message }}</div>
</template>
'''),
    'css': ('source.css', r''':host ::ng-deep .item {
  color: red;
}
'''),
}

# --- JavaScript --------------------------------------------------------------------------------
_JS = {
    'JS.KEYWORD':                                   ('js', 'function', 1),
    'JS.STRING':                                    ('js', 'download-button', 1),
    'JS.NUMBER':                                    ('js', '3;', 1),
    'JS.REGEXP':                                    ('js', '/^', 1),
    'JS.LINE_COMMENT':                              ('js', '// line', 1),
    'JS.BLOCK_COMMENT':                             ('js', '/* Block', 1),
    'JS.DOC_COMMENT':                               ('js', 'Validator', 1),
    'JS.DOC_TAG':                                   ('js', '@param', 1),
    'JS.DOC_TAG_NAMEPATH':                          ('js', 'value - ', 1),
    'JS.DOC_TYPE':                                  ('js', 'string?', 1),
    'JS.OPERATION_SIGN':                            ('js', '>=', 1),
    'JS.PARENTHS':                                  ('js', '({ options', 1),
    'JS.BRACKETS':                                  ('js', "['data", 1),
    'JS.BRACES':                                    ('js', '{ isValid }', 1),
    'JS.COMMA':                                     ('js', ", 2]", 1),
    'JS.DOT':                                       ('js', '.test', 1),
    'JS.SEMICOLON':                                 ('js', ';\n  const localFunction', 1),
    'JS.VALID_STRING_ESCAPE':                       ('js', r'\n\u', 1),
    'JS.INVALID_STRING_ESCAPE':                     ('js', r'\u11', 1),
    'JS.TEMPLATE_LITERAL_PLACEHOLDER_DELIMITERS':   ('js', '${', 1),
    'JS.FUNCTION_ARROW':                            ('js', '=>', 1),
    'JS.LABEL':                                     ('js', 'label:', 1),
    'JS.DECORATOR':                                 ('js', 'defineElement', 1),
    'JS.BADCHARACTER':                              'source.js invalid.illegal.bad-character.js',
    # semantic tokens (TypeScript server) -> VS Code fallback scopes
    'JS.LOCAL_VARIABLE':                            'source.js variable.other.constant',
    'JS.GLOBAL_VARIABLE':                           'source.js variable.other.constant',
    'JS.EXPORTED.VARIABLE':                         'source.js variable.other.constant',
    'JS.PARAMETER':                                 'source.js variable.parameter',
    'JS.INSTANCE_MEMBER_VARIABLE':                  'source.js variable.other.property',
    'JS.STATIC_MEMBER_VARIABLE':                    'source.js variable.other.property',
    'JS.INSTANCE_MEMBER_FUNCTION':                  'source.js entity.name.function.member',
    'JS.STATIC_MEMBER_FUNCTION':                    'source.js entity.name.function.member',
    'JS.GLOBAL_FUNCTION':                           'source.js entity.name.function',
    'JS.LOCAL_FUNCTION':                            'source.js entity.name.function',
    'JS.EXPORTED.FUNCTION':                         'source.js entity.name.function',
    'JS.CLASS':                                     'source.js entity.name.type.class',
    'JS.EXPORTED.CLASS':                            'source.js entity.name.type.class',
    'JS.INTERFACE':                                 'source.js entity.name.type.interface',
    'JS.TYPE_ALIAS':                                'source.js entity.name.type',
    'JS.MODULE_NAME':                               'source.js entity.name.namespace',
    'JS.PRIMITIVE.TYPE':                            ('=', 'TS.PRIMITIVE.TYPES'),
    'JS.JSX_CLIENT_COMPONENT':                      ('tsx', 'JsxClientComponent', 1),
}

# --- TypeScript --------------------------------------------------------------------------------
_TS = {
    'TS.KEYWORD':                                   ('ts', 'function', 1),
    'TS.STRING':                                    ('ts', 'download-button', 1),
    'TS.NUMBER':                                    ('ts', '3;', 1),
    'TS.REGEXP':                                    ('ts', '/^', 1),
    'TS.LINE_COMMENT':                              ('ts', '// line', 1),
    'TS.BLOCK_COMMENT':                             ('ts', '/* Block', 1),
    'TS.DOC_COMMENT':                               ('ts', 'Validator\n', 1),
    'TS.DOC_TAG':                                   ('ts', '@param', 1),
    'TS.DOC_TAG_NAMEPATH':                          ('ts', 'value - ', 1),
    'TS.DOC_TYPE':                                  ('ts', 'string?', 1),
    'TS.OPERATION_SIGN':                            ('ts', '>=', 1),
    'TS.PARENTHS':                                  ('ts', '({ options', 1),
    'TS.BRACKETS':                                  ('ts', "['data", 1),
    'TS.BRACES':                                    ('ts', '{ isValid }', 1),
    'TS.COMMA':                                     ('ts', ", 2]", 1),
    'TS.DOT':                                       ('ts', '.test', 1),
    'TS.SEMICOLON':                                 ('ts', ';\n  const localFunction', 1),
    'TS.VALID_STRING_ESCAPE':                       ('ts', r'\n\u', 1),
    'TS.INVALID_STRING_ESCAPE':                     ('ts', r'\u11', 1),
    'TS.TEMPLATE_LITERAL_PLACEHOLDER_DELIMITERS':   ('ts', '${', 1),
    'TS.FUNCTION_ARROW':                            ('ts', '=>', 1),
    'TS.LABEL':                                     ('ts', 'label:', 1),
    'TS.DECORATOR':                                 ('ts', 'defineElement', 1),
    'TS.PRIMITIVE.TYPES':                           ('ts', 'number', 1),
    'TS.BADCHARACTER':                              'source.ts invalid.illegal.bad-character.ts',
    # semantic tokens (TypeScript server) -> VS Code fallback scopes
    'TS.LOCAL_VARIABLE':                            'source.ts variable.other.constant',
    'TS.GLOBAL_VARIABLE':                           'source.ts variable.other.constant',
    'TS.EXPORTED_VARIABLE':                         'source.ts variable.other.constant',
    'TS.PARAMETER':                                 'source.ts variable.parameter',
    'TS.TYPE_GUARD':                                'source.ts variable.parameter',
    'TS.INSTANCE_MEMBER_VARIABLE':                  'source.ts variable.other.property',
    'TS.STATIC_MEMBER_VARIABLE':                    'source.ts variable.other.property',
    'TS.INSTANCE_MEMBER_FUNCTION':                  'source.ts entity.name.function.member',
    'TS.STATIC_MEMBER_FUNCTION':                    'source.ts entity.name.function.member',
    'TS.GLOBAL_FUNCTION':                           'source.ts entity.name.function',
    'TS.LOCAL_FUNCTION':                            'source.ts entity.name.function',
    'TS.EXPORTED_FUNCTION':                         'source.ts entity.name.function',
    'TS.CLASS':                                     'source.ts entity.name.type.class',
    'TS.EXPORTED_CLASS':                            'source.ts entity.name.type.class',
    'TS.INTERFACE':                                 'source.ts entity.name.type.interface',
    'TS.TYPE.ALIAS':                                'source.ts entity.name.type',
    'TS.TYPE_PARAMETER':                            'source.ts entity.name.type.parameter',
    'TS.ENUM':                                      'source.ts entity.name.type.enum',
    'TS.ENUM_MEMBER':                               'source.ts variable.other.enummember',
    'TS.MODULE_NAME':                               'source.ts entity.name.namespace',
}

# --- JSON / JSONPath ---------------------------------------------------------------------------
_JSON = {
    'JSON.PROPERTY_KEY':        ('json', 'the only', 1),
    'JSON.STRING':              ('json', 'pseudo', 1),
    'JSON.NUMBER':              ('json', '42', 1),
    'JSON.KEYWORD':             ('json', 'true', 1),
    'JSON.BRACES':              ('json', '{', 1),
    'JSON.BRACKETS':            ('json', '[', 1),
    'JSON.COLON':               ('json', ': [true', 1),
    'JSON.COMMA':               ('json', ', false', 1),
    'JSON.LINE_COMMENT':        ('json', '// Line', 1),
    'JSON.BLOCK_COMMENT':       ('json', '/* As', 1),
    'JSON.VALID_ESCAPE':        ('json', r'\r', 1),
    'JSON.INVALID_ESCAPE':      ('json', r'\0', 1),
    'JSON.IDENTIFIER':          ('=', 'JSON.PROPERTY_KEY'),
    'JSON.PARAMETER':           ('=', 'DEFAULT_PARAMETER'),
}

_JSONPATH = {
    'JSONPATH.CONTEXT':         'source.jsonpath variable.language.context.jsonpath',
    'JSONPATH.IDENTIFIER':      'source.jsonpath variable.other.property.jsonpath',
    'JSONPATH.FUNCTION':        'source.jsonpath meta.function-call.jsonpath entity.name.function.jsonpath',
    'JSONPATH.KEYWORD':         'source.jsonpath keyword.control.jsonpath',
    'JSONPATH.BOOLEAN':         'source.jsonpath constant.language.boolean.jsonpath',
    'JSONPATH.NUMBER':          'source.jsonpath constant.numeric.jsonpath',
    'JSONPATH.STRING':          'source.jsonpath string.quoted.single.jsonpath',
    'JSONPATH.OPERATIONS':      'source.jsonpath keyword.operator.jsonpath',
    'JSONPATH.BRACES':          'source.jsonpath punctuation.definition.dictionary.jsonpath',
    'JSONPATH.BRACKETS':        'source.jsonpath punctuation.definition.brackets.jsonpath',
    'JSONPATH.PARENTHESES':     'source.jsonpath punctuation.definition.parameters.jsonpath',
    'JSONPATH.COLON':           'source.jsonpath punctuation.separator.slice.jsonpath',
    'JSONPATH.COMMA':           'source.jsonpath punctuation.separator.comma.jsonpath',
    'JSONPATH.DOT':             'source.jsonpath punctuation.accessor.jsonpath',
}

# --- CoffeeScript ------------------------------------------------------------------------------
_COFFEE = {
    'COFFEESCRIPT.LINE_COMMENT':                ('coffee', '# line', 1),
    'COFFEESCRIPT.BLOCK_COMMENT':               ('coffee', 'block comment', 1),
    'COFFEESCRIPT.KEYWORD':                     ('coffee', 'extends', 1),
    'COFFEESCRIPT.CLASS_NAME':                  ('coffee', 'Animal', 1),
    'COFFEESCRIPT.FUNCTION_NAME':               ('coffee', 'square', 1),
    'COFFEESCRIPT.FUNCTION':                    ('coffee', '->', 1),
    'COFFEESCRIPT.FUNCTION_BINDING':            ('coffee', '=>', 1),
    'COFFEESCRIPT.THIS':                        ('coffee', '@name +', 1),
    'COFFEESCRIPT.NUMBER':                      ('coffee', '5', 1),
    'COFFEESCRIPT.BOOLEAN':                     ('coffee', 'yes', 1),
    'COFFEESCRIPT.STRING':                      ('coffee', ' moved', 1),
    'COFFEESCRIPT.STRING_LITERAL':              ('coffee', 'single', 1),
    'COFFEESCRIPT.ESCAPE_SEQUENCE':             ('coffee', r'\n"', 1),
    'COFFEESCRIPT.EXPRESSIONS_SUBSTITUTION_MARK': ('coffee', '#{', 1),
    'COFFEESCRIPT.HEREDOC_ID':                  ('coffee', '"""', 1),
    'COFFEESCRIPT.HEREDOC_CONTENT':             ('coffee', 'heredoc', 1),
    'COFFEESCRIPT.HEREGEX_ID':                  ('coffee', '///', 1),
    'COFFEESCRIPT.HEREGEX_CONTENT':             ('coffee', 'ab+c///', 1),
    'COFFEESCRIPT.REGULAR_EXPRESSION_ID':       ('coffee', '/ab', 1),
    'COFFEESCRIPT.REGULAR_EXPRESSION_CONTENT':  ('coffee', 'ab+c/', 1),
    'COFFEESCRIPT.REGULAR_EXPRESSION_FLAG':     ('coffee', 'gi', 1),
    'COFFEESCRIPT.JAVASCRIPT_ID':               ('coffee', '`', 1),
    'COFFEESCRIPT.JAVASCRIPT_CONTENT':          ('coffee', 'foo', 1),
    'COFFEESCRIPT.OBJECT_KEY':                  ('coffee', 'key', 1),
    'COFFEESCRIPT.IDENTIFIER':                  ('coffee', 'obj?', 1),
    'COFFEESCRIPT.LOCAL_VARIABLE':              ('coffee', 'list\n', 1),
    'COFFEESCRIPT.GLOBAL_VARIABLE':             ('coffee', 'document', 1),
    'COFFEESCRIPT.PROTOTYPE':                   ('coffee', '::', 1),
    'COFFEESCRIPT.EXISTENTIAL':                 ('coffee', '?.', 1),
    'COFFEESCRIPT.RANGE':                       ('coffee', '..', 1),
    'COFFEESCRIPT.SPLAT':                       ('coffee', '...', 1),
    'COFFEESCRIPT.OPERATIONS':                  ('coffee', '+', 1),
    'COFFEESCRIPT.BRACE':                       ('coffee', '{key', 1),
    'COFFEESCRIPT.BRACKET':                     ('coffee', '[1..', 1),
    'COFFEESCRIPT.PARENTHESIS':                 ('coffee', '(@name', 1),
    'COFFEESCRIPT.COLON':                       ('coffee', ': 1', 1),
    'COFFEESCRIPT.COMMA':                       ('coffee', ', other', 1),
    'COFFEESCRIPT.DOT':                         ('coffee', '.title', 1),
    'COFFEESCRIPT.SEMICOLON':                   ('coffee', '; yes', 1),
    'COFFEESCRIPT.BAD_CHARACTER':               'source.coffee invalid.illegal.coffee',
}

# --- Pug, GraphQL, Vue, Angular, JSP -----------------------------------------------------------
_OTHER = {
    'JADE_FILE_PATH':           ('pug', './includes', 1),
    'JADE_FILTER_NAME':         ('pug', 'markdown-it', 1),
    'JADE_JS_BLOCK':            ('pug', 'items =', 1),
    'JADE_STATEMENTS':          ('pug', 'if', 1),
    'GQL_KEYWORD':              ('graphql', 'query', 1),
    'GQL_ID':                   ('graphql', 'user', 1),
    'GQL_INT_LITERAL':          ('graphql', '10', 1),
    'GQL_STRING_LITERAL':       ('graphql', '"x"', 1),
    'VUE.SCRIPT_DELIMITERS':    ('vue', '{{', 1),
    'NG.DEEP_PSEUDO':           ('css', 'ng-deep', 1),
    # Angular: no Angular grammar installed; stacks follow the Angular Language Service grammars
    'NG.PROPERTY_BINDING_ATTR_NAME': 'text.html.derivative meta.ng-binding.property.html entity.other.ng-binding-name.property.html',
    'NG.EVENT_BINDING_ATTR_NAME':    'text.html.derivative meta.ng-binding.event.html entity.other.ng-binding-name.event.html',
    'NG.BANANA_BINDING_ATTR_NAME':   'text.html.derivative meta.ng-binding.two-way.html entity.other.ng-binding-name.two-way.html',
    'NG.TEMPLATE_BINDINGS_ATTR_NAME': 'text.html.derivative meta.ng-binding.template.html entity.other.ng-binding-name.template.html',
    'NG.TEMPLATE_VARIABLE_ATTR_NAME': 'text.html.derivative meta.ng-binding.reference.html entity.other.ng-binding-name.reference.html',
    'NG.SCRIPT_DELIMITERS':     'text.html.derivative expression.ng punctuation.definition.block.ts',
    'NG.EXPRESSIONS':           'text.html.derivative expression.ng',
    'NG.BLOCK_NAME':            'text.html.derivative control-block.ng keyword.control.block.kind.ng',
    'NG.BLOCK_BRACES':          'text.html.derivative control-block.ng punctuation.definition.block.ts',
    'NG.EXPANSION_FORM':        'text.html.derivative meta.icu.ng',
    'NG.EXPANSION_FORM_COMMA':  'text.html.derivative meta.icu.ng punctuation.separator.comma.ng',
    'NG.EXPANSION_FORM_DELIMITERS': 'text.html.derivative meta.icu.ng punctuation.definition.block.ng',
    'NG.SIGNAL':                'text.html.derivative expression.ng entity.name.function.ts',
    'NG.VARIABLE':              'text.html.derivative expression.ng variable.other.readwrite.ts',
    'JSP_DIRECTIVE_NAME':       'text.html.jsp meta.tag.directive.jsp entity.name.tag.directive.jsp',
}

MAP = {**_JS, **_TS, **_JSON, **_JSONPATH, **_COFFEE, **_OTHER}

NOTES = {
    'JS.LOCAL_VARIABLE': 'semantic: const locals are variable.readonly -> variable.other.constant (most common in modern code); let/var would be variable.other.readwrite',
    'JS.GLOBAL_VARIABLE': 'semantic variable.readonly (top-level const); explicit',
    'TS.LOCAL_VARIABLE': 'semantic variable.readonly (const); explicit',
    'TS.GLOBAL_VARIABLE': 'semantic variable.readonly (top-level const); explicit',
    'TS.TYPE_GUARD': 'narrowed parameter: VS Code shows it as a parameter; explicit',
    'JS.STATIC_MEMBER_VARIABLE': 'semantic property (static readonly would be variable.other.constant.property); explicit',
    'JS.INVALID_STRING_ESCAPE': 'VS Code JS grammar has no invalid-escape scope; any \\x is constant.character.escape',
    'TS.INVALID_STRING_ESCAPE': 'VS Code TS grammar has no invalid-escape scope; any \\x is constant.character.escape',
    'JS.BADCHARACTER': 'explicit: VS Code does not flag lexer errors; invalid.illegal like other grammars',
    'TS.BADCHARACTER': 'explicit: invalid.illegal',
    'COFFEESCRIPT.BAD_CHARACTER': 'explicit: invalid.illegal',
    'JS.JSX_CLIENT_COMPONENT': 'TextMate support.class.component (component tag), not the semantic function/class token',
    'JS.PRIMITIVE.TYPE': 'TS-only construct; same as TS.PRIMITIVE.TYPES (support.type.primitive)',
    'JSON.IDENTIFIER': 'unquoted identifiers are JSON5 keys; no VS Code JSON5 grammar, same as property key',
    'JSON.PARAMETER': 'no VS Code construct; default parameter colour',
    'JSONPATH.CONTEXT': 'no VS Code JSONPath grammar: all JSONPATH.* are explicit stacks ($/@ as variable.language)',
    'NG.PROPERTY_BINDING_ATTR_NAME': 'no Angular grammar installed: NG.* are explicit stacks modelled on the Angular Language Service grammars',
    'NG.DEEP_PSEUDO': 'VS Code CSS tokenises ::ng-deep as "::" (plain) + custom tag name ng-deep; took the name',
    'COFFEESCRIPT.LOCAL_VARIABLE': 'references are unscoped in the coffee grammar (only assignment targets get variable.assignment); took a reference',
    'JSP_DIRECTIVE_NAME': 'explicit: no JSP grammar; directive name as a tag name',
}
