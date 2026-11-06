"""GoLand languages (org.jetbrains.plugins.go + org.jetbrains.plugins.go-template).

* Go (GO_*): VS Code's built-in Go grammar. gopls semantic tokens are off by default in VS Code, so
  everything is TextMate. Keys from com.goide.highlighting.GoSyntaxHighlightingColors.
  For keys GoLand applies to both a declaration and its usages (parameters, receivers, constants,
  variables, fields), the usage is mapped: usages are far more common, and VS Code colours only
  the declaration specially.
* go.mod / go.work (VGO_*, COMMENT): golang.go extension's go.mod grammar (scope `go.mod`; go.work uses
  the same grammar). Not installed here, so explicit stacks (taken by tokenising with that grammar).
  go.sum has no highlighting keys in GoLand.
* Plan9 assembly (com.plan9.*): the Go extension has no grammar for `go.asm`; the de-facto one is
  quillaja.goasm (scope `source.x86`). Explicit stacks.
* Go templates (GO_TEMPLATE_*, plugin org.jetbrains.plugins.go-template): jinliming2.vscode-go-template,
  which injects `source.go-template` into HTML/JS/CSS/... inside `meta.embedded.go-template`, with the
  `{{ }}` delimiters as punctuation.section.embedded. Explicit stacks.
"""

GO = r'''//go:build linux && (amd64 || arm64)

// Package server serves things.
// TODO: see [Server.Start] and [fmt.Println].
package server

import (
	"fmt"
	"strings"
)

/* block comment */
const MaxSize = 10
const minSize = 1

var Counter = 0
var counter = 0
var Handler = func() {}
var handler = func() {}

type Reader interface {
	Read(p []byte) (n int, err error)
}

type reader interface{ read() }

type Server struct {
	Name    string `json:"name,omitempty" xml:"n"`
	port    int
	OnStop  func()
	onStart func()
}

type config struct{ debug bool }

func (s *Server) Start(r Reader, rd reader, c config) error {
	const retries = 3
	total := 0
	for i := 0; i < retries; i++ {
		total += i
	}
	x, err := helper(s.port), error(nil)
	x, y := 1, 2
	if x := 5; x > y {
		fmt.Println(x)
	}
	fn := func() {}
	fn()
	s.OnStop()
	s.onStart()
	Handler()
	handler()
	msg := fmt.Sprintf("name=%s\n\q", s.Name)
	arr := []int{1, 2}
	arr = append(arr, len(msg), 0x1F)
	fmt.Println(MaxSize, minSize, retries, Counter, counter, arr, total)
	var sb strings.Builder
	_, _ = sb, c
	if s == nil || !true {
		goto done
	}
done:
	return err
}

func helper(p int) int { return p }
'''

# builtin.go: how GoLand's GO_BUILTIN_FUNCTION (declarations of builtins) looks in VS Code
BUILTIN = r'''package builtin

func len(v Type) int
'''

SAMPLES = {
    'go': ('source.go', GO),
    'builtin': ('source.go', BUILTIN),
}

MOD = 'go.mod'
ASM = 'source.x86'
TPL = 'text.html.derivative meta.embedded.go-template'

MAP = {
    # ---------------------------------------------------------------- Go: lexer tokens
    'GO_KEYWORD':                 ('go', 'return'),
    'GO_LINE_COMMENT':            ('go', '// Package'),
    'GO_BLOCK_COMMENT':           ('go', '/*'),
    'GO_COMMENT_KEYWORD':         ('go', 'go:build'),
    'GO_COMMENT_REFERENCE':       ('go', '[Server.Start]'),
    'GO_BUILD_TAG':               ('go', 'linux'),
    'GO_BUILD_PAREN':             ('go', '(amd64'),
    'GO_BUILD_OPERATOR':          ('go', '&&'),
    'GO_STRING':                  ('go', 'name='),
    'GO_VALID_STRING_ESCAPE':     ('go', r'\n'),
    'GO_INVALID_STRING_ESCAPE':   ('go', r'\q'),
    'GO_NUMBER':                  ('go', '10'),
    'GO_BRACKET':                 ('go', '[]byte'),
    'GO_BRACES':                  ('go', '{\n\tRead'),
    'GO_PARENTHESES':             ('go', '(p []byte'),
    'GO_OPERATOR':                ('go', ':= 0'),
    'GO_DOT':                     ('go', '.Println(x'),
    'GO_SEMICOLON':               ('go', '; i <'),
    'GO_COLON':                   ('go', ':\n\treturn'),
    'GO_COMMA':                   ('go', ', err error'),
    'GO_IDENTIFIER':              ('go', 'x)'),
    'GO_BAD_TOKEN':               'source.go invalid.illegal.go',
    # ---------------------------------------------------------------- Go: types
    'GO_TYPE_SPECIFICATION':          ('go', 'Server struct'),
    'GO_PACKAGE_EXPORTED_STRUCT':     ('go', 'Server struct'),
    'GO_PACKAGE_LOCAL_STRUCT':        ('go', 'config struct'),
    'GO_PACKAGE_EXPORTED_INTERFACE':  ('go', 'Reader interface'),
    'GO_PACKAGE_LOCAL_INTERFACE':     ('go', 'reader interface'),
    'GO_TYPE_REFERENCE':              ('go', 'Server)'),
    'GO_EXPORTED_STRUCT_REFERENCE':   ('go', 'Builder'),
    'GO_LOCAL_STRUCT_REFERENCE':      ('go', 'config) error'),
    'GO_EXPORTED_INTERFACE_REFERENCE': ('go', 'Reader, rd'),
    'GO_LOCAL_INTERFACE_REFERENCE':   ('go', 'reader, c'),
    'GO_BUILTIN_TYPE_REFERENCE':      ('go', 'string `'),
    # ---------------------------------------------------------------- Go: functions
    'GO_EXPORTED_FUNCTION':           ('go', 'Start('),
    'GO_LOCAL_FUNCTION':              ('go', 'helper(p int'),
    'GO_BUILTIN_FUNCTION':            ('builtin', 'len'),
    'GO_EXPORTED_FUNCTION_CALL':      ('go', 'Println(x'),
    'GO_LOCAL_FUNCTION_CALL':         ('go', 'helper(s.port'),
    'GO_BUILTIN_FUNCTION_CALL':       ('go', 'len(msg'),
    'GO_PACKAGE_EXPORTED_VARIABLE_CALL': ('go', 'Handler()'),
    'GO_PACKAGE_LOCAL_VARIABLE_CALL': ('go', 'handler()'),
    'GO_LOCAL_VARIABLE_CALL':         ('go', 'fn()'),
    'GO_STRUCT_EXPORTED_MEMBER_CALL': ('go', 'OnStop()'),
    'GO_STRUCT_LOCAL_MEMBER_CALL':    ('go', 'onStart()'),
    # ---------------------------------------------------------------- Go: values (usages)
    'GO_PACKAGE':                     ('go', 'fmt.Println(x'),
    'GO_BUILTIN_CONSTANT':            ('go', 'true'),
    'GO_BUILTIN_VARIABLE':            ('go', 'nil'),
    'GO_PACKAGE_EXPORTED_CONSTANT':   ('go', 'MaxSize,'),
    'GO_PACKAGE_LOCAL_CONSTANT':      ('go', 'minSize,'),
    'GO_LOCAL_CONSTANT':              ('go', 'retries,'),
    'GO_PACKAGE_EXPORTED_VARIABLE':   ('go', 'Counter,'),
    'GO_PACKAGE_LOCAL_VARIABLE':      ('go', 'counter,'),
    'GO_STRUCT_EXPORTED_MEMBER':      ('go', 'Name)'),
    'GO_STRUCT_LOCAL_MEMBER':         ('go', 'port)'),
    'GO_METHOD_RECEIVER':             ('go', 's.OnStop'),
    'GO_FUNCTION_PARAMETER':          ('go', 'p }'),
    'GO_LOCAL_VARIABLE':              ('go', 'total)'),
    'GO_SCOPE_VARIABLE':              ('go', 'i++'),
    'GO_SHADOWING_VARIABLE':          ('go', 'x := 5'),
    'GO_REASSIGNMENT_IN_SHORT_VAR_DECLARATION': ('go', 'x, y :='),
    'GO_LABEL':                       ('go', 'done:'),
    # ---------------------------------------------------------------- Go: struct tags (one raw string in VS Code)
    'GO_TAG_KEY':                     ('go', 'json:'),
    'GO_TAG_COLON':                   ('go', ':"name'),
    'GO_TAG_VALUE':                   ('go', '"name,'),
    'GO_TAG_TEXT':                    ('go', ' xml:'),

    # ---------------------------------------------------------------- go.mod / go.work (golang.go grammar)
    'VGO_MODULE_KEYWORD':     f'{MOD} keyword.go.mod',
    'VGO_GO_KEYWORD':         f'{MOD} keyword.go.mod',
    'VGO_TOOLCHAIN_KEYWORD':  f'{MOD} keyword.go.mod',
    'VGO_GODEBUG_KEYWORD':    f'{MOD} keyword.go.mod',
    'VGO_REQUIRE_KEYWORD':    f'{MOD} keyword.go.mod',
    'VGO_REPLACE_KEYWORD':    f'{MOD} keyword.go.mod',
    'VGO_EXCLUDE_KEYWORD':    f'{MOD} keyword.go.mod',
    'VGO_RETRACT_KEYWORD':    f'{MOD} keyword.go.mod',
    'VGO_TOOL_KEYWORD':       f'{MOD} keyword.go.mod',
    'VGO_IGNORE_KEYWORD':     f'{MOD} keyword.go.mod',
    'VGO_USE_KEYWORD':        f'{MOD} keyword.go.mod',
    'VGO_GO_VERSION':         f'{MOD} string.unquoted.go.mod',
    'VGO_MODULE_VERSION':     f'{MOD} constant.language.go.mod',
    'VGO_BAD_CHARACTER':      f'{MOD} invalid.illegal.unknown.go.mod',
    'COMMENT':                f'{MOD} comment.line.double-slash.go.mod',

    # ---------------------------------------------------------------- Plan9 assembly (quillaja.goasm grammar)
    'com.plan9.LINE_COMMENT':       f'{ASM} comment.line',
    'com.plan9.INSTRUCTION':        f'{ASM} entity.name.function',
    'com.plan9.PSEUDO_INSTRUCTION': f'{ASM} storage.type',
    'com.plan9.KEYWORD':            f'{ASM} storage.type',
    'com.plan9.DIRECTIVE':          f'{ASM} storage.type',
    'com.plan9.FLAG':               f'{ASM} storage.modifier',
    'com.plan9.REGISTER':           f'{ASM} variable.other.readwrite',
    'com.plan9.LABEL':              f'{ASM} variable.function',
    'com.plan9.NUMBER':             f'{ASM} constant.numeric.dec',
    'com.plan9.STRING':             ASM,
    'com.plan9.PREPROCESSOR':       f'{ASM} meta.preprocessor.c keyword.control.import.c',
    'com.plan9.IDENTIFIER':         ASM,
    'com.plan9.OPERATOR':           ASM,
    'com.plan9.PARENTHESIS':        ASM,

    # ---------------------------------------------------------------- Go templates (jinliming2.vscode-go-template)
    'GO_TEMPLATE_DELIMITER':   f'{TPL} punctuation.section.embedded.begin.go-template',
    'GO_TEMPLATE_KEYWORD':     f'{TPL} keyword.control.go-template',
    'GO_TEMPLATE_VARIABLE':    f'{TPL} variable.other.readwrite.go-template',
    'GO_TEMPLATE_IDENTIFIER':  f'{TPL} variable.sub.property.go-template',
    'GO_TEMPLATE_DOT':         f'{TPL} variable.sub.property.go-template',
    'GO_TEMPLATE_STRING':      f'{TPL} string.quoted.double.go-template',
    'GO_TEMPLATE_COMMENT':     f'{TPL} comment.block.go-template',
    'GO_TEMPLATE_OPERATOR':    f'{TPL} keyword.operator.assignment.go-template',
    'GO_TEMPLATE_NUMBER':      TPL,
    'GO_TEMPLATE_PUNCTUATION': TPL,
    'GO_TEMPLATE_COMMA':       TPL,
    'GO_TEMPLATE_BRACES':      TPL,
    'GO_TEMPLATE_PARENTHESES': TPL,
    'GO_TEMPLATE_BAD_TOKEN':   f'{TPL} invalid.illegal.go-template',
    'GO_TEMPLATE_BACKGROUND':  ('=', 'DEFAULT_TEMPLATE_LANGUAGE_COLOR'),
}

NOTES = {
    'GO_BAD_TOKEN': 'explicit: invalid.illegal (no sample produces a bad token)',
    'GO_COMMENT_KEYWORD': 'directives (//go:build, //go:generate) are plain comment text in VS Code',
    'GO_COMMENT_REFERENCE': 'doc links [pkg.Name] are plain comment text in VS Code',
    'GO_BUILD_TAG': 'build-constraint tags/parens/operators are inside the comment in VS Code',
    'GO_TAG_KEY': 'struct tags are one string.quoted.raw token in VS Code; key/colon/value/text all string',
    'GO_METHOD_RECEIVER': 'usage (plain); VS Code colours only the declaration (variable.parameter)',
    'GO_FUNCTION_PARAMETER': 'usage (plain); VS Code colours only the declaration (variable.parameter)',
    'GO_LOCAL_CONSTANT': 'usage (plain); only the declaration is variable.other.constant. Same for package constants',
    'GO_SHADOWING_VARIABLE': 'the shadowing declaration (variable.other.assignment)',
    'GO_IDENTIFIER': 'plain identifier usage (variable.other.go)',
    'COMMENT': 'go.mod comment key (VgoSyntaxHighlightingColors names it plain "COMMENT"); explicit golang.go go.mod stack',
    'VGO_GO_KEYWORD': 'explicit: golang.go go.mod grammar (not installed here); all directives are keyword.go.mod',
    'VGO_GO_VERSION': 'explicit: `go 1.22` version has no v prefix -> string.unquoted in the go.mod grammar',
    'VGO_MODULE_VERSION': 'explicit: semver vX.Y.Z -> constant.language.go.mod',
    'com.plan9.INSTRUCTION': 'explicit: quillaja.goasm grammar (scope source.x86); mnemonics are entity.name.function',
    'com.plan9.PSEUDO_INSTRUCTION': 'explicit: goasm colours TEXT/DATA as storage.type but has no rule for PCDATA/FUNCDATA; storage.type for all pseudo-ops',
    'com.plan9.STRING': 'explicit: goasm\'s string rule includes two undefined repository rules, so vscode-textmate drops it; $"..." strings are plain (verified by tokenising the GoLand demo with goasm.tmLanguage.xml)',
    'com.plan9.IDENTIFIER': 'explicit: symbols/operators/parens are unscoped in goasm',
    'GO_TEMPLATE_DELIMITER': 'explicit: jinliming2 injection grammar, {{ }} are punctuation.section.embedded inside meta.embedded.go-template',
    'GO_TEMPLATE_IDENTIFIER': 'IntelliJ identifier covers fields (.Name) and functions (printf); field chain (variable.sub.property) chosen',
    'GO_TEMPLATE_NUMBER': 'explicit: the go-template grammar does not scope numbers/commas/parens (plain)',
}
