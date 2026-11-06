"""Markup / config / scripting family: Markdown, YAML, INI/Properties/Buildout, .env, Dockerfile, Makefile,
Shell, reStructuredText, RegExp, GitHub Actions expressions, plus explicit stacks for languages VS Code
has no grammar for (Gherkin, HTTP Client, Mermaid, Protobuf, EditorConfig, Apache config, Cron, GitLab CI)."""

SAMPLES = {
    'md': ('text.html.markdown', '''---
title: Demo
---
# Heading one
## Heading two
### Heading three
#### Heading four
##### Heading five
###### Heading six

Plain *italic* and **bold** and ~~strike~~ text with `code span` here.

> Quoted text

- unordered item
1. ordered item

Term
: definition

[link text](https://example.com "Title") and ![image alt](img.png) and <https://auto.link>
[ref link][label]

[label]: https://example.com/def "Link title"

---

```python
def x(): pass
```

```
plain fence
```

    indented code

<!-- comment -->
<div>html block</div>

Some <kbd>Ctrl</kbd> key.

| a | b |
|---|---|
| 1 | 2 |

Footnote[^1].

[^1]: footnote text
'''),
    'yaml': ('source.yaml', '''# comment
key: plain value
quoted: "double \\n str"
single: 'single'
num: 42
anchor: &base
  child: x
ref: *base
list:
  - item
text: |
  block text
folded: >
  folded text
'''),
    'ini': ('source.ini', '''# comment
[section]
key = value
other.key=some\\tvalue
'''),
    'env': ('source.dotenv', '''# comment
API_KEY=secret
NAME="quoted"
'''),
    'docker': ('source.dockerfile', '''# comment
FROM node:20 AS build
ENV PATH=/app/bin:${VERSION} NAME="app"
RUN ["npm", "install"] && echo 'hi'; ls
COPY --from=build ./app /app
EXPOSE 8080
'''),
    'make': ('source.makefile', '''# comment
CC := gcc
SRC = $(wildcard *.c) ${CC}
.PHONY: all clean
all: main.o util.o
\t$(CC) -o app $^ \\
\t  -O2
ifeq ($(DEBUG),1)
\t@echo "debug"
endif
'''),
    'sh': ('source.shell', '''#!/bin/bash
# comment
NAME="world $HOME ${USER}"
RAW='raw string'
greet() {
  local x=42
  if [[ -n "$1" ]]; then
    echo "Hello" > /dev/null
    ls -la | grep foo
    arr=(1 2)
    out=$(date) `whoami`
  fi
}
cat <<EOT
heredoc text
EOT
greet arg
'''),
    'rst': ('source.rst', '''Section Title
=============

.. comment line

Some **bold** and *italic* and ``fixed`` and `interpreted` and |sub| and `link <http://x.org>`_.

:field: value

.. note:: Directive body

.. _target: http://example.com
'''),
    'regex': ('source.js', r'''const r = /^(?<name>[a-z]+\d{2,3})\.\@(?:x|y).*?$/gi;'''),
    'pyre': ('source.python', r'''P = re.compile(r"(?i)a(?#note)b")'''),
    'gha': ('source.github-actions-workflow', '''on: push
jobs:
  build:
    if: ${{ github.event_name == 'push' && contains(github.ref, 'main') || true || github.event.commits[0] || 3 }}
'''),
}

ILL = 'invalid.illegal.bad-character'

MAP = {
    # ---------------- Markdown ----------------
    'MARKDOWN_HEADER':                     ('md', 'Heading one'),
    'MARKDOWN_HEADER_LEVEL_1':             ('md', 'Heading one'),
    'MARKDOWN_HEADER_LEVEL_2':             ('md', 'Heading two'),
    'MARKDOWN_HEADER_LEVEL_3':             ('md', 'Heading three'),
    'MARKDOWN_HEADER_LEVEL_4':             ('md', 'Heading four'),
    'MARKDOWN_HEADER_LEVEL_5':             ('md', 'Heading five'),
    'MARKDOWN_HEADER_LEVEL_6':             ('md', 'Heading six'),
    'MARKDOWN_HEADER_MARKER':              ('md', '# Heading one'),
    'MARKDOWN_TEXT':                       ('md', 'Plain '),
    'MARKDOWN_BOLD':                       ('md', 'bold'),
    'MARKDOWN_BOLD_MARKER':                ('md', '**bold'),
    'MARKDOWN_ITALIC':                     ('md', 'italic'),
    'MARKDOWN_ITALIC_MARKER':              ('md', '*italic'),
    'MARKDOWN_STRIKE_THROUGH':             ('md', 'strike'),
    'MARKDOWN_CODE_SPAN':                  ('md', 'code span'),
    'MARKDOWN_CODE_SPAN_MARKER':           ('md', '`code span'),
    'MARKDOWN_CODE_BLOCK':                 ('md', 'indented code'),
    'MARKDOWN_CODE_FENCE':                 ('md', 'plain fence'),
    'MARKDOWN_CODE_FENCE_MARKER':          ('md', '```python'),
    'MARKDOWN_CODE_FENCE_LANGUAGE':        ('md', 'python'),
    'MARKDOWN_BLOCK_QUOTE':                ('md', 'Quoted text'),
    'MARKDOWN_BLOCK_QUOTE_MARKER':         ('md', '> Quoted'),
    'MARKDOWN_LIST_ITEM':                  ('md', 'unordered item'),
    'MARKDOWN_UNORDERED_LIST':             ('md', 'unordered item'),
    'MARKDOWN_ORDERED_LIST':               ('md', 'ordered item', 2),
    'MARKDOWN_LIST_MARKER':                ('md', '- unordered'),
    'MARKDOWN_DEFINITION_LIST':            ('md', 'Term'),
    'MARKDOWN_TERM':                       ('md', 'Term'),
    'MARKDOWN_DEFINITION':                 ('md', ': definition'),
    'MARKDOWN_DEFINITION_LIST_MARKER':     ('md', ': definition'),
    'MARKDOWN_EXPLICIT_LINK':              ('md', '(https'),
    'MARKDOWN_LINK_TEXT':                  ('md', 'link text'),
    'MARKDOWN_LINK_DESTINATION':           ('md', 'https://example.com "'),
    'MARKDOWN_LINK_TITLE':                 ('md', 'Title"'),
    'MARKDOWN_REFERENCE_LINK':             ('md', 'ref link'),
    'MARKDOWN_LINK_LABEL':                 ('md', 'label]\n'),
    'MARKDOWN_LINK_DEFINITION':            ('md', ': https://example.com/def'),
    'MARKDOWN_AUTO_LINK':                  ('md', 'https://auto.link'),
    'MARKDOWN_IMAGE':                      ('md', '![image'),
    'MARKDOWN_INLINE_HTML':                ('md', 'kbd'),
    'MARKDOWN_HTML_BLOCK':                 ('md', 'html block'),
    'MARKDOWN_COMMENT':                    ('md', ' comment '),
    'MARKDOWN_HRULE':                      ('md', '---\n\n```python'),
    'MARKDOWN_TABLE_SEPARATOR':            ('md', '| a'),
    'MARKDOWN_FRONT_MATTER_HEADER_DELIMITER': ('md', '---\ntitle'),
    'MARKDOWN_FOOTNOTE_DEFINITION':        ('md', 'footnote text'),
    'MARKDOWN_ALERT_TITLE_NOTE':           'text.html.markdown markup.quote.markdown meta.paragraph.markdown',
    'MARKDOWN_ALERT_TITLE_TIP':            ('=', 'MARKDOWN_ALERT_TITLE_NOTE'),
    'MARKDOWN_ALERT_TITLE_IMPORTANT':      ('=', 'MARKDOWN_ALERT_TITLE_NOTE'),
    'MARKDOWN_ALERT_TITLE_WARNING':        ('=', 'MARKDOWN_ALERT_TITLE_NOTE'),
    'MARKDOWN_ALERT_TITLE_CAUTION':        ('=', 'MARKDOWN_ALERT_TITLE_NOTE'),

    # ---------------- YAML ----------------
    'YAML_COMMENT':                        ('yaml', ' comment'),
    'YAML_SCALAR_KEY':                     ('yaml', 'key'),
    'YAML_SCALAR_VALUE':                   ('yaml', 'folded text'),
    'YAML_TEXT':                           ('yaml', 'plain value'),
    'YAML_SCALAR_STRING':                  ('yaml', "single'"),
    'YAML_SCALAR_DSTRING':                 ('yaml', 'double '),
    'YAML_SCALAR_LIST':                    ('yaml', 'block text'),
    'YAML_SIGN':                           ('yaml', ': plain'),
    'YAML_ANCHOR':                         ('yaml', 'base'),

    # ---------------- Properties / INI / Buildout (VS Code: source.ini for all) ----------------
    'PROPERTIES.LINE_COMMENT':             ('ini', ' comment'),
    'PROPERTIES.KEY':                      ('ini', 'key'),
    'PROPERTIES.KEY_VALUE_SEPARATOR':      ('ini', '= value'),
    'PROPERTIES.VALUE':                    ('ini', ' value'),
    'PROPERTIES.VALID_STRING_ESCAPE':      ('ini', '\\t'),
    'PROPERTIES.INVALID_STRING_ESCAPE':    ('ini', '\\t'),
    'INI.COMMENT':                         ('ini', ' comment'),
    'INI.SECTION':                         ('ini', 'section'),
    'INI.KEY':                             ('ini', 'key'),
    'INI.EQUALS':                          ('ini', '= value'),
    'INI.VALUE':                           ('ini', ' value'),
    'BUILDOUT.LINE_COMMENT':               ('ini', ' comment'),
    'BUILDOUT.SECTION_NAME':               ('ini', 'section'),
    'BUILDOUT.KEY':                        ('ini', 'key'),
    'BUILDOUT.KEY_VALUE_SEPARATOR':        ('ini', '= value'),
    'BUILDOUT.VALUE':                      ('ini', ' value'),

    # ---------------- .env ----------------
    'DOTENV_COMMENT':                      ('env', '# comment'),
    'DOTENV_KEY':                          ('env', 'API_KEY'),
    'DOTENV_SEPARATOR':                    ('env', '=secret'),
    'DOTENV_VALUE':                        ('env', 'secret'),
    'DOTENV_BAD_CHARACTER':                'source.dotenv ' + ILL,

    # ---------------- Dockerfile ----------------
    'DOCKER_COMMENTS':                     ('docker', ' comment'),
    'DOCKER_KEYWORD':                      ('docker', 'FROM'),
    'DOCKER_KEYWORD_OPERATIONS':           ('docker', 'AS'),
    'DOCKER_STRING':                       ('docker', 'npm'),
    'DOCKER_NUMBER':                       ('docker', '8080'),
    'DOCKER_VARIABLE':                     ('docker', '${VERSION}'),
    'DOCKER_ATTRIBUTES':                   ('docker', '--from'),
    'DOCKER_OPERATIONS':                   ('docker', '&&'),
    'DOCKER_OPERATION_SIGN':               ('docker', '=build'),
    'DOCKER_BRACKETS':                     ('docker', '["npm'),
    'DOCKER_BRACES':                       ('docker', '${VERSION}'),
    'DOCKER_PARENTH':                      ('docker', 'node:20'),
    'DOCKER_COMMA':                        ('docker', ', "install'),
    'DOCKER_DOT':                          ('docker', './app'),
    'DOCKER_SEMICOLON':                    ('docker', '; ls'),
    'DOCKER_BAD_CHARACTER':                'source.dockerfile ' + ILL,

    # ---------------- Makefile ----------------
    'MAKEFILE_COMMENT':                    ('make', ' comment'),
    'MAKEFILE_DOCCOMMENT':                 ('make', ' comment'),
    'MAKEFILE_KEYWORD':                    ('make', 'ifeq'),
    'MAKEFILE_TARGET':                     ('make', 'all:'),
    'MAKEFILE_SPECIAL_TARGET':             ('make', '.PHONY'),
    'MAKEFILE_SEPARATOR':                  ('make', ':='),
    'MAKEFILE_PREREQUISITE':               ('make', ' main.o'),
    'MAKEFILE_VARIABLE':                   ('make', 'CC :='),
    'MAKEFILE_VARIABLE_VALUE':             ('make', ' gcc'),
    'MAKEFILE_STRING':                     ('make', '"debug"'),
    'MAKEFILE_LINE_SPLIT':                 ('make', '\\\n'),
    'MAKEFILE_TAB':                        ('make', '\t$(CC)'),
    'MAKEFILE_FUNCTION':                   ('make', 'wildcard'),
    'MAKEFILE_FUNCTION_PARAM':             ('make', '.c'),
    'MAKEFILE_PARENTHESES':                ('make', '$(wildcard'),
    'MAKEFILE_BRACES':                     ('make', '${CC}'),
    'MAKEFILE_BAD_CHARACTER':              'source.makefile ' + ILL,

    # ---------------- Shell ----------------
    'BASH.SHEBANG':                        ('sh', '/bin/bash'),
    'BASH.LINE_COMMENT':                   ('sh', ' comment'),
    'BASH.KEYWORD':                        ('sh', 'if '),
    'BASH.NUMBER':                         ('sh', '42'),
    'BASH.STRING':                         ('sh', 'Hello'),
    'BASH.RAW_STRING':                     ('sh', 'raw string'),
    'BASH.VAR_DEF':                        ('sh', 'NAME'),
    'BASH.VAR_USE':                        ('sh', 'HOME'),
    'BASH.VAR_USE_COMPOSED':               ('sh', 'USER'),
    'BASH.HERE_DOC':                       ('sh', 'heredoc text'),
    'BASH.HERE_DOC_START':                 ('sh', 'EOT', 1),
    'BASH.HERE_DOC_END':                   ('sh', 'EOT', 2),
    'BASH.PAREN':                          ('sh', '(1 2)'),
    'BASH.BRACE':                          ('sh', '{\n  local'),
    'BASH.BRACKET':                        ('sh', '[[ -n'),
    'BASH.REDIRECTION':                    ('sh', '> /dev'),
    'BASH.CONDITIONAL':                    ('sh', '-n'),
    'BASH.EXTERNAL_COMMAND':               ('sh', 'ls -la'),
    'BASH.INTERNAL_COMMAND':               ('sh', 'echo'),
    'BASH.FUNCTION_CALL':                  ('sh', 'greet arg'),
    'BASH.FUNCTION_DEF_NAME':              ('sh', 'greet()'),
    'BASH.SUBSHELL_COMMAND':               ('sh', '$(date'),
    'BASH.BACKQUOTE':                      ('sh', '`whoami'),
    'BASH.BINARY_DATA':                    'source.shell',

    # ---------------- reStructuredText ----------------
    'REST.SECTION.HEADER':                 ('rst', '====='),
    'REST.LINE_COMMENT':                   ('rst', 'comment line'),
    'REST.BOLD':                           ('rst', '**bold'),
    'REST.ITALIC':                         ('rst', '*italic'),
    'REST.FIXED':                          ('rst', '``fixed'),
    'REST.INTERPRETED':                    ('rst', '`interpreted'),
    'REST.INLINE':                         ('rst', '|sub|'),
    'REST.REF.NAME':                       ('rst', '.. _target'),
    'REST.EXPLICIT':                       ('rst', '.. note::'),
    'REST.FIELD':                          ('rst', ':field:'),

    # ---------------- RegExp (JS regex literal; Python for (?#..) and (?i)) ----------------
    'REGEXP.CHARACTER':                    ('regex', 'x|'),
    'REGEXP.META':                         ('regex', '^'),
    'REGEXP.DOT':                          ('regex', '.*?'),
    'REGEXP.PARENTHS':                     ('regex', '(?<'),
    'REGEXP.BRACKETS':                     ('regex', '[a-z'),
    'REGEXP.BRACES':                       ('regex', '{2,3}'),
    'REGEXP.COMMA':                        ('regex', ',3}'),
    'REGEXP.QUANTIFIER':                   ('regex', '+'),
    'REGEXP.CHAR_CLASS':                   ('regex', '\\d'),
    'REGEXP.ESC_CHARACTER':                ('regex', '\\.'),
    'REGEXP.REDUNDANT_ESCAPE':             ('regex', '\\@'),
    'REGEXP.QUOTE_CHARACTER':              ('regex', '\\.'),
    'REGEXP.NAME':                         ('regex', 'name'),
    'REGEXP.OPTIONS':                      ('pyre', '(?i)'),
    'REGEXP.COMMENT':                      ('pyre', 'note'),
    'REGEXP.INVALID_STRING_ESCAPE':        'source.js string.regexp.js ' + ILL,
    'REGEXP.BAD_CHARACTER':                'source.js string.regexp.js ' + ILL,

    # ---------------- GitHub Actions expressions ----------------
    'GITHUB.EXPRESSION.IDENTIFIER':        ('gha', 'github'),
    'GITHUB.EXPRESSION.FUNCTION':          ('gha', 'contains'),
    'GITHUB.EXPRESSION.STRING':            ('gha', 'push', 2),
    'GITHUB.EXPRESSION.NUMBER':            ('gha', '3 }}'),
    'GITHUB.EXPRESSION.BOOLEAN':           ('gha', 'true'),
    'GITHUB.EXPRESSION.KEYWORD':           ('gha', 'true'),
    'GITHUB.EXPRESSION.OPERATIONS':        ('gha', ' == '),
    'GITHUB.EXPRESSION.PARENTHESES':       ('gha', ') ||'),
    'GITHUB.EXPRESSION.BRACES':            ('gha', '${{'),
    'GITHUB.EXPRESSION.BRACKETS':          ('gha', '[0'),
    'GITHUB.EXPRESSION.COMMA':             ('gha', ', '),
    'GITHUB.EXPRESSION.DOT':               ('gha', '.event_name'),

    # ---------------- Objective-C protocol reference (TextMate bridge key) ----------------

    # ---------------- explicit stacks: no VS Code grammar installed ----------------
    # GitLab CI expressions
    'GITLAB_CI_EXPRESSION_VARIABLE_PREFIX':   'source.gitlab-ci-expression variable.other.readwrite.gitlab punctuation.definition.variable.gitlab',
    'GITLAB_CI_EXPRESSION_IDENTIFIER':        'source.gitlab-ci-expression variable.other.readwrite.gitlab',
    'GITLAB_CI_EXPRESSION_STRING':            'source.gitlab-ci-expression string.quoted.double.gitlab',
    'GITLAB_CI_EXPRESSION_REGEXP':            'source.gitlab-ci-expression string.regexp.gitlab',
    'GITLAB_CI_EXPRESSION_COMPARISON_OPERATOR': 'source.gitlab-ci-expression keyword.operator.comparison.gitlab',
    'GITLAB_CI_EXPRESSION_LOGICAL_OPERATOR':  'source.gitlab-ci-expression keyword.operator.logical.gitlab',
    'GITLAB_CI_EXPRESSION_PARENTHESES':       'source.gitlab-ci-expression punctuation.section.parens.gitlab',
    'GITLAB_CI_EXPRESSION_BAD_CHARACTER':     'source.gitlab-ci-expression ' + ILL,

    # Gherkin (Cucumber TextMate bundle scopes)
    'GHERKIN_KEYWORD':                     'text.gherkin.feature keyword.language.gherkin.feature',
    'GHERKIN_TEXT':                        'text.gherkin.feature',
    'GHERKIN_COMMENT':                     'text.gherkin.feature comment.line.number-sign.gherkin',
    'GHERKIN_TAG':                         'text.gherkin.feature storage.type.tag.cucumber',
    'GHERKIN_PYSTRING':                    'text.gherkin.feature string.quoted.triple.gherkin',
    'GHERKIN_REGEXP_PARAMETER':            'text.gherkin.feature string.quoted.double.gherkin',
    'GHERKIN_OUTLINE_PARAMETER_SUBSTITUTION': 'text.gherkin.feature variable.other.gherkin',
    'GHERKIN_TABLE_PIPE':                  'text.gherkin.feature keyword.control.cucumber.table',
    'GHERKIN_TABLE_CELL':                  'text.gherkin.feature',
    'GHERKIN_TABLE_HEADER_CELL':           'text.gherkin.feature',

    # HTTP Client (REST Client extension scopes)
    'HTTP_REQUEST_METHOD_TYPE':            'source.http keyword.control.http',
    'HTTP_REQUEST_KEYWORD':                'source.http keyword.other.http',
    'HTTP_REQUEST_PROTOCOL':               'source.http keyword.other.http',
    'PROTOCOL':                            ('=', 'HTTP_REQUEST_PROTOCOL'),
    'HTTP_REQUEST_PORT':                   'source.http constant.numeric.http',
    'HTTP_REQUEST_PARAMETER_NAME':         'source.http variable.parameter.http',
    'HTTP_REQUEST_PARAMETER_VALUE':        'source.http string.unquoted.http',
    'HTTP_HEADER_FIELD_NAME':              'source.http support.type.property-name.http',
    'HTTP_HEADER_FIELD_VALUE':             'source.http string.other.http',
    'HTTP_REQUEST_COMMENT':                'source.http comment.line.sharp.http',
    'HTTP_REQUEST_SEPARATOR':              'source.http comment.line.sharp.http',
    'HTTP_REQUEST_NAME':                   'source.http comment.line.sharp.http',
    'HTTP_REQUEST_DOC_COMMENT_TAG':        'source.http comment.line.sharp.http',
    'HTTP_REQUEST_MESSAGE_BODY':           'source.http',
    'HTTP_REQUEST_BODY':                   'source.http',
    'HTTP_REQUEST_SCRIPT':                 'source.http',
    'HTTP_REQUEST_INPUT_SIGN':             'source.http keyword.operator.http',
    'HTTP_REQUEST_INPUT_FILE':             'source.http string.unquoted.path.http',
    'HTTP_REQUEST_DIFFERENCE_SIGN':        'source.http keyword.operator.http',
    'HTTP_REQUEST_DIFFERENCE_FILE':        'source.http string.unquoted.path.http',
    'HTTP_REQUEST_MULTIPART_BOUNDARY':     'source.http comment.line.boundary.http',
    'HTTP_REQUEST_ENVIRONMENT_VARIABLE':   'source.http variable.other.http',
    'HTTP_REQUEST_VARIABLE_BRACES':        'source.http punctuation.definition.variable.http',
    'HTTP_REQUEST_ESCAPED_VALUE':          'source.http constant.character.escape.http',
    'HTTP_REQUEST_FILE_VARIABLE_BEGIN':    'source.http keyword.other.http',
    'HTTP_REQUEST_FILE_VARIABLE_NAME':     'source.http variable.other.http',
    'HTTP_REQUEST_FILE_VARIABLE_VALUE':    'source.http string.unquoted.http',
    'HTTP_REQUEST_DYNAMIC_VARIABLE_STRING': 'source.http string.quoted.double.http',
    'HTTP_REQUEST_DYNAMIC_VARIABLE_NUMBER': 'source.http constant.numeric.http',
    'HTTP_FILE_IMPORT_KEYWORD':            'source.http keyword.control.import.http',
    'HTTP_FILE_IMPORT':                    'source.http string.unquoted.path.http',
    'HTTP_IMPORT':                         'source.http string.unquoted.path.http',
    'HTTP_RUN_KEYWORD':                    'source.http keyword.control.http',
    'HTTP_RUN':                            'source.http string.unquoted.path.http',

    # Mermaid (markdown-mermaid extension scopes)
    'MERMAID_KEYWORD':                     'source.mermaid keyword.control.mermaid',
    'MERMAID_DIAGRAM_NAME':                'source.mermaid keyword.control.mermaid',
    'MERMAID_STRING':                      'source.mermaid string.quoted.double.mermaid',
    'MERMAID_COMMENT':                     'source.mermaid comment.line.percentage.mermaid',
    'MERMAID_IDENTIFIER':                  'source.mermaid variable.other.mermaid',
    'MERMAID_CONSTANT':                    'source.mermaid constant.language.mermaid',
    'MERMAID_OPERATOR':                    'source.mermaid keyword.operator.mermaid',
    'MERMAID_EDGE':                        'source.mermaid keyword.operator.arrow.mermaid',
    'MERMAID_NOTE':                        'source.mermaid string.unquoted.note.mermaid',
    'MERMAID_GENERIC':                     'source.mermaid entity.name.type.mermaid',
    'MERMAID_TITLE':                       'source.mermaid string.unquoted.title.mermaid',
    'MERMAID_FRONTMATTER_DELIMITER':       'source.mermaid punctuation.definition.begin.frontmatter',

    # Protobuf (vscode-proto3 scopes)
    'PROTO_KEYWORD':                       'source.proto keyword.other.proto',
    'PROTO_IDENTIFIER':                    'source.proto',
    'PROTO_NUMBER':                        'source.proto constant.numeric.proto',
    'PROTO_STRING':                        'source.proto string.quoted.double.proto',
    'PROTO_ENUM_VALUE':                    'source.proto variable.other.enummember.proto',
    'PROTO_LINE_COMMENT':                  'source.proto comment.line.double-slash.proto',
    'PROTO_BLOCK_COMMENT':                 'source.proto comment.block.proto',
    'PROTO_OPERATION_SIGN':                'source.proto keyword.operator.assignment.proto',
    'PROTO_BRACES':                        'source.proto punctuation.section.block.proto',
    'PROTO_BRACKETS':                      'source.proto punctuation.section.brackets.proto',
    'PROTO_PARENTHESES':                   'source.proto punctuation.section.parens.proto',
    'PROTO_DOT':                           'source.proto punctuation.accessor.proto',
    'PROTO_SEMICOLON':                     'source.proto punctuation.terminator.proto',
    'PROTO_COMMA':                         'source.proto punctuation.separator.proto',
    'PROTO_VALID_STRING_ESCAPE':           'source.proto string.quoted.double.proto constant.character.escape.proto',
    'PROTO_INVALID_STRING_ESCAPE':         'source.proto string.quoted.double.proto ' + ILL,
    'PROTO_BAD_CHARACTER':                 'source.proto ' + ILL,
    'PROTOTEXT_IDENTIFIER':                'source.textproto',
    'PROTOTEXT_NUMBER':                    'source.textproto constant.numeric.textproto',
    'PROTOTEXT_STRING':                    'source.textproto string.quoted.double.textproto',
    'PROTOTEXT_ENUM_VALUE':                'source.textproto variable.other.enummember.textproto',
    'PROTOTEXT_LINE_COMMENT':              'source.textproto comment.line.number-sign.textproto',
    'PROTOTEXT_COMMENT_DIRECTIVE':         'source.textproto comment.line.number-sign.textproto',
    'PROTOTEXT_OPERATION_SIGN':            'source.textproto punctuation.separator.key-value.textproto',
    'PROTOTEXT_BRACES':                    'source.textproto punctuation.section.block.textproto',
    'PROTOTEXT_BRACKETS':                  'source.textproto punctuation.section.brackets.textproto',
    'PROTOTEXT_DOT':                       'source.textproto punctuation.accessor.textproto',
    'PROTOTEXT_SEMICOLON':                 'source.textproto punctuation.terminator.textproto',
    'PROTOTEXT_COMMA':                     'source.textproto punctuation.separator.textproto',
    'PROTOTEXT_VALID_STRING_ESCAPE':       'source.textproto string.quoted.double.textproto constant.character.escape.textproto',
    'PROTOTEXT_INVALID_STRING_ESCAPE':     'source.textproto string.quoted.double.textproto ' + ILL,
    'PROTOTEXT_BAD_CHARACTER':             'source.textproto ' + ILL,

    # EditorConfig (EditorConfig extension: ini-like scopes)
    'EDITORCONFIG_LINE_COMMENT':           'source.editorconfig comment.line.number-sign.editorconfig',
    'EDITORCONFIG_PATTERN':                'source.editorconfig entity.name.section.group-title.editorconfig',
    'EDITORCONFIG_SPECIAL_SYMBOL':         'source.editorconfig entity.name.section.group-title.editorconfig keyword.operator.glob.editorconfig',
    'EDITORCONFIG_BRACE':                  'source.editorconfig entity.name.section.group-title.editorconfig',
    'EDITORCONFIG_BRACKET':                'source.editorconfig entity.name.section.group-title.editorconfig',
    'EDITORCONFIG_COMMA':                  'source.editorconfig entity.name.section.group-title.editorconfig',
    'EDITORCONFIG_VALID_CHAR_ESCAPE':      'source.editorconfig entity.name.section.group-title.editorconfig constant.character.escape.editorconfig',
    'EDITORCONFIG_INVALID_CHAR_ESCAPE':    'source.editorconfig ' + ILL,
    'EDITORCONFIG_PROPERTY_KEY':           'source.editorconfig keyword.other.definition.editorconfig',
    'EDITORCONFIG_SEPARATOR':              'source.editorconfig punctuation.separator.key-value.editorconfig',
    'EDITORCONFIG_PROPERTY_VALUE':         'source.editorconfig',
    'EDITORCONFIG_IDENTIFIER':             'source.editorconfig',
    'EDITORCONFIG_VARIABLE':               'source.editorconfig',
    'EDITORCONFIG_BAD_CHARACTER':          'source.editorconfig ' + ILL,

    # Apache config
    'APACHE_CONFIG.COMMENT':               'source.apacheconf comment.line.number-sign.apacheconf',
    'APACHE_CONFIG.IDENTIFIER':            'source.apacheconf keyword.other.directive.apacheconf',
    'APACHE_CONFIG.ARG_LEXEM':             'source.apacheconf',

    # Cron expressions
    'CRONEXP.NUMBER':                      'source.cron constant.numeric.cron',
    'CRONEXP.OPERATOR':                    'source.cron keyword.operator.cron',
    'CRONEXP.IDENTIFIER':                  'source.cron constant.language.cron',
}

NOTES = {
    'MARKDOWN_HEADER_LEVEL_1': 'IntelliJ colours the whole header; mapped to heading text (entity.name.section), "#" via MARKDOWN_HEADER_MARKER',
    'MARKDOWN_LIST_ITEM': 'element-level key over the item text; VS Code leaves item text plain (marker via MARKDOWN_LIST_MARKER)',
    'MARKDOWN_UNORDERED_LIST': 'element-level key; item text (plain in VS Code)',
    'MARKDOWN_ORDERED_LIST': 'element-level key; item text (plain in VS Code)',
    'MARKDOWN_DEFINITION_LIST': 'VS Code markdown has no definition lists: plain paragraph text',
    'MARKDOWN_LINK_DEFINITION': 'element key over the whole [label]: url "title" line; label/dest/title keys paint the parts, so only the ": " separator shows it (plain in VS Code; an underline here would leak onto the label/title)',
    'MARKDOWN_EXPLICIT_LINK': 'element key over [text](dest); LINK_TEXT/LINK_DESTINATION cover the parts, visible on the ( ) punctuation (plain in VS Code)',
    'MARKDOWN_IMAGE': 'element key over ![alt](dest); visible on ! ( ) punctuation (plain in VS Code)',
    'MARKDOWN_HTML_BLOCK': 'whole HTML block; tags come from the injected HTML, so this key shows on the text content (plain in VS Code)',
    'MARKDOWN_FOOTNOTE_DEFINITION': 'the footnote body text after [^1]: (demo page); plain paragraph in VS Code',
    'MARKDOWN_ALERT_TITLE_NOTE': 'explicit: built-in markdown grammar has no GFM alerts, [!NOTE] is plain quote text (only the Nuxt MDC extension re-scopes it)',
    'MARKDOWN_CODE_FENCE': 'fence content without language; with a language VS Code embeds that grammar',
    'YAML_TEXT': 'plain (unquoted) scalar; numbers/booleans share it in IntelliJ, strings are the common case',
    'YAML_SCALAR_VALUE': 'YAMLHighlighter.SCALAR_VALUE paints SCALAR_TEXT = folded (>) block scalar content',
    'PROPERTIES.KEY': 'VS Code tokenises .properties with the ini grammar; escapes are not scoped (plain value)',
    'PROPERTIES.INVALID_STRING_ESCAPE': 'VS Code ini grammar does not scope escapes: plain value',
    'BUILDOUT.KEY': 'buildout.cfg is INI; VS Code ini grammar',
    'DOCKER_NUMBER': 'VS Code dockerfile grammar only scopes instructions, strings, comments; args plain',
    'MAKEFILE_DOCCOMMENT': 'make has no doc comments in VS Code: ## is a line comment',
    'BASH.BINARY_DATA': 'explicit: plain shell text (no VS Code construct)',
    'REST.SECTION.HEADER': 'VS Code rst grammar scopes only the underline (markup.heading); title text stays plain',
    'REGEXP.QUOTE_CHARACTER': '\\Q..\\E has no JS form; same as an escape (constant.character.escape.backslash.regexp)',
    'REGEXP.OPTIONS': 'inline (?i) options: taken from VS Code python regexp grammar (JS has none)',
    'REGEXP.COMMENT': '(?#..) comment: taken from VS Code python regexp grammar (JS has none)',
    'REGEXP.INVALID_STRING_ESCAPE': 'explicit invalid.illegal (VS Code does not flag it)',
    'GITHUB.EXPRESSION.BOOLEAN': 'github-actions grammar scopes true/false as variable.other.read (what VS Code shows)',
    'GITHUB.EXPRESSION.KEYWORD': 'expression keywords (true/false/null) share the boolean token',
    'GHERKIN_KEYWORD': 'explicit: no Gherkin grammar installed; Cucumber TextMate bundle scopes, cells plain',
    'HTTP_REQUEST_METHOD_TYPE': 'explicit: no .http grammar installed; REST Client-style scopes',
    'MERMAID_KEYWORD': 'explicit: no mermaid grammar installed',
    'PROTO_KEYWORD': 'explicit: no proto grammar installed; identifiers/types plain like vscode-proto3',
    'EDITORCONFIG_PATTERN': 'explicit: ini-like (section = entity.name.section, key = keyword.other.definition)',
    'APACHE_CONFIG.IDENTIFIER': 'explicit: no apache grammar installed',
    'CRONEXP.NUMBER': 'explicit: no cron grammar',
    'GITLAB_CI_EXPRESSION_IDENTIFIER': 'explicit: no GitLab CI grammar installed',
    'DOTENV_BAD_CHARACTER': 'explicit invalid.illegal (all *_BAD_CHARACTER keys)',
}
