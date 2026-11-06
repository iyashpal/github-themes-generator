"""Scala (org.intellij.scala: Scala 2/3, ScalaDoc, Scala CLI `//> using` directives, Scala XML literals,
ScalaTest), Dart (Dart plugin), and Android Studio's own languages: Smali, ProGuard/R8 rules,
Room SQL (AndroidSql), Gradle Declarative (.dcl), Wear OS Watch Face Format expressions and the
Compose @Preview device spec.

Scala: VS Code has no built-in grammar; the de-facto one is scala-lang/vscode-scala-syntax (source.scala),
so syntax keys are explicit stacks in its scopes. Identifiers follow Metals' semantic tokens
(PcSemanticTokensProvider: value parameter -> parameter, type param -> typeParameter, trait -> interface,
class/object -> class, type alias -> type, var -> variable, accessor (field val/var) -> variable,
def -> method, other vals -> variable.readonly) through VS Code's fallback table.
Dart: VS Code's built-in dart grammar (samples) for tokens; identifiers follow the Dart analysis server's
semantic tokens (analysis_server lsp/semantic_tokens/mapping.dart) with Dart-Code's semanticTokenScopes
(annotation -> variable, source -> meta.embedded, string.escape -> constant.character.escape).
AIDL and RenderScript have no keys of their own (AIDL's highlighter uses DefaultLanguageHighlighterColors).
"""

SAMPLES = {
    'dart': ('source.dart', r'''library libraryName;
import "dart:html" as html;

// Comment.
dynamic topLevelVariable = "Escape sequences: \n \xFF";
var other = "Invalid: \xZZ";

void topLevelFunction(dynamicParameter) {
  num localVar = 1.5 + 42;
  label: while (true) { if (identifier) break label; }
  var list = [566];
  var sym = #Enum.EnumConstant;
}

/* block comment */
class Foo<K, V> {
  /// documentation for [Enum]
  static var staticField = 1;
  @deprecated Foo.constructor(this.instanceField) { instanceMethod(); }
  static staticMethod() => staticField.unresolved();
  Map<String, int> m = {'a': 1};
}
'''),
    'roomsql': ('source.sql', r'''-- Room DAO query
SELECT * FROM users WHERE id = :userId AND name LIKE 'A%' LIMIT 10;
/* block */
INSERT INTO logs (msg, ts) VALUES ('x', CURRENT_TIMESTAMP);
'''),
}

SC = 'source.scala'
DT = 'source.dart'
SM = 'source.smali'
PG = 'source.proguard'
KT = 'source.kotlin'

MAP = {
    # ================= Scala: TextMate tokens (vscode-scala-syntax scopes, explicit) =================
    'Scala Keyword':                 f'{SC} keyword.declaration.scala',
    'Scala Number':                  f'{SC} constant.numeric.scala',
    'Scala String':                  f'{SC} string.quoted.double.scala',
    'Scala Valid escape in string':  f'{SC} string.regexp',
    'Scala Invalid escape in string': f'{SC} string.regexp',
    'Scala Line comment':            f'{SC} comment.line.double-slash.scala',
    'Scala Block comment':           f'{SC} comment.block.scala',
    'ScalaDoc comment':              f'{SC} comment.block.documentation.scala',
    'ScalaDoc comment tag':          f'{SC} comment.block.documentation.scala keyword.other.documentation.scaladoc.scala',
    'ScalaDoc @param value':         f'{SC} variable.other.constant',
    'ScalaDoc html tag':             f'{SC} comment.block.documentation.scala',
    'ScalaDoc wiki syntax elements': f'{SC} comment.block.documentation.scala',
    'ScalaDoc html escape sequences': f'{SC} comment.block.documentation.scala',
    'ScalaDoc comment markup':       f'{SC} comment.block.documentation.scala',
    'ScalaDoc list item head':       f'{SC} comment.block.documentation.scala',
    'Scala Brackets':                f'{SC} meta.bracket.scala',
    'Scala Parentheses':             f'{SC} meta.bracket.scala',
    'Scala Braces':                  f'{SC} punctuation.section.block.begin.scala',
    'Scala Colon':                   f'{SC} meta.colon.scala',
    'Scala Semicolon':               SC,
    'Scala Dot':                     SC,
    'Scala Comma':                   SC,
    'Scala Assign':                  f'{SC} keyword.operator.comparison.scala',
    'Scala Arrow':                   f'{SC} keyword.operator.scala',
    'Scala Bad character':           SC,
    'Interpolated String Injection': f'{SC} keyword',
    # Scala XML literals
    'Scala XML tag':                 f'{SC} meta.tag.xml punctuation.definition.tag.xml',
    'Scala XML tag name':            f'{SC} meta.tag.xml entity.name.tag.xml',
    'Scala XML tag data':            f'{SC} meta.scope.between-tag-pair.xml',
    'Scala XML attribute name':      f'{SC} meta.tag.xml entity.other.attribute-name.localname.xml',
    'Scala XML attribute value':     f'{SC} meta.tag.xml string.quoted.double.xml',
    'Scala XML comment':             f'{SC} comment.block.xml',
    # Scala CLI `//> using dep org::lib:1.0` directives
    'Scala directive prefix':        f'{SC} comment.line.shebang.scala punctuation.definition.comment.scala',
    'Scala directive command':       f'{SC} comment.line.shebang.scala keyword.other.import.scala',
    'Scala directive key':           f'{SC} variable.other.constant',
    'Scala directive value':         f'{SC} string',

    # ================= Scala: identifiers (Metals semantic tokens -> fallback scopes) =================
    'Scala Class':                   f'{SC} entity.name.type.class',
    'Scala Abstract class':          f'{SC} entity.name.type.class',
    'Scala Object':                  f'{SC} entity.name.type.class',
    'Scala Trait':                   f'{SC} entity.name.type.interface',
    'Scala Enum':                    f'{SC} entity.name.type.enum',
    'Scala Enum Class Case':         f'{SC} entity.name.type.enum',
    'Scala Enum Singleton Case':     f'{SC} entity.name.type.enum',
    'Scala Predefined types':        f'{SC} entity.name.type.class',
    'Scala Mutable Collection':      f'{SC} entity.name.type.class',
    'Scala Immutable Collection':    f'{SC} entity.name.type.class',
    'StandardF Java Collection':     f'{SC} entity.name.type.class',
    'Standard Java Collection':      ('=', 'StandardF Java Collection'),
    'Scala Type parameter':          f'{SC} entity.name.type.parameter',
    'Scala Type Alias':              f'{SC} entity.name.type',
    'Scala Annotation name':         f'{SC} entity.name.type.class',
    'Scala Annotation attribute name': f'{SC} variable.parameter',
    'Scala Local value':             f'{SC} variable.other.constant',
    'Scala Local lazy val/var':      f'{SC} variable.other.constant',
    'Scala Local variable':          f'{SC} variable.other.readwrite',
    'Scala Pattern value':           f'{SC} variable.other.constant',
    'Scala For statement value':     f'{SC} variable.other.constant',
    'Scala Given':                   f'{SC} variable.other.constant',
    'Scala Template val':            f'{SC} variable.other.readwrite',
    'Scala Template var':            f'{SC} variable.other.readwrite',
    'Scala Template lazy val/var':   f'{SC} variable.other.readwrite',
    'Scala Case class field':        f'{SC} variable.other.readwrite',
    'Scala Case class var field':    f'{SC} variable.other.readwrite',
    'Scala Parameter':               f'{SC} variable.parameter',
    'Scala Anonymous Parameter':     f'{SC} variable.parameter',
    'Scala Named Argument':          f'{SC} variable.parameter',
    'Scala Method declaration':      f'{SC} entity.name.function.member',
    'Scala Class method call':       f'{SC} entity.name.function.member',
    'Scala Object method call':      f'{SC} entity.name.function.member',
    'Scala Local method call':       f'{SC} entity.name.function.member',
    'Implicit conversion':           f'{SC} entity.name.function.member',
    'Implicit conversion first part':  ('=', 'Implicit conversion'),
    'Implicit conversion second part': ('=', 'Implicit conversion'),
    'Scalatest keyword':             f'{SC} entity.name.function.member',

    # ================= Dart: TextMate (built-in dart grammar) =================
    'DART_KEYWORD':               ('dart', 'class Foo', 1),
    'DART_NUMBER':                ('dart', '42', 1),
    'DART_STRING':                ('dart', '"Escape', 1),
    'DART_VALID_STRING_ESCAPE':   ('dart', r'\n', 1),
    'DART_INVALID_STRING_ESCAPE': ('dart', r'\xZZ', 1),
    'DART_LINE_COMMENT':          ('dart', '// Comment', 1),
    'DART_BLOCK_COMMENT':         ('dart', '/* block', 1),
    'DART_DOC_COMMENT':           ('dart', '/// doc', 1),
    'DART_OPERATION_SIGN':        ('dart', '+ 42', 1),
    'DART_PARENTH':               ('dart', '(dynamicParameter', 1),
    'DART_BRACKETS':              ('dart', '[566', 1),
    'DART_BRACES':                ('dart', "{'a'", 1),
    'DART_COMMA':                 ('dart', ', V>', 1),
    'DART_DOT':                   ('dart', '.unresolved', 1),
    'DART_SEMICOLON':             ('dart', ';\nimport', 1),
    'DART_COLON':                 ('dart', ': while', 1),
    'DART_FAT_ARROW':             ('dart', '=> staticField', 1),
    'DART_SYMBOL_LITERAL':        ('dart', '#Enum', 1),
    'DART_CONSTRUCTOR':           ('dart', 'constructor(', 1),
    'DART_BAD_CHARACTER':         DT,

    # ================= Dart: identifiers (analysis-server semantic tokens) =================
    'DART_ANNOTATION':                         f'{DT} variable',
    'DART_CLASS':                              f'{DT} entity.name.type.class',
    'DART_MIXIN':                              f'{DT} entity.name.type.class',
    'DART_EXTENSION':                          f'{DT} entity.name.type.class',
    'DART_EXTENSION_TYPE':                     f'{DT} entity.name.type.class',
    'DART_ENUM':                               f'{DT} entity.name.type.enum',
    'DART_ENUM_CONSTANT':                      f'{DT} variable.other.enummember',
    'DART_FUNCTION_TYPE_ALIAS':                f'{DT} entity.name.type',
    'DART_TYPE_ALIAS':                         f'{DT} entity.name.type',
    'DART_TYPE_NAME_DYNAMIC':                  f'{DT} entity.name.type',
    'DART_TYPE_PARAMETER':                     f'{DT} entity.name.type.parameter',
    'DART_IDENTIFIER':                         f'{DT} meta.embedded',
    'DART_UNRESOLVED_INSTANCE_MEMBER_REFERENCE': f'{DT} meta.embedded',
    'DART_IMPORT_PREFIX':                      f'{DT} variable.other.readwrite',
    'DART_LIBRARY_NAME':                       f'{DT} entity.name.namespace',
    'DART_LABEL':                              f'{DT} entity.name.label',
    'DART_CONSTRUCTOR_TEAR_OFF':               f'{DT} entity.name.function.member',
    'DART_INSTANCE_FIELD_DECLARATION':         f'{DT} variable.other.readwrite',
    'DART_INSTANCE_FIELD_REFERENCE':           f'{DT} variable.other.readwrite',
    'DART_STATIC_FIELD_DECLARATION':           f'{DT} variable.other.readwrite',
    'DART_TOP_LEVEL_VARIABLE_DECLARATION':     f'{DT} variable.other.readwrite',
    'DART_LOCAL_VARIABLE_DECLARATION':         f'{DT} variable.other.readwrite',
    'DART_LOCAL_VARIABLE_REFERENCE':           f'{DT} variable.other.readwrite',
    'DART_DYNAMIC_LOCAL_VARIABLE_DECLARATION': f'{DT} variable.other.readwrite',
    'DART_DYNAMIC_LOCAL_VARIABLE_REFERENCE':   f'{DT} variable.other.readwrite',
    'DART_INSTANCE_GETTER_DECLARATION':        f'{DT} variable.other.property',
    'DART_INSTANCE_GETTER_REFERENCE':          f'{DT} variable.other.property',
    'DART_INSTANCE_SETTER_DECLARATION':        f'{DT} variable.other.property',
    'DART_INSTANCE_SETTER_REFERENCE':          f'{DT} variable.other.property',
    'DART_STATIC_GETTER_DECLARATION':          f'{DT} variable.other.property',
    'DART_STATIC_GETTER_REFERENCE':            f'{DT} variable.other.property',
    'DART_STATIC_SETTER_DECLARATION':          f'{DT} variable.other.property',
    'DART_STATIC_SETTER_REFERENCE':            f'{DT} variable.other.property',
    'DART_TOP_LEVEL_GETTER_DECLARATION':       f'{DT} variable.other.property',
    'DART_TOP_LEVEL_GETTER_REFERENCE':         f'{DT} variable.other.property',
    'DART_TOP_LEVEL_SETTER_DECLARATION':       f'{DT} variable.other.property',
    'DART_TOP_LEVEL_SETTER_REFERENCE':         f'{DT} variable.other.property',
    'DART_INSTANCE_METHOD_DECLARATION':        f'{DT} entity.name.function.member',
    'DART_INSTANCE_METHOD_REFERENCE':          f'{DT} entity.name.function.member',
    'DART_INSTANCE_METHOD_TEAR_OFF':           f'{DT} entity.name.function.member',
    'DART_STATIC_METHOD_DECLARATION':          f'{DT} entity.name.function.member',
    'DART_STATIC_METHOD_REFERENCE':            f'{DT} entity.name.function.member',
    'DART_STATIC_METHOD_TEAR_OFF':             f'{DT} entity.name.function.member',
    'DART_TOP_LEVEL_FUNCTION_DECLARATION':     f'{DT} entity.name.function',
    'DART_TOP_LEVEL_FUNCTION_REFERENCE':       f'{DT} entity.name.function',
    'DART_TOP_LEVEL_FUNCTION_TEAR_OFF':        f'{DT} entity.name.function',
    'DART_LOCAL_FUNCTION_DECLARATION':         f'{DT} entity.name.function',
    'DART_LOCAL_FUNCTION_REFERENCE':           f'{DT} entity.name.function',
    'DART_LOCAL_FUNCTION_TEAR_OFF':            f'{DT} entity.name.function',
    'DART_PARAMETER_DECLARATION':              f'{DT} variable.parameter',
    'DART_PARAMETER_REFERENCE':                f'{DT} variable.parameter',
    'DART_DYNAMIC_PARAMETER_DECLARATION':      f'{DT} variable.parameter',
    'DART_DYNAMIC_PARAMETER_REFERENCE':        f'{DT} variable.parameter',

    # ================= Smali (Android Studio; Smalise grammar scopes, explicit) =================
    'SMALI_COMMENT':          f'{SM} comment.line.number-sign.smali',
    'SMALI_KEYWORD':          f'{SM} constant.language.smali',
    'SMALI_JAVA_IDENTIFIER':  f'{SM} constant.numeric.smali',
    'SMALI_STRING':           f'{SM} string.quoted.double.smali',
    'SMALI_NUMBER':           f'{SM} constant.numeric.smali',
    'SMALI_CONSTANT':         f'{SM} constant.numeric.smali',
    'SMALI_STATIC_FIELD':     f'{SM} string.interpolated.smali',
    'SMALI_INSTANCE_FIELD':   f'{SM} string.interpolated.smali',
    'SMALI_BRACES':           SM,
    'SMALI_PARENTHESIS':      SM,

    # ================= ProGuard / R8 rules (no VS Code grammar: Java-equivalent keys) =================
    'PROGUARD_R8_FLAG':                   f'{PG} keyword.other.flag.proguard',
    'PROGUARD_R8_KEYWORD':                ('=', 'JAVA_KEYWORD'),
    'PROGUARD_R8_IDENTIFIER':             ('=', 'CLASS_REFERENCE'),
    'PROGUARD_R8_ANNOTATION':             ('=', 'ANNOTATION_NAME_ATTRIBUTES'),
    'PROGUARD_R8_METHOD_FIELD_WILDCARDS': f'{PG} variable.language.wildcard.proguard',
    'PROGUARD_R8_PARAMETER':              ('=', 'DEFAULT_INSTANCE_FIELD'),
    'PROGUARD_R8_STRING':                 ('=', 'JAVA_STRING'),
    'PROGUARD_R8_LINE_COMMENT':           f'{PG} comment.line.number-sign.proguard',
    'PROGUARD_R8_BRACES':                 ('=', 'JAVA_BRACES'),
    'PROGUARD_R8_PARENTHESES':            ('=', 'JAVA_PARENTH'),
    'PROGUARD_R8_COMMA':                  ('=', 'JAVA_COMMA'),
    'PROGUARD_R8_SEMICOLON':              ('=', 'JAVA_SEMICOLON'),
    'PROGUARD_R8_BAD_CHARACTER':          PG,

    # ================= Room SQL (AndroidSql): VS Code sql grammar =================
    'ANDROID_SQL_KEYWORD':       ('roomsql', 'SELECT'),
    'ANDROID_SQL_NUMBER':        ('roomsql', '10'),
    'ANDROID_SQL_STRING':        ('roomsql', "'A%'"),
    'ANDROID_SQL_LINE_COMMENT':  ('roomsql', '-- Room'),
    'ANDROID_SQL_BLOCK_COMMENT': ('roomsql', '/* block'),
    'ANDROID_SQL_PARAMETER':     ('roomsql', ':userId'),
    'ANDROID_SQL_OPERATOR':      ('roomsql', '= :userId'),
    'ANDROID_SQL_PARENTHESES':   ('roomsql', '(msg'),
    'ANDROID_SQL_COMMA':         ('roomsql', ', ts'),
    'ANDROID_SQL_SEMICOLON':     ('roomsql', ';\n/*'),
    'ANDROID_SQL_DOT':           ('=', 'SQL_DOT'),
    'ANDROID_SQL_CONSTANT':      ('roomsql', 'CURRENT_TIMESTAMP'),
    'ANDROID_SQL_IDENTIFIER':    ('roomsql', 'users'),
    'ANDROID_SQL_BAD_CHARACTER': 'source.sql',

    # ================= Gradle Declarative (.dcl; Kotlin-DSL subset, fwcd Kotlin scopes) =================
    'org.gradle.declarative.COMMENT':               f'{KT} comment.line.double-slash.kotlin',
    'org.gradle.declarative.BLOCK_COMMENT':         f'{KT} comment.block.kotlin',
    'org.gradle.declarative.BOOLEAN':               f'{KT} constant.language.boolean.kotlin',
    'org.gradle.declarative.NULL':                  f'{KT} constant.language.null.kotlin',
    'org.gradle.declarative.NUMBER':                f'{KT} constant.numeric.decimal.kotlin',
    'org.gradle.declarative.STRING':                f'{KT} string.quoted.double.kotlin',
    'org.gradle.declarative.VALID_STRING_ESCAPE':   f'{KT} string.quoted.double.kotlin constant.character.escape.kotlin',
    'org.gradle.declarative.INVALID_STRING_ESCAPE': f'{KT} string.quoted.double.kotlin constant.character.escape.kotlin',

    # ================= Wear OS Watch Face Format expressions (no VS Code grammar) =================
    'WFF_expression_DATA_SOURCE':   ('=', 'DEFAULT_STATIC_FIELD'),
    'WFF_expression_CONFIGURATION': ('=', 'DEFAULT_INSTANCE_FIELD'),
    'WFF_expression_REFERENCE':     ('=', 'DEFAULT_INSTANCE_FIELD'),
    'WFF_expression_FUNCTION_ID':   ('=', 'DEFAULT_FUNCTION_CALL'),
    'WFF_expression_ID':            ('=', 'DEFAULT_IDENTIFIER'),
    'WFF_expression_NULL':          ('=', 'DEFAULT_KEYWORD'),
    'WFF_expression_NUMBER':        ('=', 'DEFAULT_NUMBER'),
    'WFF_expression_STRING':        ('=', 'DEFAULT_STRING'),
    'WFF_expression_OPERATORS':     ('=', 'DEFAULT_OPERATION_SIGN'),
    'WFF_expression_PARENTHESES':   ('=', 'DEFAULT_PARENTHS'),
    'WFF_expression_BRACKETS':      ('=', 'DEFAULT_BRACKETS'),
    'WFF_expression_COMMA':         ('=', 'DEFAULT_COMMA'),
    'WFF_expression_BAD_CHARACTER': 'source.ts',

    # ================= Compose @Preview(device = "spec:...") string injection =================
    # VS Code sees a plain Kotlin string literal: every part takes the string colour.
    'PREFIX': ('=', 'DEFAULT_IDENTIFIER'),  # bare global key name (Compose @Preview spec): neutral core colour
    'PARAM': ('=', 'DEFAULT_IDENTIFIER'),  # bare global key name (Compose @Preview spec): neutral core colour
    'SEPARATOR': ('=', 'DEFAULT_COMMA'),  # bare global key name (Compose @Preview spec): neutral core colour
    'OPERATOR': ('=', 'DEFAULT_OPERATION_SIGN'),  # bare global key name (Compose @Preview spec): neutral core colour
    'PRIMITIVE': ('=', 'DEFAULT_CONSTANT'),  # bare global key name (Compose @Preview spec): neutral core colour
    'UNIT': ('=', 'DEFAULT_IDENTIFIER'),  # bare global key name (Compose @Preview spec): neutral core colour
    'STRING': ('=', 'DEFAULT_STRING'),  # bare global key name (Compose @Preview spec): neutral core colour
}

NOTES = {
    'Scala Keyword': 'Scala: no VS Code grammar installed; explicit stacks in scala-lang/vscode-scala-syntax scopes (keywords all colour alike)',
    'Scala Class': 'Scala identifiers: Metals semantic tokens (class/object -> class, trait -> interface, alias -> type) via VS Code fallback table',
    'Scala Template val': 'Metals (Scala 2 PC): member val/var are accessors -> semantic variable (no readonly) -> variable.other.readwrite; Scala 3 PC gives member vals readonly (judgement: Scala 2 kept); local vals are variable.readonly',
    'Scala Local value': 'Metals: local/pattern/for/given vals -> variable.readonly -> variable.other.constant',
    'Scala Assign': '`=` is a one-char operator -> keyword.operator.comparison.scala in vscode-scala-syntax',
    'Scala Dot': 'vscode-scala-syntax leaves . , ; unscoped',
    'Interpolated String Injection': 'the `$` of s"..$x" (the name gets its own key): Metals emits Interpolation.SpliceStart as keyword',
    'Scala Valid escape in string': 'Metals makeStringTokens emits every backslash escape (valid or not) and $$ as semantic regexp -> string.regexp (string colour)',
    'ScalaDoc @param value': 'Metals DocstringToken: @param/@tparam name -> variable.readonly',
    'Scala Enum': 'Scala 3 presentation compiler: enum, enum class cases and singleton cases (EnumVal) are all semantic enum',
    'Scala directive key': 'Metals makeScalaCliTokens: //> comment, using keyword, key variable.readonly, values string',
    'Implicit conversion': 'IntelliJ marks the implicitly-applied method (demo: `1 to 5`); in VS Code it is a Metals method token',
    'Scalatest keyword': 'should/in/must are methods for Metals -> method',
    'Scala XML comment': 'explicit; vscode-scala-syntax has no XML comment rule, comment scope kept',
    'Scala directive prefix': 'Metals makeScalaCliTokens (//> -> comment)',
    'ScalaDoc html tag': 'Metals emits comment for all doc text except @tags (keyword), @param names and [[links]]; html, wiki and escapes stay comment',
    'StandardF Java Collection': 'real key name (typo in the Scala plugin); "Standard Java Collection" is a stale name in its bundled schemes',
    'Implicit conversion first part': 'stale keys still set by the Scala plugin schemes (no code creates them); aliased to Implicit conversion',
    'DART_KEYWORD': 'Dart: built-in TextMate grammar for tokens; identifiers explicit from analysis-server semantic tokens + Dart-Code semanticTokenScopes',
    'DART_ANNOTATION': 'Dart-Code maps semantic "annotation" -> variable',
    'DART_IDENTIFIER': 'analysis server emits custom "source" -> Dart-Code meta.embedded (plain text)',
    'DART_INSTANCE_FIELD_DECLARATION': 'analysis server: fields are "variable", getters/setters (and their references) "property"',
    'DART_CONSTRUCTOR': 'named constructors get no semantic token from the analysis server: TextMate scope',
    'SMALI_KEYWORD': 'explicit; Smalise grammar (de-facto VS Code Smali ext): directives constant.language (chosen), access flags variable.parameter',
    'SMALI_JAVA_IDENTIFIER': 'Smalise scopes class descriptors in operands/signatures constant.numeric (in .class/.super they are string)',
    'SMALI_STATIC_FIELD': 'Smalise scopes field names string.interpolated',
    'PROGUARD_R8_FLAG': 'explicit; no VS Code ProGuard grammar: -keep etc. as keywords. Java-like tokens alias Java keys',
    'PROGUARD_R8_METHOD_FIELD_WILDCARDS': 'explicit; <init>/<methods>/<fields> as language constants (variable.language)',
    'ANDROID_SQL_KEYWORD': 'Room SQL: VS Code sql grammar sample',
    'org.gradle.declarative.COMMENT': 'explicit; .dcl is a Kotlin-DSL subset: fwcd Kotlin scopes as for KOTLIN_* keys',
    'WFF_expression_DATA_SOURCE': 'Watch Face Format expressions: no VS Code grammar; aliases to the core keys they fall back to',
    'PREFIX': 'Compose device-spec keys (PREFIX/PARAM/SEPARATOR/OPERATOR/PRIMITIVE/UNIT/STRING) colour parts of a Kotlin string; VS Code shows the whole string',
}
