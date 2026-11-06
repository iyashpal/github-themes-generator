"""Python (PyCharm / PythonCore + Pythonid plugins): Python incl. f-strings and docstrings,
requirements.txt, Django/Jinja2 templates (shared DJANGO_* keys), Django URL path patterns and the
GNU-style command line of the manage.py / setup.py task console. Cython and Chameleon reuse PY.* /
XML keys; no Jupyter keys exist in these plugins.

Keys come from PyHighlighter, RequirementsSyntaxHighlighter, Jinja2TemplateHighlighterColors,
DjangoUrlPathLanguageKt and CommandLineSyntaxHighlighter (static initialisers).

VS Code: built-in python grammar (Pylance's own grammar where installed) plus Pylance semantic tokens.
Identifier keys use explicit `source.python <scope>` stacks from Pylance's semanticTokenScopes or
VS Code's standard fallback table; everything else is sample-based.
requirements.txt uses the pip-requirements grammar of the ms-python extension."""

PY = r'''# line comment
from dataclasses import dataclass


@dataclass
class User(Base):
    """Represents a user.

    :param name: the name
    """

    def __init__(self, name, items):
        super().__init__()
        self.name = name.strip()
        self.items = [x * 2 for x in items if x > 0.5]
        self.meta = {"key": "a\tb\qc", 'n': 42}
        data = b'raw\n'
        label = f'{name!r:>{10}}' + f"{len(items):08d}"
        print(len(self.items), __name__)
'''

REQ = r'''# pinned deps
requests==2.31.0
Django>=4.2; python_version >= "3.10"
https://example.com/pkg.zip#egg=pkg
-r ${BASE_DIR}/base.txt
'''

URLS = r'''urlpatterns = [path("articles/<int:year>/", views.year)]
'''

CMD = r'''manage.py migrate --fake -v 2 app
'''

SAMPLES = {
    'py': ('source.python', PY),
    'req': ('source.pip-requirements', REQ),
    'urls': ('source.python', URLS),
    'cmd': ('source.shell', CMD),
}

DJ = 'text.html.django'

MAP = {
    # ---------------------------------------------------------------- Python: lexer keys (TextMate)
    'PY.KEYWORD':               ('py', 'for'),
    'PY.LINE_COMMENT':          ('py', '#'),
    'PY.DOC_COMMENT':           ('py', 'Represents'),
    'PY.DOC_COMMENT_TAG':       ('py', ':param'),
    'PY.STRING.U':              ('py', 'key'),
    'PY.STRING.B':              ('py', 'raw'),
    'PY.STRING':                ('=', 'PY.STRING.U'),
    'PY.VALID_STRING_ESCAPE':   ('py', '\\t'),
    'PY.INVALID_STRING_ESCAPE': 'source.python string.quoted.single.python constant.character.escape.python',
    'PY.NUMBER':                ('py', '42'),
    'PY.OPERATION_SIGN':        ('py', '* 2'),
    'PY.BRACES':                ('py', '{"'),
    'PY.BRACKETS':              ('py', '[x'),
    'PY.PARENTHS':              ('py', '(self'),
    'PY.COMMA':                 ('py', ', name'),
    'PY.DOT':                   ('py', '.name'),
    'PY.DECORATOR':             ('py', '@dataclass'),
    # f-strings
    'PY.FSTRING_FRAGMENT_BRACES':          ('py', '{name!r'),
    'PY.FSTRING_FRAGMENT_TYPE_CONVERSION': ('py', '!r'),
    'PY.FSTRING_FRAGMENT_COLON':           ('py', ':>'),
    'PY.FSTRING_FORMAT_SPEC_SPECIAL_CHAR': ('py', '08d'),
    'PY.FSTRING_FORMAT_SPEC_NUMBER':       ('py', '8d'),
    # ---------------------------------------------------------------- Python: identifiers (Pylance semantic)
    'PY.CLASS_DEFINITION':      'source.python entity.name.type.class',
    'PY.FUNC_DEFINITION':       'source.python entity.name.function',
    'PY.NESTED_FUNC_DEFINITION': 'source.python entity.name.function',
    'PY.PREDEFINED_DEFINITION': 'source.python support.function.magic.python',
    'PY.PREDEFINED_USAGE':      'source.python variable.other.readwrite',
    'PY.BUILTIN_NAME':          'source.python entity.name.type.class',
    'PY.PARAMETER':             'source.python variable.parameter',
    'PY.SELF_PARAMETER':        'source.python variable.parameter.function.language.special.self.python',
    'PY.KEYWORD_ARGUMENT':      'source.python variable.parameter.function-call.python',
    'PY.FUNCTION_CALL':         'source.python entity.name.function',
    'PY.METHOD_CALL':           'source.python entity.name.function.member',
    'PY.ANNOTATION':            'source.python entity.name.type.class',
    'PY.LOCAL_VARIABLE':        'source.python variable.other.readwrite',
    'PY.TYPE_PARAMETER':        'source.python entity.name.type.parameter',

    # ---------------------------------------------------------------- requirements.txt
    'REQUIREMENTS_COMMENT':      ('req', 'pinned'),
    'IDENTIFIER': ('=', 'DEFAULT_IDENTIFIER'),  # global key name shared by many plugins: keep neutral
    'REQUIREMENTS_OPERATOR':     ('req', '=='),
    'REQUIREMENTS_VERSION':      ('req', '2.31.0'),
    'REQUIREMENTS_SEMICOLON':    ('req', ';'),
    'REQUIREMENTS_PYTHON_STR_C': ('req', '3.10'),
    'REQUIREMENTS_URL':          ('req', 'https'),
    'REQUIREMENTS_SHARP':        ('req', '#egg'),
    'REQUIREMENTS_ENV_VAR':      ('req', 'BASE_DIR'),

    # ---------------------------------------------------------------- Django / Jinja2 templates (no grammar here)
    'DJANGO_TAG_START_END':  f'{DJ} meta.scope.django.template.tag punctuation.section.embedded.begin.django',
    'DJANGO_TAG_NAME':       f'{DJ} meta.scope.django.template.tag keyword.control.tag-name.django',
    'DJANGO_KEYWORD':        f'{DJ} meta.scope.django.template.tag keyword.control.django',
    'DJANGO_ID':             f'{DJ} meta.scope.django.template.variable variable.other.django',
    'DJANGO_FILTER':         f'{DJ} meta.scope.django.template.variable support.function.filter.django',
    'DJANGO_STRING_LITERAL': f'{DJ} meta.scope.django.template.tag string.quoted.double.django',
    'DJANGO_NUMBER':         f'{DJ} meta.scope.django.template.tag constant.numeric.django',
    'DJANGO_COMMENT':        f'{DJ} comment.block.django.template',

    # ---------------------------------------------------------------- Django URL path patterns (inside a str)
    'DJANGO_URL_PATH.GT_LT': ('urls', '<int'),
    'DJANGO_URL_PATH.ID':    ('urls', 'year>'),

    # ---------------------------------------------------------------- manage.py / setup.py task command line
    'GNU.LETTER':       ('cmd', 'app'),
    'GNU.NUMBER':       ('cmd', '2'),
    'GNU.SHORT_OPTION': ('cmd', '-v'),
    'GNU.LONG_OPTION':  ('cmd', '--fake'),
}

NOTES = {
    'PY.STRING': 'legacy key (no longer declared by PyHighlighter, still in our scheme); same as PY.STRING.U',
    'PY.DOC_COMMENT_TAG': 'VS Code does not parse docstring tags: the docstring colour',
    'PY.INVALID_STRING_ESCAPE': 'explicit: Pylance emits string+escapeCharacter|invalid (98304); selector score '
                                '`string.escapeCharacter:python` 210 beats `*.invalid:python` 110, so the foreground is the '
                                'escape colour; VS Code additionally takes italic from invalid.illegal (escape rule has no '
                                'fontStyle), which a single stack cannot express',
    'PY.CLASS_DEFINITION': 'explicit: Pylance semantic class',
    'PY.FUNC_DEFINITION': 'explicit: Pylance semantic function/method declaration',
    'PY.NESTED_FUNC_DEFINITION': 'explicit: Pylance semantic function',
    'PY.PREDEFINED_DEFINITION': 'explicit: Pylance magicFunction scope (def __init__)',
    'PY.PREDEFINED_USAGE': 'explicit: IntelliJ paints qualified/class-scope dunders (f.__doc__, cls.__name__, '
                           'obj.__dict__, super().__init__). Pylance emits dunder attributes as variable/property '
                           '(default fg, TM blue overridden); only dunder method refs are magicFunction (blue). '
                           'Attributes outnumber dunder calls ~3.6:1 in the stdlib -> variable',
    'PY.BUILTIN_NAME': 'explicit: any non-decorator reference into builtins. Pylance emits builtin classes '
                       '(str, int, bool, list, ValueError) as class -> entity.name.type.class and builtin functions '
                       '(len, print) as function (builtin modifier unmapped, no defaultLibrary). Classes outnumber '
                       'functions ~4.5:1 in real code (and 3:1 in the colors-page demo) -> class',
    'PY.PARAMETER': 'explicit: Pylance parameter -> variable.parameter (declaration and usages)',
    'PY.SELF_PARAMETER': 'explicit: Pylance selfParameter scope',
    'PY.KEYWORD_ARGUMENT': 'explicit: Pylance parameter.keywordArgument scope',
    'PY.FUNCTION_CALL': 'explicit: Pylance semantic function',
    'PY.METHOD_CALL': 'explicit: Pylance semantic method',
    'PY.ANNOTATION': 'explicit: annotations are mostly class names -> Pylance class',
    'PY.LOCAL_VARIABLE': 'explicit: Pylance semantic variable',
    'PY.TYPE_PARAMETER': 'explicit: Pylance semantic typeParameter',
    'IDENTIFIER': 'requirements.txt package name (RequirementsSyntaxHighlighter registers the bare name IDENTIFIER)',
    'DJANGO_TAG_START_END': 'explicit (no Django grammar installed); stacks of batisteo.vscode-django; also used by Jinja2',
    'DJANGO_URL_PATH.GT_LT': 'VS Code: plain Python string',
    'GNU.LETTER': 'manage.py task console input; tokenised as a shell command line',
}
