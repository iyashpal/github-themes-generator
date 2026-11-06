"""JVM family: Java (+ IntelliJ's Java-flavoured core keys), Groovy, Kotlin, Scala, Clojure leftovers,
EL / SpEL / Micronaut EL, Velocity, FreeMarker, Qute, Lombok config, Drools, Spring beans, Compose.

Java: VS Code with the Red Hat Java extension colours identifiers from semantic tokens, so identifier keys
use explicit `source.java <semantic fallback scope>` stacks (VS Code's fallback table plus vscode-java's
own semanticTokenScopes: annotation -> storage.type.annotation.java, annotationMember ->
entity.name.annotationMember.java, *.constructor -> entity.name.function.java).
Groovy and Clojure: VS Code's bundled TextMate grammars (no semantic tokens) -> samples.
Kotlin / Scala: no grammar installed -> explicit stacks in the fwcd Kotlin / Scala grammar style.
Template / expression languages without a VS Code grammar (EL, SpEL, MN EL, Velocity, FTL, Qute, Drools)
-> aliases to the equivalent Java / core keys.
"""

SAMPLES = {
    'java': ('source.java', r'''package com.example.demo;

import java.util.List;

/**
 * Demo service.
 * <p>Uses a list.</p>
 * @param <T> the item type
 */
public abstract class Demo<T> implements Runnable {
    private static final int LIMIT = 10;
    private String name;

    public Demo(String name) {
        // line comment
        /* block comment */
        int[] values = new int[3];
        String text = "tab\tend\q";
        this.name = text;
        values[0] = LIMIT;
        List<String> pair = List.of("a", "b");
        return;
    }
}
'''),
    'groovy': ('source.groovy', r'''package demo

class Greeter {
    static final String PREFIX = 'Hi'
    String name

    static String greet(String who) {
        def list = [1, 2, 3]
        list.each { item -> println item }
        Point p = [1, 2]
        return "${PREFIX} ${who}"
    }

    void run() {
        println this.name
        Greeter.greet('x')
        unknownCall()
        println Greeter.PREFIX
    }
}
'''),
    'groovy2': ('source.groovy', r'''package demo

/**
 * Greets people.
 * @param who the name
 */
@Grab(group = 'org', version = '1')
class Greeter<T> extends Base {
    static final String PREFIX = 'Hi\n'
    private int count = 42

    Greeter(String who) {
        this.count = 1
    }

    static String greet(String who) {
        // line comment
        /* block comment */
        File f = new File('x')
        def map = [key1: 1, key2: 2]
        def fn = x -> { x * 2 }
        def r = new Runnable() { void run() {} }
        String s = who.toUpperCase()
        outer:
        for (i in map) { continue outer }
        return "${PREFIX} ${s}\t" + 'a' + (s ? 1 : 2)
    }
}
'''),
    'clojure': ('source.clojure', r'''(ns demo.core)

(defn greet [who]
  (println "Hello" who))
'''),
    'lombok': ('source.ini', r'''# Lombok config
clear lombok.log.fieldName
lombok.log.fieldName = LOGGER
'''),
}

J = 'source.java'
KT = 'source.kotlin'
SC = 'source.scala'

MAP = {
    # ---- Java: TextMate (keywords, literals, comments, punctuation) ----
    'JAVA_KEYWORD':               ('java', 'return', 1),
    'JAVA_NUMBER':                ('java', '10', 1),
    'JAVA_STRING':                ('java', '"tab', 1),
    'JAVA_VALID_STRING_ESCAPE':   ('java', r'\t', 1),
    'JAVA_INVALID_STRING_ESCAPE': ('java', r'\q', 1),  # VS Code's Java grammar scopes any \x as an escape
    'JAVA_LINE_COMMENT':          ('java', '// line', 1),
    'JAVA_BLOCK_COMMENT':         ('java', '/* block', 1),
    'JAVA_DOC_COMMENT':           ('java', 'Demo service', 1),
    'JAVA_DOC_TAG':               ('java', '@param', 1),
    'JAVA_DOC_MARKUP':            ('java', '<p>', 1),
    'DOC_COMMENT_TAG_VALUE':      f'{J} variable.parameter',
    'JAVA_OPERATION_SIGN':        ('java', '= 10', 1),
    'JAVA_PARENTH':               ('java', '(String name', 1),
    'JAVA_BRACKETS':              ('java', '[0]', 1),
    'JAVA_BRACES':                ('java', '{\n    private', 1),
    'JAVA_COMMA':                 ('java', ', "b"', 1),
    'JAVA_DOT':                   ('java', '.of', 1),
    'JAVA_SEMICOLON':             ('java', ';\n\nimport', 1),

    # ---- Java / core identifier keys: semantic-token fallback scopes ----
    'CLASS_NAME_ATTRIBUTES':                  f'{J} entity.name.type.class',
    'CLASS_REFERENCE':                        f'{J} entity.name.type.class',
    'ABSTRACT_CLASS_NAME_ATTRIBUTES':         f'{J} entity.name.type.class',
    'ANONYMOUS_CLASS_NAME_ATTRIBUTES':        f'{J} entity.name.function.java',
    'RECORD_NAME_ATTRIBUTES':                 f'{J} entity.name.type.class',
    'ENUM_NAME_ATTRIBUTES':                   f'{J} entity.name.type.enum',
    'INTERFACE_NAME_ATTRIBUTES':              f'{J} entity.name.type.interface',
    'TYPE_PARAMETER_NAME_ATTRIBUTES':         f'{J} entity.name.type.parameter',
    'ENUM_CONST':                             f'{J} variable.other.enummember',
    'ANNOTATION_NAME_ATTRIBUTES':             f'{J} storage.type.annotation.java',
    'ANNOTATION_ATTRIBUTE_NAME_ATTRIBUTES':   f'{J} entity.name.annotationMember.java',
    'METHOD_DECLARATION_ATTRIBUTES':          f'{J} entity.name.function.member',
    'METHOD_CALL_ATTRIBUTES':                 f'{J} entity.name.function.member',
    'STATIC_METHOD_ATTRIBUTES':               f'{J} entity.name.function.member',
    'STATIC_METHOD_IMPORTED_ATTRIBUTES':      f'{J} entity.name.function.member',
    'STATIC_METHOD_CALL_IMPORTED_ATTRIBUTES': f'{J} entity.name.function.member',
    'ABSTRACT_METHOD_ATTRIBUTES':             f'{J} entity.name.function.member',
    'INHERITED_METHOD_ATTRIBUTES':            f'{J} entity.name.function.member',
    'CONSTRUCTOR_DECLARATION_ATTRIBUTES':     f'{J} entity.name.function.java',
    'CONSTRUCTOR_CALL_ATTRIBUTES':            f'{J} entity.name.function.java',
    'INSTANCE_FIELD_ATTRIBUTES':              f'{J} variable.other.property',
    'INSTANCE_FINAL_FIELD_ATTRIBUTES':        f'{J} variable.other.constant.property',
    'RECORD_COMPONENT_ATTRIBUTES':            f'{J} variable.parameter',
    'STATIC_FIELD_ATTRIBUTES':                f'{J} variable.other.property',
    'STATIC_FIELD_IMPORTED_ATTRIBUTES':       f'{J} variable.other.property',
    'STATIC_FINAL_FIELD_ATTRIBUTES':          f'{J} variable.other.constant.property',
    'STATIC_FINAL_FIELD_IMPORTED_ATTRIBUTES': f'{J} variable.other.constant.property',
    'LOCAL_VARIABLE_ATTRIBUTES':              f'{J} variable.other.readwrite',
    'REASSIGNED_LOCAL_VARIABLE_ATTRIBUTES':   f'{J} variable.other.readwrite',
    'PARAMETER_ATTRIBUTES':                   f'{J} variable.parameter',
    'REASSIGNED_PARAMETER_ATTRIBUTES':        f'{J} variable.parameter',
    'LAMBDA_PARAMETER_ATTRIBUTES':            f'{J} variable.parameter',
    'IMPLICIT_ANONYMOUS_CLASS_PARAMETER_ATTRIBUTES': f'{J} variable.other.readwrite',

    # ---- Groovy (bundled TextMate grammar) ----
    'GROOVY_KEYWORD':                 ('groovy', 'def', 1),
    'Class':                          ('groovy2', 'File f', 1),
    'Groovy method declaration':      ('groovy', 'greet(String', 1),
    'Static method access':           ('groovy', "greet('x')", 1),
    'Instance property reference ID': ('groovy', 'name\n        Greeter', 1),
    'Static property reference ID':   ('groovy', 'PREFIX\n    }', 1),
    'Unresolved reference access':    ('groovy', 'unknownCall', 1),
    'Closure braces':                 ('groovy', '{ item', 1),
    'List/map to object conversion':  ('groovy', '[1, 2]', 1),
    'Annotation':                     ('groovy2', '@Grab', 1),
    'Anotation attribute name':       ('groovy2', 'group', 1),
    'Groovydoc comment':              ('groovy2', 'Greets', 1),
    'Groovydoc tag':                  ('groovy2', '@param', 1),
    'Line comment':                   ('groovy2', '// line', 1),
    'Block comment':                  ('groovy2', '/* block', 1),
    'Abstract class name':            ('=', 'Class'),
    'Anonymous class name':           ('groovy2', 'Runnable', 1),
    'Interface name':                 ('=', 'Class'),
    'Trait name':                     ('=', 'Class'),
    'Enum name':                      ('=', 'Class'),
    'Type parameter':                 ('groovy2', 'T>', 1),
    'Groovy constructor declaration': ('groovy2', 'Greeter(String', 1),
    'Groovy constructor call':        ('groovy2', "File('x", 1),
    'Method call':                    ('groovy2', 'toUpperCase', 1),
    'Instance field':                 ('groovy2', 'count =', 1),
    'Static field':                   ('groovy2', 'PREFIX =', 1),
    'Groovy var':                     ('groovy2', 's ?', 1),
    'Groovy reassigned var':          ('=', 'Groovy var'),
    'Groovy parameter':               ('groovy2', 'who)', 1),
    'Groovy reassigned parameter':    ('=', 'Groovy parameter'),
    'Map key':                        ('groovy2', 'key1', 1),
    'Label':                          ('groovy2', 'outer:', 1),
    'Lambda braces':                  ('groovy2', '{ x', 1),
    'Number':                         ('groovy2', '42', 1),
    'String':                         ('groovy2', "'Hi", 1),
    'GString':                        ('groovy2', '"${', 1),
    'Valid string escape':            ('groovy2', r'\t', 1),
    'Invalid string escape':          ('=', 'Valid string escape'),
    'Braces':                         ('groovy2', '{\n    static final', 1),
    'Brackets':                       ('groovy2', '[key1', 1),
    'Parentheses':                    ('groovy2', '(i in', 1),
    'Operation sign':                 ('groovy2', '* 2', 1),

    # ---- Clojure (La Clojure key still in our scheme) ----
    'First symbol in list':           ('clojure', 'println', 1),

    # ---- Kotlin (explicit, fwcd Kotlin grammar style) ----
    'KOTLIN_KEYWORD':            f'{KT} keyword.hard.kotlin',
    'KOTLIN_KEYWORD_VAL':        f'{KT} keyword.hard.kotlin',
    'KOTLIN_KEYWORD_VAR':        f'{KT} keyword.hard.kotlin',
    'KOTLIN_BUILTIN_ANNOTATION': f'{KT} storage.modifier.other.kotlin',
    'KOTLIN_NUMBER':             f'{KT} constant.numeric.decimal.kotlin',
    'KOTLIN_STRING':             f'{KT} string.quoted.double.kotlin',
    'KOTLIN_STRING_ESCAPE':      f'{KT} string.quoted.double.kotlin constant.character.escape.kotlin',
    'KOTLIN_INVALID_STRING_ESCAPE': f'{KT} string.quoted.double.kotlin constant.character.escape.kotlin',
    'KOTLIN_LINE_COMMENT':       f'{KT} comment.line.double-slash.kotlin',
    'KOTLIN_BLOCK_COMMENT':      f'{KT} comment.block.kotlin',
    'KOTLIN_DOC_COMMENT':        f'{KT} comment.block.javadoc.kotlin',
    'KDOC_TAG_NAME':             f'{KT} comment.block.javadoc.kotlin keyword.other.documentation.javadoc.kotlin',
    'KDOC_LINK':                 f'{KT} comment.block.javadoc.kotlin',
    'KOTLIN_OPERATION_SIGN':     f'{KT} keyword.operator.assignment.kotlin',
    'KOTLIN_AMPERSAND':          KT,  # `T & Any` sits in a type annotation: unscoped in the fwcd grammar
    'KOTLIN_SAFE_ACCESS':        KT,  # `?.` is not scoped by the fwcd grammar
    'KOTLIN_QUEST':              KT,  # nullable `?` sits in a type annotation: unscoped
    'KOTLIN_EXCLEXCL':           f'{KT} keyword.operator.logical.kotlin',
    'KOTLIN_DOUBLE_COLON':       KT,  # method-reference rule scopes only the name after `::`
    'KOTLIN_ARROW':              f'{KT} storage.type.function.arrow.kotlin',
    'KOTLIN_FUNCTION_LITERAL_BRACES_AND_ARROW': f'{KT} punctuation.section.block.kotlin',
    'KOTLIN_PARENTHESIS':        f'{KT} punctuation.section.parens.kotlin',
    'KOTLIN_BRACES':             f'{KT} punctuation.section.block.kotlin',
    'KOTLIN_BRACKETS':           f'{KT} punctuation.section.brackets.kotlin',
    'KOTLIN_COMMA':              f'{KT} punctuation.separator.delimiter.kotlin',
    'KOTLIN_SEMICOLON':          f'{KT} punctuation.terminator.kotlin',
    'KOTLIN_COLON':              f'{KT} punctuation.separator.colon.kotlin',
    'KOTLIN_DOT':                f'{KT} punctuation.separator.dot.kotlin',
    'KOTLIN_CLASS':              f'{KT} entity.name.type.class',
    'KOTLIN_ABSTRACT_CLASS':     f'{KT} entity.name.type.class',
    'KOTLIN_DATA_CLASS':         f'{KT} entity.name.type.class',
    'KOTLIN_DATA_OBJECT':        f'{KT} entity.name.type.class',
    'KOTLIN_OBJECT':             f'{KT} entity.name.type.class',
    'KOTLIN_TRAIT':              f'{KT} entity.name.type.interface',
    'KOTLIN_ENUM':               f'{KT} entity.name.type.enum',
    'KOTLIN_TYPE_ALIAS':         f'{KT} entity.name.type',
    'KOTLIN_TYPE_PARAMETER':     f'{KT} entity.name.type.parameter',
    'KOTLIN_ANNOTATION':         f'{KT} meta.annotation.kotlin entity.name.type.annotation.kotlin',
    'KOTLIN_ANNOTATION_ATTRIBUTE_NAME_ATTRIBUTES': f'{KT} variable.parameter',
    'KOTLIN_ENUM_ENTRY':         f'{KT} variable.other.enummember',
    'KOTLIN_LOCAL_VARIABLE':     f'{KT} variable.other.readwrite',
    'KOTLIN_MUTABLE_VARIABLE':   f'{KT} variable.other.readwrite',
    'KOTLIN_WRAPPED_INTO_REF':   f'{KT} variable.other.readwrite',
    'KOTLIN_PARAMETER':          f'{KT} variable.parameter',
    'KOTLIN_CLOSURE_DEFAULT_PARAMETER': f'{KT} variable.parameter',
    'KOTLIN_NAMED_ARGUMENT':     f'{KT} variable.parameter',
    'KOTLIN_CONTEXT_ARGUMENT':   f'{KT} variable.parameter',
    'KOTLIN_INSTANCE_PROPERTY':  f'{KT} variable.other.property',
    'KOTLIN_PACKAGE_PROPERTY':   f'{KT} variable.other.property',
    'KOTLIN_BACKING_FIELD_VARIABLE': f'{KT} variable.other.property',
    'KOTLIN_EXTENSION_PROPERTY': f'{KT} variable.other.property',
    'KOTLIN_SYNTHETIC_EXTENSION_PROPERTY': f'{KT} variable.other.property',
    'KOTLIN_DYNAMIC_PROPERTY_CALL': f'{KT} variable.other.property',
    'KOTLIN_ANDROID_EXTENSIONS_PROPERTY_CALL': f'{KT} variable.other.property',
    'KOTLIN_INSTANCE_PROPERTY_CUSTOM_PROPERTY_DECLARATION': f'{KT} variable.other.property',
    'KOTLIN_PACKAGE_PROPERTY_CUSTOM_PROPERTY_DECLARATION': f'{KT} variable.other.property',
    'KOTLIN_FUNCTION_DECLARATION': f'{KT} entity.name.function.declaration.kotlin',
    'KOTLIN_FUNCTION_CALL':      f'{KT} entity.name.function.call.kotlin',
    'KOTLIN_PACKAGE_FUNCTION_CALL': f'{KT} entity.name.function.call.kotlin',
    'KOTLIN_EXTENSION_FUNCTION_CALL': f'{KT} entity.name.function.call.kotlin',
    'KOTLIN_DYNAMIC_FUNCTION_CALL': f'{KT} entity.name.function.call.kotlin',
    'KOTLIN_SUSPEND_FUNCTION_CALL': f'{KT} entity.name.function.call.kotlin',
    'KOTLIN_VARIABLE_AS_FUNCTION': f'{KT} entity.name.function.call.kotlin',
    'KOTLIN_VARIABLE_AS_FUNCTION_LIKE': f'{KT} entity.name.function.call.kotlin',
    'KOTLIN_CONSTRUCTOR':        f'{KT} entity.name.function.call.kotlin',
    'KOTLIN_LABEL':              KT,  # `loop@` / `@loop` are unscoped in the fwcd grammar, no KLS token
    'IntelliJComposableCallTextAttributes': f'{KT} entity.name.function.call.kotlin',

    # ---- Lombok config (ini-like) ----
    'LOMBOK_COMMENT':   ('lombok', '# Lombok', 1),
    'LOMBOK_CLEAN':     f'{"source.lombok.config"} keyword.control.clear.lombok',
    'LOMBOK_KEY':       ('lombok', 'lombok.log.fieldName =', 1),
    'LOMBOK_SEPARATOR': ('lombok', '= LOGGER', 1),
    'LOMBOK_VALUE':     ('lombok', 'LOGGER', 1),

    # ---- EL (JSP/JSF), no VS Code grammar -> Java equivalents ----
    'EL.KEYWORD':  ('=', 'JAVA_KEYWORD'),
    'EL.IDENT':    ('=', 'LOCAL_VARIABLE_ATTRIBUTES'),
    'EL.STRING':   ('=', 'JAVA_STRING'),
    'EL.NUMBER':   ('=', 'JAVA_NUMBER'),
    'EL.PARENTHS': ('=', 'JAVA_PARENTH'),
    'EL.BRACKETS': ('=', 'JAVA_BRACKETS'),
    'EL.COMMA':    ('=', 'JAVA_COMMA'),
    'EL.DOT':      ('=', 'JAVA_DOT'),
    'EL.BOUNDS':   'text.html.jsp punctuation.section.embedded.begin.jsp',
}

# SpEL and Micronaut EL share one highlighter design
for _p in ('SPEL.', 'MN_EL.'):
    MAP.update({
        _p + 'KEYWORD':        ('=', 'JAVA_KEYWORD'),
        _p + 'IDENTIFIER':     ('=', 'LOCAL_VARIABLE_ATTRIBUTES'),
        _p + 'OPERATIONS':     ('=', 'JAVA_OPERATION_SIGN'),
        _p + 'STRING':         ('=', 'JAVA_STRING'),
        _p + 'NUMBER':         ('=', 'JAVA_NUMBER'),
        _p + 'PARENTHESES':    ('=', 'JAVA_PARENTH'),
        _p + 'BRACKETS':       ('=', 'JAVA_BRACKETS'),
        _p + 'BRACES':         ('=', 'JAVA_BRACES'),
        _p + 'COMMA':          ('=', 'JAVA_COMMA'),
        _p + 'DOT':            ('=', 'JAVA_DOT'),
        _p + 'COLON':          ('=', 'JAVA_OPERATION_SIGN'),
        _p + 'BOUNDS':         ('=', 'EL.BOUNDS'),
        _p + 'BEAN_PREFIX':    ('=', 'ANNOTATION_NAME_ATTRIBUTES'),
        _p + 'QUALIFIED_TYPE': ('=', 'CLASS_REFERENCE'),
        _p + 'PROPERTY_KEY':   ('=', 'INSTANCE_FIELD_ATTRIBUTES'),
        _p + 'METHOD_CALL':    ('=', 'METHOD_CALL_ATTRIBUTES'),
        _p + 'STATIC_FIELD':   ('=', 'STATIC_FINAL_FIELD_ATTRIBUTES'),
    })

MAP.update({
    # ---- Velocity ----
    'VELOCITY_KEYWORD':        ('=', 'JAVA_KEYWORD'),
    'VELOCITY_DIRECTIVE':      'text.html.velocity meta.directive.velocity keyword.control.directive.velocity',
    'VELOCITY_REFERENCE':      'text.html.velocity variable.other.readwrite.velocity',
    'VELOCITY_STRING':         ('=', 'JAVA_STRING'),
    'VELOCITY_ESCAPE':         ('=', 'JAVA_VALID_STRING_ESCAPE'),
    'VELOCITY_NUMBER':         ('=', 'JAVA_NUMBER'),
    'VELOCITY_COMMENT':        ('=', 'JAVA_BLOCK_COMMENT'),
    'VELOCITY_OPERATION_SIGN': ('=', 'JAVA_OPERATION_SIGN'),
    'VELOCITY_PARENTHS':       ('=', 'JAVA_PARENTH'),
    'VELOCITY_BRACKETS':       ('=', 'JAVA_BRACKETS'),
    'VELOCITY_BRACES':         ('=', 'JAVA_BRACES'),
    'VELOCITY_COMMA':          ('=', 'JAVA_COMMA'),
    'VELOCITY_DOT':            ('=', 'JAVA_DOT'),
    'VELOCITY_SEMICOLON':      ('=', 'JAVA_SEMICOLON'),

    # ---- FreeMarker ----
    'FTL_DIRECTIVE':        'text.html.ftl meta.tag.directive.ftl entity.name.tag.directive.ftl',
    'FTL_REFERENCE':        'text.html.ftl variable.other.readwrite.ftl',
    'FTL_KEYWORD':          ('=', 'JAVA_KEYWORD'),
    'FTL_STRING':           ('=', 'JAVA_STRING'),
    'FTL_ESCAPE':           ('=', 'JAVA_VALID_STRING_ESCAPE'),
    'FTL_NUMBER':           ('=', 'JAVA_NUMBER'),
    'FTL_COMMENT':          ('=', 'JAVA_BLOCK_COMMENT'),
    'FTL_OPERATION_SIGN':   ('=', 'JAVA_OPERATION_SIGN'),
    'FTL_PARENTHESES':      ('=', 'JAVA_PARENTH'),
    'FTL_BRACKETS':         ('=', 'JAVA_BRACKETS'),
    'FTL_BRACES':           ('=', 'JAVA_BRACES'),
    'FTL_COMMA':            ('=', 'JAVA_COMMA'),
    'FTL_DOT':              ('=', 'JAVA_DOT'),
    'FTL_SEMICOLON':        ('=', 'JAVA_SEMICOLON'),

    # ---- Qute (Quarkus templates) ----
    'QUTE_TAG_NAME':          'text.html.qute meta.tag.qute entity.name.tag.qute',
    'QUTE_TAG_BRACE':         'text.html.qute meta.tag.qute punctuation.definition.tag.qute',
    'QUTE_SECONDARY_KEYWORD': ('=', 'JAVA_KEYWORD'),
    'QUTE_BOOLEAN':           'text.html.qute constant.language.boolean.qute',
    'QUTE_IDENTIFIER':        ('=', 'LOCAL_VARIABLE_ATTRIBUTES'),
    'QUTE_STRING':            ('=', 'JAVA_STRING'),
    'QUTE_NUMBER':            ('=', 'JAVA_NUMBER'),
    'QUTE_COMMENT':           ('=', 'JAVA_BLOCK_COMMENT'),
    'QUTE_OPERATOR_SIGN':     ('=', 'JAVA_OPERATION_SIGN'),
    'QUTE_PARENTHESES':       ('=', 'JAVA_PARENTH'),
    'QUTE_BRACKETS':          ('=', 'JAVA_BRACKETS'),
    'QUTE_COMMA':             ('=', 'JAVA_COMMA'),
    'QUTE_DOT':               ('=', 'JAVA_DOT'),

    # ---- Drools (Java-like rule language) ----
    'DROOLS_KEYWORD':            ('=', 'JAVA_KEYWORD'),
    'DROOLS_ATTRIBUTES':         ('=', 'JAVA_KEYWORD'),
    'DROOLS_KEYWORD_OPERATIONS': ('=', 'JAVA_KEYWORD'),
    'DROOLS_OPERATIONS':         ('=', 'JAVA_OPERATION_SIGN'),
    'DROOLS_OPERATION_SIGN':     ('=', 'JAVA_OPERATION_SIGN'),
    'DROOLS_STRING':             ('=', 'JAVA_STRING'),
    'DROOLS_NUMBER':             ('=', 'JAVA_NUMBER'),
    'DROOLS_PARENTH':            ('=', 'JAVA_PARENTH'),
    'DROOLS_BRACKETS':           ('=', 'JAVA_BRACKETS'),
    'DROOLS_BRACES':             ('=', 'JAVA_BRACES'),
    'DROOLS_COMMA':              ('=', 'JAVA_COMMA'),
    'DROOLS_DOT':                ('=', 'JAVA_DOT'),
    'DROOLS_SEMICOLON':          ('=', 'JAVA_SEMICOLON'),
})

NOTES = {
    'CLASS_NAME_ATTRIBUTES': 'Java identifiers use Red Hat Java semantic-token fallback scopes (explicit)',
    'CLASS_REFERENCE': 'in our scheme; same construct as a Java class reference (semantic class, explicit)',
    'ANNOTATION_NAME_ATTRIBUTES': 'vscode-java maps semantic "annotation" to storage.type.annotation.java (keyword colour)',
    'ANNOTATION_ATTRIBUTE_NAME_ATTRIBUTES': 'vscode-java maps "annotationMember" to entity.name.annotationMember.java',
    'CONSTRUCTOR_CALL_ATTRIBUTES': 'vscode-java maps "*.constructor" to entity.name.function.java',
    'STATIC_FINAL_FIELD_ATTRIBUTES': 'JDT LS: property + static + readonly -> variable.other.constant.property',
    'IMPLICIT_ANONYMOUS_CLASS_PARAMETER_ATTRIBUTES': 'captured outer local inside an anonymous class: a plain variable in VS Code',
    'ENUM_CONST': 'legacy key in our scheme; enum constant -> semantic enumMember',
    'First symbol in list': 'Clojure call head; VS Code clojure grammar sample',
    'KOTLIN_KEYWORD': 'Kotlin: no VS Code grammar installed; explicit fwcd-style stacks for all KOTLIN_* keys',
    'KOTLIN_NAMED_ARGUMENT': 'explicit; argument name is a parameter reference (semantic parameter)',
    'KOTLIN_FUNCTION_LITERAL_BRACES_AND_ARROW': 'explicit; lambda braces are plain punctuation in VS Code',
    'LOMBOK_CLEAN': 'explicit; lombok.config has no VS Code grammar, `clear` is a keyword',
    'LOMBOK_VALUE': 'ini analogue (as LOMBOK_KEY/SEPARATOR): VS Code ini leaves values unscoped',
    'ANONYMOUS_CLASS_NAME_ATTRIBUTES': 'JDT LS gives the type in `new X() {..}` the constructor modifier -> vscode-java *.constructor scope',
    'DOC_COMMENT_TAG_VALUE': 'Javadoc @param value: JDT LS emits the referenced parameter (semantic parameter, explicit)',
    'RECORD_COMPONENT_ATTRIBUTES': 'vscode-java recordComponent (superType parameter) -> variable.parameter',
    'INSTANCE_FINAL_FIELD_ATTRIBUTES': 'JDT LS: final -> readonly; property.readonly -> variable.other.constant.property',
    'Class': 'Groovy CLASS_REFERENCE paints declarations and references; references (storage.type.groovy) are far more common',
    'Groovy parameter': 'declaration (variable.parameter.method.groovy); VS Code leaves usages unscoped',
    'Groovy var': 'usage (unscoped); `def x =` declarations get meta.definition.variable.name',
    'Lambda braces': 'braces (unscoped) over the `->` arrow (keyword.operator), as for Closure braces',
    'KOTLIN_QUEST': 'explicit fwcd grammar (vscode-kotlin): `?`, `?.`, `&`, `::`, labels carry no scope -> plain',
    'KDOC_LINK': 'explicit; fwcd grammar leaves KDoc links as comment text',
    'EL.BOUNDS': 'explicit; ${ } delimiters as embedded-section punctuation (keyword colour in GitHub theme)',
    'VELOCITY_DIRECTIVE': 'explicit; no Velocity grammar, #if/#foreach as keyword.control',
    'FTL_DIRECTIVE': 'explicit; <#if> directive names as tag names, as FreeMarker extensions do',
    'QUTE_TAG_NAME': 'explicit; {#if} section names as tag names',
}
