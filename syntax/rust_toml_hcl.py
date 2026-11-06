"""Rust (RustRover / com.jetbrains.rust: org.rust.*), TOML (org.toml.*), HCL / Terraform (HCL.*) and the
Terraform interpolation / template language (TIL.*).

Rust: VS Code's built-in rust grammar + rust-analyzer semantic tokens. rust-analyzer's
contributes.semanticTokenScopes (editors/code/package.json) override the standard fallback table for
identifiers, so identifier-like keys are explicit `source.rust <semantic scope>` stacks; keywords, literals,
comments and punctuation stay TextMate (sample-based), because rust-analyzer's punctuation/operator/escape
token types have no scope mapping and VS Code keeps the TextMate colour for them.
TOML: Even Better TOML (tamasfe.even-better-toml) grammar, not bundled with VS Code -> explicit stacks taken
from tokenising its toml.tmLanguage.json.
HCL / Terraform: HashiCorp Terraform extension (hashicorp.terraform) grammar, not bundled -> explicit stacks
from tokenising its terraform.tmGrammar.json; identifier-like keys use terraform-ls semantic token scopes
(hcl-attrName -> variable.other.property, hcl-blockType -> entity.name.type, hcl-blockLabel ->
variable.other.enummember, hcl-referenceStep -> variable.other.readwrite, hcl-functionName -> support.function).
"""

SAMPLES = {
    'rust': ('source.rust', r'''#[macro_use]
extern crate log;

use std::collections::HashMap;

/// Docs with `code`, *emphasis* and **strong**
/// # Heading
/// [Rust](https://www.rust-lang.org/)
#[derive(Debug, Clone)]
pub struct Point<'a, T: Copy, const N: usize> {
    pub x: f64,
    name: &'a str,
    data: [T; N],
}

impl<'a, T: Copy, const N: usize> Point<'a, T, N> {
    fn new(x: f64, mut count: i64) -> Self {
        let value = x * 2.0;
        let mut total = 0;
        total += 1;
        let s = String::from("hi\n\q");
        let c = 'c';
        let f = |a: i32| a + 1;
        println!("{} {name:>8}", value, name = s);
        self.translate(1.0).unwrap()?;
        unsafe { COUNTER += 1; }
        Self { x: value, name: "", data: [0; N] }
    }
}

macro_rules! square {
    ($x:expr, $($rest:ident),*) => { $x * $x };
}

// line comment
/* block comment */
fn main() { let v = square!(3, a, b); }
'''),
}

R = 'source.rust '
TOML = 'source.toml '
TF = 'source.hcl.terraform meta.block.hcl '
TIL = 'source.hcl.terraform meta.block.hcl string.quoted.double.hcl meta.interpolation.hcl '

MAP = {
    # ---- Rust: identifiers (rust-analyzer semantic tokens) ----
    'org.rust.VARIABLE':                  R + 'variable.other.rust',                     # variable
    'org.rust.MUT_BINDING':               R + 'variable.other.rust markup.underline',    # variable.mutable (*.mutable)
    'org.rust.FIELD':                     R + 'variable.other.property',                 # property
    'org.rust.CONSTANT':                  R + 'variable.other.constant.rust',            # const (variable.constant)
    'org.rust.STATIC':                    R + 'variable.other.rust',                     # static -> variable
    'org.rust.MUT_STATIC':                R + 'variable.other.rust markup.underline',    # static.mutable
    'org.rust.SELF_EXPRESSION':           R + 'keyword.other.rust',                      # selfKeyword -> keyword
    'org.rust.SELF_PARAMETER':            R + 'keyword.other.rust',
    'org.rust.MUT_SELF_PARAMETER':        R + 'keyword.other.rust markup.underline',
    'org.rust.FUNCTION':                  R + 'entity.name.function.rust',               # function
    'org.rust.METHOD':                    R + 'entity.name.function.rust',               # method
    'org.rust.TRAIT_METHOD':              R + 'entity.name.function.rust',
    'org.rust.ASSOC_FUNCTION':            R + 'entity.name.function.rust',
    'org.rust.ASSOC_TRAIT_FUNCTION':      R + 'entity.name.function.rust',
    'org.rust.FUNCTION_CALL':             R + 'entity.name.function.rust',
    'org.rust.METHOD_CALL':               R + 'entity.name.function.rust',
    'org.rust.TRAIT_METHOD_CALL':         R + 'entity.name.function.rust',
    'org.rust.ASSOC_FUNCTION_CALL':       R + 'entity.name.function.rust',
    'org.rust.ASSOC_TRAIT_FUNCTION_CALL': R + 'entity.name.function.rust',
    'org.rust.MACRO':                     R + 'entity.name.function.preprocessor',       # macro (call name; std fallback)
    'org.rust.MACRO_EXCL':                R + 'entity.name.function.macro.rust',         # macroBang
    'org.rust.MACRO_IDENTIFIER':          R + 'entity.name.function.preprocessor',       # macro (declaration)
    'org.rust.PARAMETER':                 R + 'variable.parameter',                      # parameter (std fallback)
    'org.rust.MUT_PARAMETER':             R + 'variable.parameter markup.underline',     # parameter.mutable
    'org.rust.LIFETIME':                  R + 'storage.modifier.lifetime.rust',          # lifetime
    'org.rust.TYPE_PARAMETER':            R + 'entity.name.type.parameter',              # typeParameter (std)
    'org.rust.CONST_PARAMETER':           R + 'constant.other.caps.rust',                # constParameter
    'org.rust.PRIMITIVE_TYPE':            R + 'support.type.primitive.rust',             # builtinType
    'org.rust.STRUCT':                    R + 'entity.name.type.struct.rust',            # struct
    'org.rust.UNION':                     R + 'entity.name.type.union.rust',             # union
    'org.rust.TRAIT':                     R + 'entity.name.type.trait.rust',             # interface
    'org.rust.ENUM':                      R + 'entity.name.type.enum.rust',              # enum
    'org.rust.ENUM_VARIANT':              R + 'variable.other.enummember',               # enumMember (std)
    'org.rust.TYPE_ALIAS':                R + 'entity.name.type.declaration.rust',       # typeAlias
    'org.rust.CRATE':                     R + 'entity.name.namespace',                   # namespace.crateRoot
    'org.rust.MODULE':                    R + 'entity.name.namespace',                   # namespace
    'org.rust.ATTRIBUTE':                 R + 'meta.attribute.rust',                     # attribute
    'org.rust.FORMAT_PARAMETER':          R + 'string.quoted.double.rust meta.interpolation.rust punctuation.definition.interpolation.rust punctuation.section.embedded.rust',  # formatSpecifier over TextMate
    'org.rust.FORMAT_SPECIFIER':          R + 'variable.other.rust',                     # {name} identifier -> variable
    'org.rust.MACRO_RULES':               R + 'keyword.other.rust',                      # macro_rules -> keyword

    # ---- Rust: TextMate (sample-based) ----
    'org.rust.KEYWORD':                   ('rust', 'fn new'),
    'org.rust.KEYWORD_UNSAFE':            ('rust', 'unsafe'),
    'org.rust.CHAR':                      ('rust', "'c'", 1),
    'org.rust.NUMBER':                    ('rust', '2.0'),
    'org.rust.STRING':                    ('rust', '"hi'),
    'org.rust.VALID_STRING_ESCAPE':       ('rust', r'\n\q'),
    'org.rust.INVALID_STRING_ESCAPE':     ('rust', r'\q'),
    'org.rust.BLOCK_COMMENT':             ('rust', '/* block'),
    'org.rust.EOL_COMMENT':               ('rust', '// line'),
    'org.rust.DOC_COMMENT':               ('rust', ' Docs with'),
    'org.rust.DOC_HEADING':               ('rust', '# Heading'),
    'org.rust.DOC_LINK':                  ('rust', '[Rust]'),
    'org.rust.DOC_EMPHASIS':              ('rust', '*emphasis*'),
    'org.rust.DOC_STRONG':                ('rust', '**strong**'),
    'org.rust.DOC_CODE':                  ('rust', '`code`'),
    'org.rust.BRACES':                    ('rust', '{\n    pub x'),
    'org.rust.BRACKETS':                  ('rust', '[T; N]'),
    'org.rust.PARENTHESES':               ('rust', '(x: f64'),
    'org.rust.SEMICOLON':                 ('rust', ';\n        let mut'),
    'org.rust.DOT':                       ('rust', '.translate'),
    'org.rust.COMMA':                     ('rust', ', T: Copy, const N: usize> {'),
    'org.rust.OPERATORS':                 ('rust', '* 2.0'),
    'org.rust.OVERLOADED_OPERATOR':       ('rust', '+= 1;\n        let s'),
    'org.rust.Q_OPERATOR':                ('rust', '?;'),
    'org.rust.CLOSURE':                   ('rust', '|a: i32|'),
    'org.rust.MACRO_DOLLAR':              ('rust', '$x:expr'),
    'org.rust.MACRO_META_VAR_IDENTIFIER': ('rust', 'x:expr'),
    'org.rust.MACRO_COLON':               ('rust', ':expr'),
    'org.rust.MACRO_BINDING_IDENTIFIER':  ('rust', 'expr,'),
    'org.rust.MACRO_GROUP_ELEMENTS':      ('rust', '($rest'),

    # ---- TOML (Even Better TOML grammar; explicit) ----
    'org.toml.KEY':                   TOML + 'meta.entry.toml support.type.property-name.toml',
    'org.toml.COMMENT':               TOML + 'comment.line.number-sign.toml',
    'org.toml.BOOLEAN':               TOML + 'constant.language.boolean.toml',
    'org.toml.NUMBER':                TOML + 'constant.numeric.integer.toml',
    'org.toml.DATE':                  TOML + 'constant.other.time.datetime.offset.toml',
    'org.toml.STRING':                TOML + 'string.quoted.single.basic.line.toml',
    'org.toml.VALID_STRING_ESCAPE':   TOML + 'string.quoted.single.basic.line.toml constant.character.escape.toml',
    'org.toml.INVALID_STRING_ESCAPE': TOML + 'string.quoted.single.basic.line.toml invalid.illegal.escape.toml',

    # ---- HCL / Terraform (HashiCorp grammar + terraform-ls semantic tokens; explicit) ----
    'HCL.BRACKETS':               TF + 'punctuation.section.brackets.begin.hcl',
    'HCL.BRACES':                 TF + 'punctuation.section.block.begin.hcl',
    'HCL.COMMA':                  TF + 'punctuation.separator.hcl',
    'HCL.OPERATION_SIGN':         TF + 'keyword.operator.arithmetic.hcl',
    'HCL.NUMBER':                 TF + 'constant.numeric.integer.hcl',
    'HCL.STRING':                 TF + 'string.quoted.double.hcl',
    'HCL.KEYWORD':                TF + 'constant.language.hcl',
    'HCL.LINE_COMMENT':           'source.hcl.terraform comment.line.double-slash.hcl',
    'HCL.BLOCK_COMMENT':          'source.hcl.terraform comment.block.hcl',
    'HCL.IDENTIFIER':             'source.hcl.terraform variable.other.readwrite',          # hcl-referenceStep
    'HCL.PROPERTY_KEY':           'source.hcl.terraform variable.other.property',           # hcl-attrName
    'HCL.BLOCK_FIRST_TYPE_KEY':   'source.hcl.terraform entity.name.type',                  # hcl-blockType
    'HCL.BLOCK_ONLY_NAME_KEY':    'source.hcl.terraform entity.name.type',                  # hcl-blockType
    'HCL.BLOCK_SECOND_TYPE_KEY':  'source.hcl.terraform variable.other.enummember',         # hcl-blockLabel
    'HCL.BLOCK_TYPES_KEY':        'source.hcl.terraform variable.other.enummember',         # hcl-blockLabel
    'HCL.BLOCK_NAME_KEY':         'source.hcl.terraform variable.other.enummember',         # hcl-blockLabel
    'HCL.VALID_ESCAPE':           TF + 'string.quoted.double.hcl constant.character.escape.hcl',
    'HCL.INVALID_ESCAPE':         TF + 'string.quoted.double.hcl',

    # ---- TIL: Terraform interpolation (${...}) / template language (explicit) ----
    'TIL.PARENS':                     TIL + 'punctuation.section.parens.begin.hcl',
    'TIL.BRACES':                     TIL + 'keyword.other.interpolation.begin.hcl',
    'TIL.BRACKETS':                   TIL + 'punctuation.section.brackets.begin.hcl',
    'TIL.COMMA':                      TIL + 'punctuation.separator.hcl',
    'TIL.DOT':                        TIL + 'keyword.operator.accessor.hcl',
    'TIL.OPERATOR':                   TIL + 'keyword.operator.arithmetic.hcl',
    'TIL.NUMBER':                     TIL + 'constant.numeric.integer.hcl',
    'TIL.STRING':                     TIL + 'string.quoted.double.hcl',
    'TIL.KEYWORD':                    TIL + 'constant.language.hcl',
    'TIL.IDENTIFIER':                 'source.hcl.terraform variable.other.readwrite',      # hcl-referenceStep
    'TIL.PREDEFINED_SCOPE':           'source.hcl.terraform variable.other.readwrite',      # hcl-referenceStep
    'TIL.RESOURCE_TYPE_REFERENCE':    'source.hcl.terraform variable.other.readwrite',      # hcl-referenceStep
    'TIL.RESOURCE_INSTANCE_REFERENCE': 'source.hcl.terraform variable.other.readwrite',     # hcl-referenceStep
    'TIL.PROPERTY_REFERENCE':         'source.hcl.terraform variable.other.readwrite',      # hcl-referenceStep
    'TIL.VALID_ESCAPE':               TIL + 'string.quoted.double.hcl constant.character.escape.hcl',
    'TIL.INVALID_ESCAPE':             TIL + 'string.quoted.double.hcl',
    'TERRAFORM_TEMPLATE_BACKGROUND':  ('=', 'DEFAULT_TEMPLATE_LANGUAGE_COLOR'),
}

_SEM = 'explicit: rust-analyzer semantic token scope (semanticTokenScopes / standard fallback)'
NOTES = {
    'org.rust.MUT_BINDING': 'explicit: rust-analyzer variable.mutable; "*.mutable" -> markup.underline, so VS Code underlines mutable bindings (fg stays the variable colour)',
    'org.rust.MUT_STATIC': 'explicit: rust-analyzer static.mutable -> variable colour + markup.underline',
    'org.rust.MUT_PARAMETER': 'explicit: rust-analyzer parameter.mutable -> variable.parameter + markup.underline',
    'org.rust.MUT_SELF_PARAMETER': 'explicit: rust-analyzer selfKeyword.mutable -> keyword + markup.underline',
    'org.rust.SELF_EXPRESSION': 'explicit: rust-analyzer selfKeyword (superType keyword) -> keyword.other.rust (TextMate alone would give variable.language)',
    'org.rust.SELF_PARAMETER': 'explicit: rust-analyzer selfKeyword -> keyword.other.rust',
    'org.rust.PRIMITIVE_TYPE': 'explicit: rust-analyzer builtinType -> support.type.primitive.rust (TextMate alone: entity.name.type.numeric)',
    'org.rust.LIFETIME': 'explicit: rust-analyzer lifetime -> storage.modifier.lifetime.rust (TextMate alone: entity.name.type.lifetime)',
    'org.rust.FORMAT_PARAMETER': 'explicit: rust-analyzer formatSpecifier ({ } : < etc.) -> punctuation.section.embedded.rust; GitHub Light/Dark (classic) have no rule for it, so VS Code keeps the TextMate colour (string interpolation punctuation): the stack carries the TextMate parents so both cases resolve right',
    'org.rust.FORMAT_SPECIFIER': 'explicit: IntelliJ paints the name and the width/precision inside {} with this key; rust-analyzer emits the name as variable (variable.other.rust) and digits as number. Picked the inline-argument name ({foo}), the more common case',
    'org.rust.MACRO_RULES': 'explicit: rust-analyzer emits macro_rules as keyword -> keyword.other.rust (TextMate alone: entity.name.function.macro.rules)',
    'org.rust.MACRO': 'explicit: IntelliJ paints name+!; rust-analyzer emits the name as macro (std fallback entity.name.function.preprocessor) and ! as macroBang (entity.name.function.macro.rust), same colour',
    'org.rust.MACRO_EXCL': 'explicit: the ! of macro_rules! -> rust-analyzer macroBang -> entity.name.function.macro.rust',
    'org.rust.CRATE': 'explicit: rust-analyzer namespace (crateRoot) -> entity.name.namespace',
    'org.rust.MACRO_IDENTIFIER': 'explicit: rust-analyzer macro (declaration) -> standard fallback entity.name.function.preprocessor',
    'org.rust.INVALID_STRING_ESCAPE': 'rust-analyzer invalidEscapeSequence has no scope and the grammar scopes it as an escape, so VS Code shows it like a valid escape',
    'org.rust.DOC_HEADING': 'VS Code has no markdown highlighting in Rust doc comments: whole line is comment.line.documentation',
    'org.rust.DOC_LINK': 'plain doc comment in VS Code (no markdown injection)',
    'org.rust.DOC_EMPHASIS': 'plain doc comment in VS Code (no markdown injection)',
    'org.rust.DOC_STRONG': 'plain doc comment in VS Code (no markdown injection)',
    'org.rust.DOC_CODE': 'plain doc comment in VS Code (inline code not injected)',
    'org.rust.ATTRIBUTE': 'explicit: rust-analyzer attribute -> meta.attribute.rust (no theme rule: default foreground)',
    'org.toml.KEY': 'explicit: Even Better TOML grammar (not bundled); table-header keys (support.type.property-name.table) resolve to the same colour',
    'org.toml.NUMBER': 'explicit: Even Better TOML grammar (not bundled)',
    'org.toml.DATE': 'explicit: Even Better TOML grammar (not bundled)',
    'HCL.KEYWORD': 'explicit (HashiCorp grammar): true/false/null as constant.language; terraform-ls hcl-bool (keyword.control) only applies to schema-known bool attributes in .tf, so the grammar scope serves all HCL files',
    'HCL.IDENTIFIER': 'explicit: terraform-ls hcl-referenceStep -> variable.other.readwrite',
    'HCL.PROPERTY_KEY': 'explicit: terraform-ls hcl-attrName -> variable.other.property',
    'HCL.BLOCK_FIRST_TYPE_KEY': 'explicit: terraform-ls hcl-blockType -> entity.name.type',
    'HCL.BLOCK_SECOND_TYPE_KEY': 'explicit: terraform-ls hcl-blockLabel -> variable.other.enummember',
    'HCL.INVALID_ESCAPE': 'explicit: HashiCorp grammar leaves invalid escapes as plain string text',
    'TIL.BRACES': 'explicit: ${ } interpolation delimiters (keyword.other.interpolation) in the HashiCorp grammar',
    'TIL.IDENTIFIER': 'explicit: terraform-ls hcl-referenceStep -> variable.other.readwrite (resolved without the enclosing string scope, as semantic tokens are)',
    'TIL.INVALID_ESCAPE': 'explicit: HashiCorp grammar leaves invalid escapes as plain string text',
}
for _k, _v in MAP.items():
    if _k.startswith('org.rust.') and isinstance(_v, str) and _k not in NOTES:
        NOTES[_k] = _SEM
