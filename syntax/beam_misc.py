"""BEAM languages and leftover plugin keys: Elixir (org.elixir_lang), Erlang (org.jetbrains.erlang),
Kubernetes YAML annotator colours, Astro/Svelte keys not in js.py, and HTTP Client cookie files.

VS Code has no built-in Elixir or Erlang grammar. Their stacks are explicit, taken by tokenising
real code with the de-facto extensions' grammars: elixir-lsp/vscode-elixir-ls `syntaxes/elixir.json`
(scope source.elixir) and erlang-ls/vscode `grammar/Erlang.plist` (scope source.erlang).
ElixirLS' semanticTokenScopes map to the same TextMate scopes, so TextMate stacks are used as-is.
Svelte (svelte.svelte-vscode not installed): stack from sveltejs/language-tools svelte.tmLanguage.src.yaml.
Shell (BASH.*), HTTP request keys, Vue and Angular keys are already complete in markup.py / js.py."""
import string

SAMPLES = {
    # Kubernetes plugin annotates values of k8s manifests (YAML) on top of the YAML highlighter.
    'k8s': ('source.yaml', '''apiVersion: v1
kind: Pod
metadata:
  name: demo
spec:
  containers:
    - name: demo
      imagePullPolicy: Always
      ports:
        - containerPort: 8080
          protocol: TCP
      volumeMounts:
        - mountPath: /data
          readOnly: false
'''),
    'astro': ('source.astro', '''---
import Layout from "../layouts/Layout.astro";
const title = "Hi";
---
<Layout title={title}><h1>{title}</h1></Layout>
'''),
}

EX = 'source.elixir'
ERL = 'source.erlang'
ERL_FN = f'{ERL} meta.function.erlang'
ERL_TYPE = f'{ERL} meta.directive.erlang meta.type.erlang meta.function-call.erlang entity.name.function.erlang'

MAP = {
    # ---- Elixir (explicit, vscode-elixir-ls grammar) ----
    'ELIXIR_ALIAS':                          f'{EX} entity.name.type.module.elixir',
    'ELIXIR_ATOM':                           f'{EX} constant.language.symbol.elixir',
    'ELIXIR_BRACES':                         f'{EX} punctuation.section.scope.elixir',
    'ELIXIR_BRACKET':                        f'{EX} punctuation.section.array.elixir',
    'ELIXIR_PARENTHESES':                    f'{EX} punctuation.section.function.elixir',
    'ELIXIR_COMMA':                          f'{EX} punctuation.separator.object.elixir',
    'ELIXIR_DOT':                            f'{EX} punctuation.separator.method.elixir',
    'ELIXIR_SEMICOLON':                      f'{EX} punctuation.separator.statement.elixir',
    'ELIXIR_OPERATION_SIGN':                 f'{EX} keyword.operator.other.elixir',
    'ELIXIR_BIT':                            f'{EX} keyword.operator.other.elixir',
    'ELIXIR_MAP':                            f'{EX} punctuation.definition.map.elixir',
    'ELIXIR_STRUCT':                         f'{EX} punctuation.definition.map.elixir',
    'ELIXIR_CHAR_LIST':                      f'{EX} string.quoted.single.elixir',
    'ELIXIR_CHAR_TOKEN':                     f'{EX} constant.numeric.elixir',
    'ELIXIR_STRING':                         f'{EX} string.quoted.double.elixir',
    'ELIXIR_VALID_ESCAPE_SEQUENCE':          f'{EX} string.quoted.double.elixir constant.character.escape.elixir',
    'ELIXIR_EXPRESSION_SUBSTITUTION_MARK':   f'{EX} string.quoted.double.elixir meta.embedded.line.elixir punctuation.section.embedded.elixir',
    'ELIXIR_INTERPOLATION':                  ('=', 'ELIXIR_EXPRESSION_SUBSTITUTION_MARK'),
    'ELIXIR_SIGIL':                          f'{EX} string.quoted.double.interpolated.elixir',
    'ELIXIR_COMMENT':                        f'{EX} comment.line.number-sign.elixir',
    'ELIXIR_DOCUMENTATION_MODULE_ATTRIBUTE': f'{EX} comment.documentation.heredoc.elixir',
    'ELIXIR_DOCUMENTATION_TEXT':             f'{EX} comment.documentation.heredoc.elixir',
    'ELIXIR_DECIMAL':                        f'{EX} constant.numeric.elixir',
    'ELIXIR_VALID_DIGIT':                    f'{EX} constant.numeric.elixir',
    'ELIXIR_WHOLE_NUMBER_BASE':              f'{EX} constant.numeric.elixir',
    'ELIXIR_INVALID_DIGIT':                  EX,
    'ELIXIR_OBSOLETE_WHOLE_NUMBER_BASE':     EX,
    'ELIXIR_BAD_CHARACTER':                  EX,
    'ELIXIR_KEYWORD':                        f'{EX} keyword.control.elixir',
    'ELIXIR_MACRO_CALL':                     f'{EX} keyword.control.elixir',
    'ELIXIR_KERNEL_MACRO':                   ('=', 'ELIXIR_MACRO_CALL'),
    'ELIXIR_PREDEFINED':                     f'{EX} keyword.control.elixir',
    'ELIXIR_FUNCTION_CALL':                  f'{EX} entity.name.function.call.local.elixir',
    'ELIXIR_FUNCTION_DECLARATION':           f'{EX} meta.function.definition.elixir entity.name.function.elixir',
    'ELIXIR_MACRO_DECLARATION':              f'{EX} meta.function.definition.elixir entity.name.function.elixir',
    'ELIXIR_MODULE_ATTRIBUTE':               f'{EX} variable.other.constant.elixir',
    'ELIXIR_SPECIFICATION':                  f'{EX} meta.type.definition.elixir entity.name.function.typespec.elixir',
    'ELIXIR_CALLBACK':                       f'{EX} meta.type.definition.elixir entity.name.function.typespec.elixir',
    'ELIXIR_TYPE':                           f'{EX} meta.type.definition.elixir entity.name.function.typespec.elixir',
    'ELIXIR_TYPE_PARAMETER':                 f'{EX} meta.type.definition.elixir variable.other.readwrite.elixir',
    'ELIXIR_IDENTIFIER':                     f'{EX} variable.other.readwrite.elixir',
    'ELIXIR_VARIABLE':                       f'{EX} variable.other.readwrite.elixir',
    'ELIXIR_PARAMETER':                      f'{EX} meta.function.definition.elixir variable.other.readwrite.elixir',
    'ELIXIR_IGNORED_VARIABLE':               f'{EX} meta.function.definition.elixir comment.unused.elixir',

    # ---- Erlang (explicit, erlang-ls grammar) ----
    'ERL_COMMENT':        f'{ERL} comment.line.percentage.erlang',
    'ERL_DOC_TAG':        f'{ERL} comment.line.percentage.erlang',
    'ERL_STRING':         f'{ERL_FN} string.quoted.double.erlang',
    'ERL_ILLEGAL':        f'{ERL} string.quoted.double.erlang invalid.illegal.string.erlang',
    'ERL_NUMBER':         f'{ERL_FN} constant.numeric.integer.decimal.erlang',
    'ERL_KEYWORD':        f'{ERL_FN} keyword.control.erlang',
    'ERL_OP_SIGN':        f'{ERL_FN} keyword.operator.symbolic.erlang',
    'ERL_PARENTHESES':    f'{ERL_FN} meta.function-call.erlang punctuation.definition.parameters.begin.erlang',
    'ERL_BRACES':         f'{ERL_FN} meta.structure.tuple.erlang punctuation.definition.tuple.begin.erlang',
    'ERL_BRACKETS':       f'{ERL_FN} meta.structure.list.erlang punctuation.definition.list.begin.erlang',
    'ERL_ATOM':           f'{ERL_FN} constant.other.symbol.unquoted.erlang',
    'ERL_MACRO':          f'{ERL_FN} meta.macro-usage.erlang entity.name.function.macro.erlang',
    'ERL_VARIABLES':      f'{ERL_FN} variable.other.erlang',
    'ERL_RECORDS':        f'{ERL_FN} meta.record-usage.erlang entity.name.type.class.record.erlang',
    'ERL_FUNCTION':       f'{ERL_FN} entity.name.function.definition.erlang',
    'ERL_FUNCTION_CALL':  f'{ERL_FN} meta.function-call.erlang entity.name.function.erlang',
    'ERL_GUARD':          f'{ERL_FN} meta.function-call.erlang entity.name.function.guard.erlang',
    'ERL_MODULE_REF':     f'{ERL_FN} meta.function-call.erlang entity.name.type.class.module.erlang',
    'ERL_ATTRIBUTE':      f'{ERL} meta.directive.module.erlang keyword.control.directive.module.erlang',
    'ERL_TYPE':           ERL_TYPE,
    'ERL_BUILT_IN_TYPE':  ERL_TYPE,
    'ERL_SPEC':           ERL_TYPE,
    'ERL_CALLBACK':       ERL_TYPE,

    # ---- Kubernetes (annotator colours on YAML values; key = 'com.intellij.kubernetes.' + name) ----
    'com.intellij.kubernetes.gvk':     ('k8s', 'Pod'),
    'com.intellij.kubernetes.enum':    ('k8s', 'Always'),
    'com.intellij.kubernetes.number':  ('k8s', '8080'),
    'com.intellij.kubernetes.boolean': ('k8s', 'false'),

    # ---- Astro / Svelte ----
    'ASTRO.FRONTMATTER_SEPARATOR': ('astro', '---'),
    'SVELTE_KEYWORD': 'source.svelte meta.special.if.svelte meta.special.start.svelte keyword.control.conditional.svelte',

    # ---- HTTP Client cookie file (http-client.cookies) ----
    'COOKIE_TOKEN':         ('=', 'DEFAULT_IDENTIFIER'),
    'COOKIE_COMMENT':       'source.http comment.line.sharp.http',
    'COOKIE_BAD_CHARACTER': 'source.http invalid.illegal.http',
}

# ELIXIR_SIGIL_{LOWER,UPPER}_<letter>: lowercase sigils interpolate, uppercase are literal; r/R are regexes,
# c/C charlists (string.quoted.single), as vscode-elixir-ls tokenises them.
for c in string.ascii_lowercase:
    MAP[f'ELIXIR_SIGIL_LOWER_{c.upper()}'] = f'{EX} ' + {
        'r': 'string.regexp.interpolated.elixir', 'c': 'string.quoted.single.elixir'}.get(c, 'string.quoted.double.interpolated.elixir')
for c in string.ascii_uppercase:
    MAP[f'ELIXIR_SIGIL_UPPER_{c}'] = f'{EX} ' + {
        'R': 'string.regexp.literal.elixir', 'C': 'string.quoted.single.elixir'}.get(c, 'string.quoted.double.literal.elixir')

NOTES = {
    'ELIXIR_ALIAS': 'explicit (vscode-elixir-ls grammar; no VS Code built-in Elixir grammar). All ELIXIR_* stacks are explicit',
    'ELIXIR_MACRO_CALL': 'macro calls are mostly Kernel macros (if/case/raise/and/quote) = keyword.control in VS Code',
    'ELIXIR_PREDEFINED': 'Kernel calls: if/case/raise/def are keyword.control in VS Code (is_nil-style guards are function calls there); chose keyword',
    'ELIXIR_TYPE': 'type name in @type and parenthesised type calls (integer(), String.t()) are entity.name.function; bare type names in specs (integer) are plain in VS Code',
    'ELIXIR_IGNORED_VARIABLE': 'VS Code scopes _var as comment.unused (comment colour)',
    'ELIXIR_INVALID_DIGIT': 'vscode-elixir-ls leaves malformed numbers (0b012, 0B01) unscoped -> plain; same for OBSOLETE_WHOLE_NUMBER_BASE, BAD_CHARACTER',
    'ELIXIR_INTERPOLATION': 'legacy key still set by bundled schemes; same as #{ mark',
    'ELIXIR_KERNEL_MACRO': 'legacy key still set by bundled schemes; same as macro call',
    'ERL_ATOM': 'explicit (erlang-ls grammar; no VS Code built-in Erlang grammar). All ERL_* stacks are explicit',
    'ERL_DOC_TAG': 'erlang-ls grammar does not scope edoc tags; whole line is comment',
    'ERL_TYPE': 'types in -type/-spec/-callback are function-call-like entity.name.function in erlang-ls grammar',
    'com.intellij.kubernetes.gvk': 'apiVersion/kind values are plain YAML scalars in VS Code (same for enum values)',
    'SVELTE_KEYWORD': 'explicit (svelte grammar not installed): {#if} keyword from svelte.tmLanguage',
    'COOKIE_COMMENT': 'explicit: no VS Code grammar for http-client.cookies; same root as HTTP Client keys',
}
