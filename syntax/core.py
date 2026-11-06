"""Language-neutral IntelliJ keys (DEFAULT_*, CUSTOM_* for user file types, TEXT-level ones).

These are the fallbacks of almost every language key, so they use the scope VS Code gives the
construct in a typical language. Identifier-like keys follow VS Code's semantic-token fallback
scopes (TypeScript/JavaScript emit semantic tokens, and the GitHub theme enables them), the rest
come from real TypeScript / HTML samples.
"""

TS = r'''/**
 * Adds two numbers.
 * @param a first value
 */
export function add(a: number, b = 2): number {
  const total = a + b; // sum
  /* block */
  return total > 10 ? 0x1f : "ten\n\q";
}
label: for (;;) { break label; }
'''
HTML = '<div class="box">&amp; text</div>\n'

SAMPLES = {'ts': ('source.ts', TS), 'html': ('text.html.basic', HTML)}

MAP = {
    # lexical
    'DEFAULT_KEYWORD': ('ts', 'return', 1),
    'DEFAULT_STRING': ('ts', 'ten', 1),
    'DEFAULT_NUMBER': ('ts', '10', 1),
    'DEFAULT_LINE_COMMENT': ('ts', 'sum', 1),
    'DEFAULT_BLOCK_COMMENT': ('ts', 'block', 1),
    'DEFAULT_DOC_COMMENT': ('ts', 'Adds', 1),
    'DEFAULT_DOC_COMMENT_TAG': ('ts', '@param', 1),
    'DEFAULT_DOC_COMMENT_TAG_VALUE': ('ts', 'a first', 1),
    'DEFAULT_DOC_MARKUP': ('ts', 'Adds', 1),
    'DEFAULT_OPERATION_SIGN': ('ts', '+ b', 1),
    'DEFAULT_BRACES': ('ts', '{\n  const', 1),
    'DEFAULT_BRACKETS': 'source.ts meta.array.literal.ts meta.brace.square.ts',
    'DEFAULT_PARENTHS': ('ts', '(a:', 1),
    'DEFAULT_COMMA': ('ts', ', b', 1),
    'DEFAULT_DOT': 'source.ts punctuation.accessor.ts',
    'DEFAULT_SEMICOLON': ('ts', '; // sum', 1),
    'DEFAULT_VALID_STRING_ESCAPE': ('ts', '\\n', 1),
    'DEFAULT_INVALID_STRING_ESCAPE': 'source.ts string.quoted.double.ts invalid.illegal',
    # identifiers: VS Code semantic-token fallback scopes
    'DEFAULT_IDENTIFIER': 'source.ts',
    'DEFAULT_LOCAL_VARIABLE': 'source.ts variable.other.readwrite',
    'DEFAULT_REASSIGNED_LOCAL_VARIABLE': 'source.ts variable.other.readwrite',
    'DEFAULT_GLOBAL_VARIABLE': 'source.ts variable.other.readwrite',
    'DEFAULT_PARAMETER': 'source.ts variable.parameter',
    'DEFAULT_REASSIGNED_PARAMETER': 'source.ts variable.parameter',
    'DEFAULT_INSTANCE_FIELD': 'source.ts variable.other.property',
    'DEFAULT_STATIC_FIELD': 'source.ts variable.other.property',
    'DEFAULT_CONSTANT': 'source.ts variable.other.constant',
    'DEFAULT_PREDEFINED_SYMBOL': 'source.ts support.function',
    'DEFAULT_CLASS_NAME': 'source.ts entity.name.type.class',
    'DEFAULT_CLASS_REFERENCE': 'source.ts entity.name.type.class',
    'DEFAULT_INTERFACE_NAME': 'source.ts entity.name.type.interface',
    'DEFAULT_FUNCTION_DECLARATION': 'source.ts entity.name.function',
    'DEFAULT_FUNCTION_CALL': 'source.ts entity.name.function',
    'DEFAULT_INSTANCE_METHOD': 'source.ts entity.name.function.member',
    'DEFAULT_STATIC_METHOD': 'source.ts entity.name.function.member',
    'DEFAULT_METADATA': 'source.ts meta.decorator.ts entity.name.function',
    'DEFAULT_LABEL': ('ts', 'label', 1),
    # markup
    'DEFAULT_TAG': ('html', 'div', 1),
    'DEFAULT_ATTRIBUTE': ('html', 'class', 1),
    'DEFAULT_ENTITY': ('html', '&amp;', 1),
    'DEFAULT_TEMPLATE_LANGUAGE_COLOR': ('html', 'text', 1),
    # user-defined file types (Settings | Editor | File Types): keyword sets 1-4
    'CUSTOM_KEYWORD1_ATTRIBUTES': ('=', 'DEFAULT_KEYWORD'),
    'CUSTOM_KEYWORD2_ATTRIBUTES': 'source.ts support.type',
    'CUSTOM_KEYWORD3_ATTRIBUTES': ('=', 'DEFAULT_CLASS_REFERENCE'),
    'CUSTOM_KEYWORD4_ATTRIBUTES': ('=', 'DEFAULT_FUNCTION_CALL'),
    'CUSTOM_STRING_ATTRIBUTES': ('=', 'DEFAULT_STRING'),
    'CUSTOM_NUMBER_ATTRIBUTES': ('=', 'DEFAULT_NUMBER'),
    'CUSTOM_LINE_COMMENT_ATTRIBUTES': ('=', 'DEFAULT_LINE_COMMENT'),
    'CUSTOM_MULTI_LINE_COMMENT_ATTRIBUTES': ('=', 'DEFAULT_BLOCK_COMMENT'),
    'CUSTOM_VALID_STRING_ESCAPE_ATTRIBUTES': ('=', 'DEFAULT_VALID_STRING_ESCAPE'),
    'CUSTOM_INVALID_STRING_ESCAPE_ATTRIBUTES': ('=', 'DEFAULT_INVALID_STRING_ESCAPE'),
}

NOTES = {
    'DEFAULT_METADATA': 'decorators/annotations: TS semantic token for the decorator call is a function',
    'DEFAULT_IDENTIFIER': 'plain identifier: no scope beyond the root, i.e. editor foreground',
    'DEFAULT_DOC_MARKUP': 'IntelliJ doc markup is plain doc-comment text in VS Code',
}
