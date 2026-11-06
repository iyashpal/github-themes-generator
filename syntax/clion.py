"""CLion / CIDR (also bundled in Android Studio's cidr-base): C, C++ and Objective-C (OC.* plus the
legacy un-prefixed keys still in our schemes), CMake, assembly / disassembly and the debugger's
memory view (hexdump). ReSharper C++ (CLion Nova, ReSharper.*) is mapped elsewhere.

Keys come from OCHighlightingKeys (intellij.cidr.psi.base), CMakeHighlightingKeys (intellij.cmake.psi),
AsmSyntaxHighlighter (intellij.cidr.asm) and HexdumpSyntaxHighlighter (intellij.cidr.debugger.core),
read from their static initialisers; what each key colours comes from the Colors & Fonts demo texts
codeStyle/preview/cpp/Colors.cpp and codeStyle/preview/mm/Colors.mm.

VS Code:
* C / C++: built-in grammars plus cpptools semantic tokens. Identifier keys use explicit
  `source.cpp <scope>` stacks from cpptools' contributes.semanticTokenScopes (package.json of
  ms-vscode.cpptools); keywords, literals, comments, punctuation are sample-based.
* Objective-C: cpptools does not serve Objective-C, so TextMate only (sample-based).
* CMake: twxs.cmake grammar (source.cmake), not installed here -> explicit stacks.
* Assembly: 13xforever.language-x86-64-assembly grammar (source.asm.x86_64), not installed -> explicit.
* Memory view: no VS Code equivalent; aliased to the matching assembly keys."""

SAMPLES = {
    'cpp': ('source.cpp', r'''/*
 * Block comment
 */
#include <vector>
#include <cstdio>
#define MAX(a, b) ((a) > (b) ? (a) : (b))

using namespace std; // line comment
namespace app {
typedef struct Point { int x; } Point_t;
extern int counter;
constexpr int limit = 123;

template <typename T, int N>
class Widget : public Base {
    T value;
public:
    /**
     * Computes the area.
     * @param width the width
     */
    virtual float area(int width) const {
        const char *label = "area\n\g";
        int total = MAX(width, 0) + 3.5;
        int values[2] = {1, 2};
        std::vector<int> vec = {7, 8, 9};
        int n = vec.size();
        if (N > 42) {
            this->value = N;
        }
        while (true) { break; }
        printf("Formatted %d\n", total);
        return total; /* block */ // line
    }
};

template <typename T>
concept Sized = requires (T t) { t.field; };
}
'''),
    'c': ('source.c', r'''#if 0
int disabled = 1;
#endif
'''),
    'objc': ('source.objc', r'''#import <Foundation/Foundation.h>

@interface Account<GenericType> : NSObject <NSCopying> {
    NSString *_owner;
}
@property (nonatomic, copy) NSString *name;
@end

@implementation Account
- (void)deposit:(NSInteger)amount withNote:(NSString *)note {
    [self.ledger record:amount withNote:note];
    NSLog(@"Deposit %ld", (long)amount);
    _owner = self.name;
    [super description];
}
@end
'''),
}

CPP = 'source.cpp'
CM = 'source.cmake'
ASM = 'source.asm.x86_64'

MAP = {
    # ---------------------------------------------------------------- C / C++: TextMate tokens
    'OC.KEYWORD':                  ('cpp', 'constexpr'),
    'OC.CPP_KEYWORD':              ('cpp', 'class Widget'),
    'OC.CONTROL_FLOW_KEYWORD':     ('cpp', 'if ('),
    'OC.CONTROL_TRANSFER_KEYWORD': ('cpp', 'return total'),
    'OC.BUILTIN_TYPE_KEYWORD':     ('cpp', 'float'),
    'OC.SELFSUPERTHIS':            ('cpp', 'this'),
    'OC.DIRECTIVE':                ('cpp', '#include'),
    'OC.HEADER_PATH':              ('cpp', '<vector>'),
    'OC.STRING':                   ('cpp', 'area\\n'),
    'OC.VALID_STRING_ESCAPE':      ('cpp', '\\n\\g'),
    'OC.INVALID_STRING_ESCAPE':    ('cpp', '\\g'),
    'OC.FORMAT_TOKEN':             ('cpp', '%d'),
    'OC.NUMBER':                   ('cpp', '3.5'),
    'OC.LINE_COMMENT':             ('cpp', '// line comment'),
    'OC.BLOCK_COMMENT':            ('cpp', 'Block comment'),
    'Doxygen Comment':             ('cpp', 'Computes'),
    'Doxygen Tag':                 ('cpp', '@param'),
    'Doxygen Parameter':           ('cpp', 'width the'),
    'OC.OPERATION_SIGN':           ('cpp', '+ 3.5'),
    'OC.PARENTHS':                 ('cpp', '(width, 0)'),
    'OC.BRACKETS':                 ('cpp', '[2]'),
    'OC.BRACES':                   ('cpp', '{\n            this'),
    'OC.COMMA':                    ('cpp', ', 0)'),
    'OC.DOT':                      ('cpp', '.size'),
    'OC.SEMICOLON':                ('cpp', '; /*'),
    'OC.STD_INITIALIZER_LIST':     ('cpp', '{7'),
    'OC.MACRO_PARAMETER':          ('cpp', 'a, b)'),
    'OC.DEPENDENT_CODE':           ('cpp', 'field;'),
    'OC.BADCHARACTER':             CPP,
    'OC.CONDITIONALLY_NOT_COMPILED_V2': ('c', 'int disabled'),

    # ---------------------------------------------------------------- C / C++: cpptools semantic tokens
    'OC.STRUCT_LIKE':              f'{CPP} entity.name.type.cpp',
    'OC.CLASS_REFERENCE':          ('objc', 'NSString *)note'),
    'OC.NAMESPACE_LIKE':           f'{CPP} entity.name.namespace.cpp',
    'OC.CONCEPT':                  f'{CPP} entity.name.type.cpp',
    'OC.TYPEDEF':                  f'{CPP} entity.name.type.cpp',
    'OC.TEMPLATE_TYPE':            f'{CPP} entity.name.type.cpp',
    'OC.TEMPLATE_VALUE':           f'{CPP} variable.parameter.cpp',
    'OC.DEDUCTION_GUIDE':          f'{CPP} entity.name.type.class.templated.cpp',
    'OC.GLOBAL_VARIABLE':          f'{CPP} variable.other.global.cpp',
    'OC.EXTERN_VARIABLE':          f'{CPP} variable.other.global.cpp',
    'OC.LOCAL_VARIABLE':           f'{CPP} variable.other.local.cpp',
    'OC.CONSTANT':                 f'{CPP} variable.other.global.cpp',
    'OC.ENUM_CONST':               f'{CPP} variable.other.enummember.cpp',
    'OC.PARAMETER':                f'{CPP} variable.parameter.cpp',
    'OC.STRUCT_FIELD':             f'{CPP} variable.other.property.cpp',
    'OC.FUNCTION_DECLARATION':     f'{CPP} entity.name.function.cpp',
    'OC.FUNCTION':                 f'{CPP} entity.name.function.cpp',
    'OC.OVERLOADED_OPERATOR':      f'{CPP} entity.name.function.operator.cpp',
    'OC.LABEL':                    f'{CPP} entity.name.label.cpp',
    'OC.MACRONAME':                f'{CPP} entity.name.function.preprocessor.cpp',

    # ---------------------------------------------------------------- Objective-C (TextMate only)
    'OC.METHOD_DECLARATION':       ('objc', 'deposit'),
    'OC.MESSAGE_ARGUMENT':         ('objc', 'record:'),
    'OC.PROPERTY':                 ('objc', 'name;\n    [super'),
    'OC.PROPERTY_ATTRIBUTE':       ('objc', 'nonatomic'),
    'OC.IVAR':                     ('objc', '_owner ='),
    'OC.PROTOCOL_REFERENCE':       ('objc', 'NSCopying'),
    'OC.GENERIC_PARAMETER':        ('objc', 'GenericType'),

    # ---------------------------------------------------------------- legacy keys (older CLion/AppCode)
    'OC_FORMAT_TOKEN':             ('objc', '%ld'),
    'TYPEDEF':                     ('=', 'OC.TYPEDEF'),
    'MACRONAME':                   ('=', 'OC.MACRONAME'),
    'MACRO_PARAMETER':             ('=', 'OC.MACRO_PARAMETER'),
    'LABEL':                       ('=', 'OC.LABEL'),
    'IVAR':                        ('=', 'OC.IVAR'),
    'PROTOCOL_REFERENCE':          ('=', 'OC.PROTOCOL_REFERENCE'),
    'CONDITIONALLY_NOT_COMPILED':  ('=', 'OC.CONDITIONALLY_NOT_COMPILED_V2'),

    # ---------------------------------------------------------------- CMake (twxs.cmake, explicit)
    'com.jetbrains.cmake.COMMAND':                 f'{CM} keyword.cmake',
    'com.jetbrains.cmake.KEYWORD':                 f'{CM} keyword.cmake',
    'com.jetbrains.cmake.ARGUMENT_KEYWORD':        f'{CM} entity.source.cmake',
    'com.jetbrains.cmake.ARGUMENT_PROPERTY':       f'{CM} entity.source.cmake',
    'com.jetbrains.cmake.ARGUMENT_PROPERTY_CMAKE': f'{CM} entity.source.cmake',
    'com.jetbrains.cmake.ARGUMENT_LITERAL':        CM,
    'com.jetbrains.cmake.ARGUMENT_LITERAL_CMAKE':  f'{CM} variable.source.cmake',
    'com.jetbrains.cmake.STRING_TEXT':             f'{CM} string.source.cmake',
    'com.jetbrains.cmake.VALID_STRING_ESCAPE':     f'{CM} string.source.cmake constant.character.escape',
    'com.jetbrains.cmake.INVALID_STRING_ESCAPE':   f'{CM} string.source.cmake constant.character.escape',
    'com.jetbrains.cmake.NUMERIC_TEXT':            CM,
    'com.jetbrains.cmake.LINE_COMMENT':            f'{CM} comment.source.cmake',
    'com.jetbrains.cmake.PARENTHESES':             CM,
    'com.jetbrains.cmake.BRACKETS':                CM,
    'com.jetbrains.cmake.SEMICOLON':               CM,

    # ---------------------------------------------------------------- assembly / disassembly (explicit)
    'ASM_LINE_COMMENT':    f'{ASM} comment.line',
    'ASM_BLOCK_COMMENT':   f'{ASM} comment.block',
    'ASM_MNEMONIC':        f'{ASM} keyword.operator.word.mnemonic.general-purpose.data-transfer.mov',
    'ASM_PREFIX':          f'{ASM} storage.modifier.prefix.asm.x86_64',
    'ASM_LABEL':           f'{ASM} entity.name.function.asm.x86_64',
    'ASM_DIRECTIVE_NAME':  ASM,
    'ASM_NUMBER':          f'{ASM} constant.numeric.hex.asm.x86_64',
    'ASM_PERCENT':         ASM,
    'ASM_AT':              ASM,
    'ASM_STAR':            ASM,
    'ASM_SIGN':            ASM,
    'ASM_COMMA':           ASM,
    'ASM_PARENTHESES':     ASM,
    'ASM_BRACES':          ASM,

    # ---------------------------------------------------------------- debugger memory view (hexdump)
    'MEMORY_LINE_COMMENT':   ('=', 'ASM_LINE_COMMENT'),
    'MEMORY_BLOCK_COMMENT':  ('=', 'ASM_BLOCK_COMMENT'),
    'MEMORY_LABEL':          ('=', 'ASM_LABEL'),
    'MEMORY_DIRECTIVE_NAME': ('=', 'ASM_DIRECTIVE_NAME'),
    'MEMORY_PREFIX':         ('=', 'ASM_PREFIX'),
    'MEMORY_NUMBER':         ('=', 'ASM_NUMBER'),
    'MEMORY_COMMA':          ('=', 'ASM_COMMA'),
    'MEMORY_BAD_CHARACTER':  ASM,
}

NOTES = {
    'OC.STRUCT_LIKE': 'explicit: cpptools emits `type` for classes/structs/unions/enums (its legend has no class/struct/enum type); class templates are templateType, same colour',
    'OC.NAMESPACE_LIKE': 'explicit: cpptools semantic namespace',
    'OC.CONCEPT': 'explicit: assumed cpptools `type` (legend: macro enumMember variable parameter type referenceType valueType function method property cliProperty event genericType templateFunction templateType namespace label customLiteral numberLiteral stringLiteral operatorOverload memberOperatorOverload newOperator; no concept type)',
    'OC.TYPEDEF': 'explicit: cpptools semantic type',
    'OC.TEMPLATE_TYPE': 'explicit: template type parameter, assumed cpptools `type` (legend has no typeParameter)',
    'OC.TEMPLATE_VALUE': 'explicit: non-type template parameter, assumed cpptools `parameter` (unverified; plain if cpptools emits nothing)',
    'OC.DEDUCTION_GUIDE': 'explicit: the guide is named after the class template -> cpptools templateType',
    'OC.GLOBAL_VARIABLE': 'explicit: cpptools semantic variable.global',
    'OC.EXTERN_VARIABLE': 'explicit: cpptools semantic variable.global',
    'OC.LOCAL_VARIABLE': 'explicit: cpptools semantic variable.local',
    'OC.CONSTANT': 'explicit: cpptools modifiers are only static/global/local (no readonly), so a constexpr global is variable.global (plain)',
    'OC.ENUM_CONST': 'explicit: cpptools semantic enumMember',
    'OC.PARAMETER': 'explicit: cpptools semantic parameter',
    'OC.STRUCT_FIELD': 'explicit: cpptools semantic property',
    'OC.FUNCTION_DECLARATION': 'explicit: cpptools semantic function',
    'OC.FUNCTION': 'explicit: cpptools semantic function',
    'OC.OVERLOADED_OPERATOR': 'explicit: cpptools semantic operatorOverload',
    'OC.LABEL': 'explicit: cpptools semantic label',
    'OC.MACRONAME': 'explicit: cpptools semantic macro',
    'OC.DEPENDENT_CODE': 'dependent names get no cpptools token: TextMate member access',
    'OC.CLASS_REFERENCE': 'Objective-C class reference: Foundation classes (NSString) are support.class in the objc grammar; user classes would be plain',
    'OC.CONDITIONALLY_NOT_COMPILED_V2': 'C grammar #if 0 branch (comment.block.preprocessor.if-branch); cpptools only dims other inactive regions',
    'com.jetbrains.cmake.COMMAND': 'explicit (twxs.cmake): built-in commands are keyword.cmake; user functions would be plain',
    'com.jetbrains.cmake.ARGUMENT_KEYWORD': 'explicit (twxs.cmake): VERSION/PUBLIC/PRIVATE match its target-property list (entity.source.cmake)',
    'com.jetbrains.cmake.ARGUMENT_LITERAL': 'explicit (twxs.cmake): unquoted arguments are plain',
    'com.jetbrains.cmake.ARGUMENT_LITERAL_CMAKE': 'explicit (twxs.cmake): CMAKE_* variables are variable.source.cmake',
    'com.jetbrains.cmake.NUMERIC_TEXT': 'explicit (twxs.cmake): no number scope, plain',
    'com.jetbrains.cmake.INVALID_STRING_ESCAPE': 'explicit (twxs.cmake): every backslash escape is constant.character.escape',
    'ASM_MNEMONIC': 'explicit (13xforever x86_64 asm): keyword.operator.word.mnemonic.*',
    'ASM_DIRECTIVE_NAME': 'explicit (13xforever x86_64 asm): only .globl/.extern are scoped; most directives (.cfi_*, .p2align) are plain',
    'ASM_PERCENT': 'explicit: the % of AT&T registers is plain (the register name itself has no IntelliJ key)',
    'MEMORY_LABEL': 'memory view (hexdump) has no VS Code equivalent: aliased to the assembly keys',
}
