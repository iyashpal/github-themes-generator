"""JetBrains Rider: C#, VB.NET (generic ReSharper keys), F#, Razor/Blazor + ASP.NET WebForms, XAML, T4,
IL viewer, Unity ShaderLab (+ HLSL via ReSharper C++), ReSharper C++ (Rider / CLion Nova), Godot GDScript
and Godot scenes (.tscn).

Key names. Rider's frontend keys for backend highlighters are "ReSharper." + the highlighter's Rider tag.
The tag comes from the language's RiderNamesProvider (C#: CSHARP_*, C++: CPP_*, XAML: XAML_*, ASP.NET:
ASP_NET_*, ShaderLab: "ReSharper.ShaderLab_*", hence the doubled prefix) or, without one, from the
highlighter id with the "ReSharper" prefix removed, '#' -> SHARP, upper-cased, non-alphanumerics -> '_'
("ReSharper F# Keyword" -> FSHARP_KEYWORD, "T4 Macro" -> T4_MACRO); see
JetBrains.Platform.TextControl.dll. Names were taken from the colour-page demo texts and RegisterHighlighter
attributes in lib/ReSharperHost + plugin DLLs, the frontend *TextAttributeKeys classes
(intellij.rider.languages / cpp.core / razor / fsharp jars), ReSharperAttributesIds and the bundled Rider
colour schemes (rider-theme-pack). GD_* / TSCN_* are plain frontend keys (rider-plugins-godot-gdscript).

VS Code side:
* C#: C# Dev Kit / Roslyn emits semantic tokens, so identifier keys use explicit `source.cs <fallback>`
  stacks: VS Code's standard table plus dotnet/vscode-csharp's semanticTokenScopes (field ->
  entity.name.variable.field.cs, delegate -> entity.name.type.delegate.cs, extensionMethod ->
  entity.name.function.extension.cs, typeParameter -> entity.name.type.type-parameter, constant ->
  variable.other.constant, operatorOverloaded -> entity.name.function.member.overload.cs, excludedCode ->
  support.other.excluded.cs, xmlDocComment* -> comment.documentation.*.cs). Keywords, strings, numbers,
  comments and punctuation are TextMate samples.
* Razor: the C# extension's Razor semantic tokens (razorTagHelperElement/Attribute,
  razorDirective, razorTransition, razorComment) for Razor-only constructs; HTML/C# parts from samples.
* F#, ShaderLab, XML (XAML): VS Code's bundled TextMate grammars.
* C++ (ReSharper C++ also highlights HLSL): bundled grammar + cpptools semantic tokens for identifiers.
* GDScript / .tscn: godot-tools 2.x grammars (source.gdscript / source.gdresource), not installed here,
  so explicit stacks copied from tokenising those grammars.
* T4, IL, WebForms (.aspx): no VS Code grammar -> aliases to the equivalent Razor / C# / core keys.
"""

SAMPLES = {
    'cs': ('source.cs', r'''using System;
namespace Demo.App;

/// <summary>Doc <see cref="Foo"/> text</summary>
[Obsolete("x")]
public static class Util { public static int Twice(this int x) => x * 2; }
public class Shape<T> : IShape where T : class
{
    private const int Limit = 10;
    private readonly string _name = "a\tb {0}";
    public double Area { get; set; }
    public Shape(string name)
    {
        // line comment
        /* block */
        var local = 3.5;
        _count = checked(mutable + 1);
        dynamic d = name;
        var z = d.Prop;
        if (local > 1) { return; }
        int[] arr = new int[2];
#if DEBUG
        Console.WriteLine(this, 1);
#endif
    }
}
'''),
    'razor': ('text.html.cshtml', r'''@page "/counter"
@model IndexModel
@* razor comment *@
<!-- html comment -->
<div class="row" id="main">
    <p>Count: @currentCount</p>
    @if (currentCount > 0)
    {
        <span>@Model.Name</span>
    }
</div>
@code {
    private int currentCount = 0;
}
'''),
    'fs': ('source.fsharp', r'''module Demo.App

open System
[<Literal>]
let Answer = 42
type Shape =
    | Circle of radius: float
let add x y = x + y
(* block comment *)
// line comment
let s = "text\n"
#if DEBUG
let ch = 'c'
#endif
let f = 3.14
'''),
    'xaml': ('text.xml', r'''<Page x:Class="Demo.MainPage"
      xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">
  <Grid x:Name="Root" Grid.Row="1" Background="{StaticResource Brush}" />
</Page>
'''),
    'shader': ('source.shaderlab', r'''Shader "Custom/Demo"
{
    Properties
    {
        [HDR] _Color ("Main Color", Color) = (1,1,1,1)
    }
    SubShader
    {
        Tags { "RenderType"="Opaque" }
        // line comment
        Cull Off
        Pass
        {
            CGPROGRAM
            #pragma multi_compile RED GREEN
            ENDCG
        }
    }
}
'''),
    'cpp': ('source.cpp', r'''#include "local.h"
#define SQUARE(x) ((x) * (x))
/// Doxygen \brief summary
namespace geo {
// line comment
/* block comment */
struct Point { int x; };
const char* text = "hi\n" R"(raw)";
char ch = 'c';
double ratio = 2.5 + 0x1F;
int compute(int value) {
    int local = value + SQUARE(2);
    int arr[2] = {0, 1};
    Point p; p.x = 1;
    if (local > 0) { return this_is_free(local, nullptr); }
    for (int i = 0; i < 3; ++i) { continue; }
    return local;
}
}
'''),
}

CS = 'source.cs '
CPP = 'source.cpp '
GD = 'source.gdscript '
TSCN = 'source.gdresource '

MAP = {
    # ---------------------------------------------------------------- C# (TextMate for tokens)
    'ReSharper.CSHARP_KEYWORD':                  ('cs', 'public static class'),
    'ReSharper.CSHARP_CONTROL_FLOW_KEYWORD':     ('cs', 'if (local'),
    'ReSharper.CSHARP_CONTROL_TRANSFER_KEYWORD': ('cs', 'return;'),
    'ReSharper.CSHARP_BUILTIN_TYPE_KEYWORD':     ('cs', 'int Twice'),
    'ReSharper.CSHARP_PREPROCESSOR_KEYWORD':     CS + 'entity.name.function.preprocessor',
    'ReSharper.CSHARP_STRING':                   ('cs', r'a\tb'),
    'ReSharper.CSHARP_ESCAPE_CHARACTER_1':       ('cs', r'\tb'),
    'ReSharper.CSHARP_ESCAPE_CHARACTER_2':       ('=', 'ReSharper.CSHARP_ESCAPE_CHARACTER_1'),
    'ReSharper.CSHARP_NUMBER':                   ('cs', '10;'),
    'ReSharper.CSHARP_LINE_COMMENT':             ('cs', '// line'),
    'ReSharper.CSHARP_BLOCK_COMMENT':            ('cs', '/* block'),
    'ReSharper.CSHARP_DOC_COMMENT':              CS + 'comment.documentation.cs',
    'ReSharper.CSHARP_DOC_COMMENT_TAG_NAME':     CS + 'comment.documentation.name.cs',
    'ReSharper.CSHARP_DOC_COMMENT_ATTRIBUTE':    CS + 'comment.documentation.attribute.name.cs',
    'ReSharper.CSHARP_DOC_COMMENT_ATTRIBUTE_VALUE': CS + 'comment.documentation.attribute.value.cs',
    'ReSharper.CSHARP_DOT':                      ('cs', '.App'),
    'ReSharper.CSHARP_COMMA':                    ('cs', ', 1)'),
    'ReSharper.CSHARP_SEMICOLON':                ('cs', ';\nnamespace'),
    'ReSharper.CSHARP_PARENTHESES':              ('cs', '("x")'),
    'ReSharper.CSHARP_BRACKETS':                 ('cs', '[Obsolete'),
    'ReSharper.CSHARP_BRACES':                   ('cs', '{ public static int'),
    'ReSharper.CSHARP_OPERATOR_SIGN':            ('cs', '* 2'),
    'ReSharper.CSHARP_OVERFLOW_CHECKED_OPERATION': ('cs', '+ 1)'),
    'ReSharper.CSHARP_ACCESSOR_IDENTIFIER':      ('cs', 'get;'),
    'ReSharper.CSHARP_PREPROCESSOR_INACTIVE_BRANCH': CS + 'support.other.excluded.cs',
    # ---------------------------------------------------------------- C# identifiers (Roslyn semantic)
    'ReSharper.CSHARP_CLASS_IDENTIFIER':         CS + 'entity.name.type.class',
    'ReSharper.CSHARP_STATIC_CLASS_IDENTIFIER':  CS + 'entity.name.type.class',
    'ReSharper.CSHARP_RECORD_IDENTIFIER':        CS + 'entity.name.type.class',
    'ReSharper.CSHARP_ATTRIBUTE_IDENTIFIER':     CS + 'entity.name.type.class',
    'ReSharper.CSHARP_ALIAS_IDENTIFIER':         CS + 'entity.name.type.class',
    'ReSharper.CSHARP_STRUCT_IDENTIFIER':        CS + 'entity.name.type.struct',
    'ReSharper.CSHARP_RECORD_STRUCT_IDENTIFIER': CS + 'entity.name.type.struct',
    'ReSharper.CSHARP_INTERFACE_IDENTIFIER':     CS + 'entity.name.type.interface',
    'ReSharper.CSHARP_ENUM_IDENTIFIER':          CS + 'entity.name.type.enum',
    'ReSharper.CSHARP_DELEGATE_IDENTIFIER':      CS + 'entity.name.type.delegate.cs',
    'ReSharper.CSHARP_TYPE_PARAMETER_IDENTIFIER': CS + 'entity.name.type.type-parameter',
    'ReSharper.CSHARP_NAMESPACE_IDENTIFIER':     CS + 'entity.name.namespace',
    'ReSharper.CSHARP_METHOD_IDENTIFIER':        CS + 'entity.name.function.member',
    'ReSharper.CSHARP_METHOD_CALL_IDENTIFIER':   CS + 'entity.name.function.member',
    'ReSharper.CSHARP_METHOD_DECLARATION_IDENTIFIER': CS + 'entity.name.function.member',
    'ReSharper.CSHARP_STATIC_METHOD_CALL_IDENTIFIER': CS + 'entity.name.function.member',
    'ReSharper.CSHARP_STATIC_METHOD_IDENTIFIER': CS + 'entity.name.function.member',
    'ReSharper.CSHARP_STATIC_METHOD_DECLARATION_IDENTIFIER': CS + 'entity.name.function.member',
    'ReSharper.CSHARP_LOCAL_FUNCTION_IDENTIFIER': CS + 'entity.name.function.member',
    'ReSharper.CSHARP_EXTENSION_METHOD_IDENTIFIER': CS + 'entity.name.function.extension.cs',
    'ReSharper.CSHARP_EXTENSION_METHOD_CALL_IDENTIFIER': CS + 'entity.name.function.extension.cs',
    'ReSharper.CSHARP_EXTENSION_METHOD_DECLARATION_IDENTIFIER': CS + 'entity.name.function.extension.cs',
    'ReSharper.CSHARP_OVERLOADED_OPERATOR':      CS + 'entity.name.function.member.overload.cs',
    'ReSharper.CSHARP_OPERATOR_IDENTIFIER':      CS + 'entity.name.function.member.overload.cs',
    'ReSharper.CSHARP_FIELD_IDENTIFIER':         CS + 'entity.name.variable.field.cs',
    'ReSharper.CSHARP_STATIC_FIELD_IDENTIFIER':  CS + 'entity.name.variable.field.cs',
    'ReSharper.CSHARP_TUPLE_COMPONENT_NAME':     CS + 'entity.name.variable.field.cs',
    'ReSharper.CSHARP_CONSTANT_IDENTIFIER':      CS + 'variable.other.constant',
    'ReSharper.CSHARP_PROPERTY_IDENTIFIER':      CS + 'variable.other.property',
    'ReSharper.CSHARP_STATIC_PROPERTY_IDENTIFIER': CS + 'variable.other.property',
    'ReSharper.CSHARP_EVENT_IDENTIFIER':         CS + 'variable.other.event',
    'ReSharper.CSHARP_LOCAL_VARIABLE_IDENTIFIER': CS + 'variable.other.readwrite',
    'ReSharper.CSHARP_MUTABLE_LOCAL_VARIABLE_IDENTIFIER': CS + 'variable.other.readwrite',
    'ReSharper.CSHARP_PARAMETER_IDENTIFIER':     CS + 'variable.parameter',
    'ReSharper.CSHARP_PRIMARY_CONSTRUCTOR_PARAMETER_IDENTIFIER': CS + 'variable.parameter',
    'ReSharper.CSHARP_PRIMARY_CONSTRUCTOR_PARAMETER_CAPTURED_IDENTIFIER': CS + 'variable.parameter',
    'ReSharper.CSHARP_LATE_BOUND_IDENTIFIER':    ('cs', 'Prop;'),
    # ---------------------------------------------------------------- generic ReSharper keys (VB.NET and
    # other .NET languages fall back to these; C# keys above inherit them in Rider)
    'ReSharper.KEYWORD':                         ('=', 'ReSharper.CSHARP_KEYWORD'),
    'ReSharper.CONTROL_FLOW_KEYWORD':            ('=', 'ReSharper.CSHARP_CONTROL_FLOW_KEYWORD'),
    'ReSharper.CONTROL_TRANSFER_KEYWORD':        ('=', 'ReSharper.CSHARP_CONTROL_TRANSFER_KEYWORD'),
    'ReSharper.BUILTIN_TYPE_KEYWORD':            ('=', 'ReSharper.CSHARP_BUILTIN_TYPE_KEYWORD'),
    'ReSharper.PREPROCESSOR_KEYWORD':            ('=', 'ReSharper.CSHARP_PREPROCESSOR_KEYWORD'),
    'ReSharper.INACTIVE_PREPROCESSOR_BRANCH':    ('=', 'ReSharper.CSHARP_PREPROCESSOR_INACTIVE_BRANCH'),
    'ReSharper.STRING':                          ('=', 'ReSharper.CSHARP_STRING'),
    'ReSharper.VERBATIM_STRING':                 ('=', 'ReSharper.CSHARP_STRING'),
    'ReSharper.SINGLE_QUOTED_STRING':            ('=', 'ReSharper.CSHARP_STRING'),
    'ReSharper.CHARACTER':                       ('=', 'ReSharper.CSHARP_STRING'),
    'ReSharper.NUMBER':                          ('=', 'ReSharper.CSHARP_NUMBER'),
    'ReSharper.LINE_COMMENT':                    ('=', 'ReSharper.CSHARP_LINE_COMMENT'),
    'ReSharper.MULTILINE_COMMENT':               ('=', 'ReSharper.CSHARP_BLOCK_COMMENT'),
    'ReSharper.DOC_COMMENT_TAG':                 ('=', 'ReSharper.CSHARP_DOC_COMMENT_ATTRIBUTE'),
    'ReSharper.DOC_COMMENT_TAG_VALUE':           ('=', 'ReSharper.CSHARP_DOC_COMMENT_ATTRIBUTE_VALUE'),
    'ReSharper.DOC_COMMENT_MARKUP':              ('=', 'ReSharper.CSHARP_DOC_COMMENT_TAG_NAME'),
    'ReSharper.PUNCTUATION':                     ('=', 'ReSharper.CSHARP_SEMICOLON'),
    'ReSharper.IDENTIFIER':                      CS + 'variable.other.readwrite',
    'ReSharper.STRING_ESCAPE_CHARACTER_2':       ('=', 'ReSharper.CSHARP_ESCAPE_CHARACTER_1'),
    'ReSharper.FORMAT_STRING_ITEM':              ('cs', '{0}"'),
    'ReSharper.FORMAT_STRING_ITEM_2':            ('=', 'ReSharper.FORMAT_STRING_ITEM'),
    'ReSharper.PATH_IDENTIFIER':                 ('=', 'ReSharper.CSHARP_STRING'),
    'ReSharper.NAMESPACE_IDENTIFIER':            ('=', 'ReSharper.CSHARP_NAMESPACE_IDENTIFIER'),
    'ReSharper.STATIC_CLASS_IDENTIFIER':         ('=', 'ReSharper.CSHARP_STATIC_CLASS_IDENTIFIER'),
    'ReSharper.STRUCT_IDENTIFIER':               ('=', 'ReSharper.CSHARP_STRUCT_IDENTIFIER'),
    'ReSharper.ENUM_IDENTIFIER':                 ('=', 'ReSharper.CSHARP_ENUM_IDENTIFIER'),
    'ReSharper.DELEGATE_IDENTIFIER':             ('=', 'ReSharper.CSHARP_DELEGATE_IDENTIFIER'),
    'ReSharper.TYPE_PARAMETER_IDENTIFIER':       ('=', 'ReSharper.CSHARP_TYPE_PARAMETER_IDENTIFIER'),
    'ReSharper.EXTENSION_METHOD_IDENTIFIER':     ('=', 'ReSharper.CSHARP_EXTENSION_METHOD_IDENTIFIER'),
    'ReSharper.OPERATOR_IDENTIFIER':             ('=', 'ReSharper.CSHARP_OVERLOADED_OPERATOR'),
    'ReSharper.PROPERTY_IDENTIFIER':             ('=', 'ReSharper.CSHARP_PROPERTY_IDENTIFIER'),
    'ReSharper.EVENT_IDENTIFIER':                ('=', 'ReSharper.CSHARP_EVENT_IDENTIFIER'),
    'ReSharper.MUTABLE_LOCAL_VARIABLE_IDENTIFIER': ('=', 'ReSharper.CSHARP_MUTABLE_LOCAL_VARIABLE_IDENTIFIER'),
    'ReSharper.LATE_BOUND_IDENTIFIER':           ('=', 'ReSharper.CSHARP_LATE_BOUND_IDENTIFIER'),
    # ---------------------------------------------------------------- ASP.NET MVC references / routes (in strings)
    'ReSharper.ASP_NET_MVC_ACTION':              ('=', 'ReSharper.CSHARP_STRING'),
    'ReSharper.ASP_NET_MVC_AREA':                ('=', 'ReSharper.CSHARP_STRING'),
    'ReSharper.ASP_NET_MVC_CONTROLLER':          ('=', 'ReSharper.CSHARP_STRING'),
    'ReSharper.ASP_NET_MVC_VIEW':                ('=', 'ReSharper.CSHARP_STRING'),
    'ReSharper.ASP_NET_MVC_VIEW_COMPONENT':      ('=', 'ReSharper.CSHARP_STRING'),
    'ReSharper.ASP_NET_ROUTE_TEMPLATE_PARAMETER': ('=', 'ReSharper.CSHARP_STRING'),
    'ReSharper.ASP_NET_ROUTE_TEMPLATE_TOKEN_SUBSTITUTION': ('=', 'ReSharper.CSHARP_STRING'),
    # ---------------------------------------------------------------- Razor / Blazor
    'ReSharper.ASP_NET_RAZOR_KEYWORD':           'text.html.cshtml keyword.control.razor.directive',
    'ReSharper.ASP_NET_RAZOR_CODE_BLOCK_TAG':    'text.html.cshtml keyword.control.razor.transition',
    'ReSharper.ASP_NET_RAZOR_TRANSITION_ESCPAE': 'text.html.cshtml keyword.control.razor.transition',
    'ReSharper.ASP_NET_RAZOR_COMMENT':           'text.html.cshtml comment.block.razor',
    'ReSharper.ASP_NET_RAZOR_TAG_HELPER_ELEMENT': 'text.html.cshtml entity.name.class.element.taghelper',
    'ReSharper.ASP_NET_RAZOR_TAG_HELPER_ATTRIBUTE': 'text.html.cshtml entity.name.class.attribute.taghelper',
    'ReSharper.HTML_ID_ATTRIBUTE':               ('razor', 'main"'),
    # ---------------------------------------------------------------- ASP.NET WebForms (.aspx/.ascx; no VS Code grammar)
    'ReSharper.ASP_NET_BLOCK_TAG':               ('=', 'ReSharper.ASP_NET_RAZOR_CODE_BLOCK_TAG'),
    'ReSharper.ASP_NET_DIRECTIVE_NAME':          ('=', 'ReSharper.ASP_NET_RAZOR_KEYWORD'),
    'ReSharper.ASP_NET_ATTRIBUTE_NAME':          ('razor', 'class="row"'),
    'ReSharper.ASP_NET_ATTRIBUTE_VALUE':         ('razor', 'row"'),
    'ReSharper.ASP_NET_RUN_AT_ATTRIBUTE':        ('=', 'ReSharper.ASP_NET_ATTRIBUTE_NAME'),
    'ReSharper.ASP_NET_RUNAT_ATTRIBUTE':         ('=', 'ReSharper.ASP_NET_ATTRIBUTE_NAME'),
    'ReSharper.ASP_NET_COMMENT':                 ('razor', '<!--'),
    # ---------------------------------------------------------------- T4 (no VS Code grammar)
    'ReSharper.T4_DIRECTIVE':                    ('=', 'ReSharper.ASP_NET_RAZOR_KEYWORD'),
    'ReSharper.T4_DIRECTIVE_ATTRIBUTE':          ('=', 'ReSharper.ASP_NET_ATTRIBUTE_NAME'),
    'ReSharper.T4_ATTRIBUTE_VALUE':              ('=', 'ReSharper.ASP_NET_ATTRIBUTE_VALUE'),
    'ReSharper.T4_MACRO':                        ('=', 'ReSharper.ASP_NET_ATTRIBUTE_VALUE'),
    'ReSharper.T4_ENVIRONMENT_VARIABLE':         ('=', 'ReSharper.ASP_NET_ATTRIBUTE_VALUE'),
    # ---------------------------------------------------------------- XAML (VS Code: XML grammar)
    'ReSharper.XAML_CLASS':                      ('xaml', 'Page x:'),
    'ReSharper.XAML_NAMESPACE_ALIAS':            ('xaml', 'x:Class'),
    'ReSharper.XAML_PREDEFINED_ELEMENT':         ('xaml', 'Class='),
    'ReSharper.XAML_PROPERTY_IDENTIFIER':        ('xaml', 'Background='),
    'ReSharper.XAML_ATTACHED_PROPERTY_IDENTIFIER': ('xaml', 'Grid.Row'),
    'ReSharper.XAML_FIELD':                      ('xaml', 'Root"'),
    'ReSharper.XAML_TEMPLATE_FIELD':             ('=', 'ReSharper.XAML_FIELD'),
    'ReSharper.XAML_IMPLICIT_FIELD':             ('=', 'ReSharper.XAML_FIELD'),
    'ReSharper.XAML_STYLE_CLASS':                ('=', 'ReSharper.XAML_FIELD'),
    'ReSharper.XAML_RESOURCE':                   ('xaml', '{StaticResource'),
    # ---------------------------------------------------------------- IL viewer (no VS Code grammar)
    'ReSharper.IL_KEYWORD':                      ('=', 'DEFAULT_KEYWORD'),
    'ReSharper.IL_INSTRUCTION':                  ('=', 'DEFAULT_KEYWORD'),
    'ReSharper.IL_COMMENT':                      ('=', 'DEFAULT_LINE_COMMENT'),
    'ReSharper.IL_STRING_LITERAL':               ('=', 'DEFAULT_STRING'),
    'ReSharper.IL_CONSTANT_LITERAL':             ('=', 'DEFAULT_NUMBER'),
    'ReSharper.IL_CODE_LABEL':                   ('=', 'DEFAULT_LABEL'),
    'ReSharper.IL_TARGET_CODE_LABEL':            ('=', 'DEFAULT_LABEL'),
    'ReSharper.IL_QUALIFIED_NAME':               ('=', 'DEFAULT_CLASS_REFERENCE'),
    'ReSharper.IL_METHOD_IDENTIFIER':            ('=', 'DEFAULT_INSTANCE_METHOD'),
    'ReSharper.IL_PARAMETER_IDENTIFIER':         ('=', 'DEFAULT_PARAMETER'),
    'ReSharper.IL_IDENTIFIER':                   ('=', 'DEFAULT_IDENTIFIER'),
    # ---------------------------------------------------------------- F# (bundled TextMate grammar)
    'ReSharper.FSHARP_KEYWORD':                  ('fs', 'let add'),
    'ReSharper.FSHARP_PREPROCESSOR_KEYWORD':     ('fs', '#if'),
    'ReSharper.FSHARP_PREPROCESSOR_INACTIVE_BRANCH': 'source.fsharp',
    'ReSharper.FSHARP_STRING':                   ('fs', 'text'),
    'ReSharper.FSHARP_ESCAPE_CHARACTER_1':       ('fs', r'\n"'),
    'ReSharper.FSHARP_ESCAPE_CHARACTER_2':       ('=', 'ReSharper.FSHARP_ESCAPE_CHARACTER_1'),
    'ReSharper.FSHARP_NUMBER':                   ('fs', '42'),
    'ReSharper.FSHARP_LINE_COMMENT':             ('fs', '// line'),
    'ReSharper.FSHARP_BLOCK_COMMENT':            ('fs', '(* block'),
    'ReSharper.FSHARP_NAMESPACE_IDENTIFIER':     ('fs', 'System'),
    'ReSharper.FSHARP_MODULE_IDENTIFIER':        ('fs', 'Demo.App'),
    'ReSharper.FSHARP_CLASS_IDENTIFIER':         ('fs', 'Shape ='),
    'ReSharper.FSHARP_STATIC_CLASS_IDENTIFIER':  ('=', 'ReSharper.FSHARP_CLASS_IDENTIFIER'),
    'ReSharper.FSHARP_INTERFACE_IDENTIFIER':     ('=', 'ReSharper.FSHARP_CLASS_IDENTIFIER'),
    'ReSharper.FSHARP_DELEGATE_IDENTIFIER':      ('=', 'ReSharper.FSHARP_CLASS_IDENTIFIER'),
    'ReSharper.FSHARP_STRUCT_IDENTIFIER':        ('=', 'ReSharper.FSHARP_CLASS_IDENTIFIER'),
    'ReSharper.FSHARP_ENUM_IDENTIFIER':          ('=', 'ReSharper.FSHARP_CLASS_IDENTIFIER'),
    'ReSharper.FSHARP_UNION_IDENTIFIER':         ('=', 'ReSharper.FSHARP_CLASS_IDENTIFIER'),
    'ReSharper.FSHARP_RECORD_IDENTIFIER':        ('=', 'ReSharper.FSHARP_CLASS_IDENTIFIER'),
    'ReSharper.FSHARP_STRUCT_RECORD_IDENTIFIER': ('=', 'ReSharper.FSHARP_CLASS_IDENTIFIER'),
    'ReSharper.FSHARP_STRUCT_UNION_IDENTIFIER':  ('=', 'ReSharper.FSHARP_CLASS_IDENTIFIER'),
    'ReSharper.FSHARP_CLASS_EXTENSION_IDENTIFIER': ('=', 'ReSharper.FSHARP_CLASS_IDENTIFIER'),
    'ReSharper.FSHARP_STRUCT_EXTENSION_IDENTIFIER': ('=', 'ReSharper.FSHARP_CLASS_IDENTIFIER'),
    'ReSharper.FSHARP_TYPE_PARAMETER_IDENTIFIER': ('fs', 'float\n'),
    'ReSharper.FSHARP_UNIT_OF_MEASURE_IDENTIFIER': ('=', 'ReSharper.FSHARP_TYPE_PARAMETER_IDENTIFIER'),
    'ReSharper.FSHARP_UNION_CASE_IDENTIFIER':    ('fs', 'Circle'),
    'ReSharper.FSHARP_STRUCT_UNION_CASE_IDENTIFIER': ('=', 'ReSharper.FSHARP_UNION_CASE_IDENTIFIER'),
    'ReSharper.FSHARP_ACTIVE_PATTERN_CASE_IDENTIFIER': ('=', 'ReSharper.FSHARP_UNION_CASE_IDENTIFIER'),
    'ReSharper.FSHARP_LITERAL_IDENTIFIER':       ('fs', 'Answer'),
    'ReSharper.FSHARP_VALUE_IDENTIFIER':         ('fs', 's ='),
    'ReSharper.FSHARP_MUTABLE_VALUE_IDENTIFIER': ('=', 'ReSharper.FSHARP_VALUE_IDENTIFIER'),
    'ReSharper.FSHARP_FIELD_IDENTIFIER':         ('=', 'ReSharper.FSHARP_VALUE_IDENTIFIER'),
    'ReSharper.FSHARP_PROPERTY_IDENTIFIER':      ('=', 'ReSharper.FSHARP_VALUE_IDENTIFIER'),
    'ReSharper.FSHARP_EXTENSION_PROPERTY_IDENTIFIER': ('=', 'ReSharper.FSHARP_VALUE_IDENTIFIER'),
    'ReSharper.FSHARP_EVENT_IDENTIFIER':         ('=', 'ReSharper.FSHARP_VALUE_IDENTIFIER'),
    'ReSharper.FSHARP_FUNCTION_IDENTIFIER':      ('fs', 'add x'),
    'ReSharper.FSHARP_MUTABLE_FUNCTION_IDENTIFIER': ('=', 'ReSharper.FSHARP_FUNCTION_IDENTIFIER'),
    'ReSharper.FSHARP_METHOD_IDENTIFIER':        ('=', 'ReSharper.FSHARP_FUNCTION_IDENTIFIER'),
    'ReSharper.FSHARP_EXTENSION_METHOD_IDENTIFIER': ('=', 'ReSharper.FSHARP_FUNCTION_IDENTIFIER'),
    'ReSharper.FSHARP_OPERATOR_IDENTIFIER':      ('fs', '+ y'),
    'ReSharper.FSHARP_PARAMETER_IDENTIFIER':     ('fs', 'radius'),
    'ReSharper.FSHARP_COMPUTATION_EXPRESSION_IDENTIFIER': ('=', 'ReSharper.FSHARP_KEYWORD'),
    # ---------------------------------------------------------------- Unity ShaderLab (bundled grammar)
    'ReSharper.ReSharper.ShaderLab_KEYWORD':         ('shader', 'SubShader'),
    'ReSharper.ReSharper.ShaderLab_COMMAND':         ('shader', 'Cull'),
    'ReSharper.ReSharper.ShaderLab_BLOCK_COMMAND':   ('shader', 'Tags'),
    'ReSharper.ReSharper.ShaderLab_COMMAND_ARGUMENT': ('shader', 'Off'),
    'ReSharper.ReSharper.ShaderLab_PROPERTY_NAME':   ('shader', '_Color'),
    'ReSharper.ReSharper.ShaderLab_PROPERTY_TYPE':   ('shader', 'Color)'),
    'ReSharper.ReSharper.ShaderLab_PROPERTY_ATTRIBUTE': ('shader', 'HDR'),
    'ReSharper.ReSharper.ShaderLab_NUMBER':          ('shader', '1,1'),
    'ReSharper.ReSharper.ShaderLab_STRING':          ('shader', 'Main Color'),
    'ReSharper.ReSharper.ShaderLab_LINE_COMMENT':    ('shader', '// line'),
    'ReSharper.ReSharper.ShaderLab_BLOCK_COMMENT':   ('=', 'ReSharper.ReSharper.ShaderLab_LINE_COMMENT'),
    'ReSharper.ReSharper.ShaderLab_ENABLED_SHADER_KEYWORD': 'source.shaderlab meta.cgblock',
    'ReSharper.ReSharper.ShaderLab_IMPLICITLY_ENABLED_SHADER_KEYWORD': 'source.shaderlab meta.cgblock',
    'ReSharper.ReSharper.ShaderLab_DISABLED_SHADER_KEYWORD': 'source.shaderlab meta.cgblock',
    'ReSharper.ReSharper.ShaderLab_SUPPRESSED_SHADER_KEYWORD': 'source.shaderlab meta.cgblock',
    # Unity 6 block shaders (.shader blocks; no VS Code grammar): RegisterHighlighter ids "ReSharper BlockShaders *"
    'ReSharper.BLOCK_SHADERS_KEYWORD':               ('=', 'ReSharper.ReSharper.ShaderLab_KEYWORD'),
    'ReSharper.BLOCK_SHADERS_IDENTIFIER':            'source.shaderlab',
    # ---------------------------------------------------------------- ReSharper C++ (Rider, CLion Nova; also HLSL)
    'ReSharper.CPP_KEYWORD':                     ('cpp', 'namespace geo'),
    'ReSharper.CPP_CONTROL_FLOW_KEYWORD':        ('cpp', 'if (local'),
    'ReSharper.CPP_CONTROL_TRANSFER_KEYWORD':    ('cpp', 'continue'),
    'ReSharper.CPP_BUILTIN_TYPE_KEYWORD':        ('cpp', 'char ch'),
    'ReSharper.CPP_THIS_KEYWORD':                ('cpp', 'nullptr'),
    'ReSharper.CPP_DIRECTIVE':                   ('cpp', 'include'),
    'ReSharper.CPP_HEADER_PATH':                 ('cpp', 'local.h'),
    'ReSharper.CPP_LINE_COMMENT':                ('cpp', '// line'),
    'ReSharper.CPP_BLOCK_COMMENT':               ('cpp', '/* block'),
    'ReSharper.CPP_DOXYGEN_TEXT':                ('cpp', ' Doxygen'),
    'ReSharper.CPP_DOXYGEN_COMMENT':             ('=', 'ReSharper.CPP_DOXYGEN_TEXT'),
    'ReSharper.CPP_DOXYGEN_COMMAND':             ('cpp', r'\brief'),
    'ReSharper.CPP_DOXYGEN_COMMAND_VALUE':       ('cpp', ' summary'),
    'ReSharper.CPP_STRING_LITERAL':              ('cpp', 'hi'),
    'ReSharper.CPP_RAW_STRING_LITERAL':          ('cpp', 'raw'),
    'ReSharper.CPP_CHARACTER_LITERAL':           ('cpp', "'c'"),
    'ReSharper.CPP_VALID_STRING_ESCAPE':         ('cpp', r'\n"'),
    'ReSharper.CPP_INVALID_STRING_ESCAPE':       ('=', 'DEFAULT_INVALID_STRING_ESCAPE'),
    'ReSharper.CPP_INTEGER_LITERAL':             ('cpp', '3; ++i'),
    'ReSharper.CPP_FLOAT_LITERAL':               ('cpp', '2.5'),
    'ReSharper.CPP_OPERATOR_SIGN':               ('cpp', '+ 0x1F'),
    'ReSharper.CPP_DOT':                         ('cpp', '.x = 1'),
    'ReSharper.CPP_COMMA':                       ('cpp', ', nullptr'),
    'ReSharper.CPP_SEMICOLON':                   ('cpp', '; };'),
    'ReSharper.CPP_PARENTHESES':                 ('cpp', '(int value'),
    'ReSharper.CPP_BRACKETS':                    ('cpp', '[2]'),
    'ReSharper.CPP_BRACES':                      ('cpp', '{0, 1}'),
    'ReSharper.CPP_PREPROCESSOR_INACTIVE_BRANCH': 'source.cpp',
    'ReSharper.CPP_NAMESPACE_IDENTIFIER':        CPP + 'entity.name.namespace.cpp',
    'ReSharper.CPP_CLASS_IDENTIFIER':            CPP + 'entity.name.type.class.cpp',
    'ReSharper.CPP_STRUCT_IDENTIFIER':           CPP + 'entity.name.type.class.cpp',
    'ReSharper.CPP_UNION_IDENTIFIER':            CPP + 'entity.name.type.class.cpp',
    'ReSharper.CPP_ENUM_IDENTIFIER':             CPP + 'entity.name.type.enum.cpp',
    'ReSharper.CPP_TYPEDEF_IDENTIFIER':          CPP + 'entity.name.type.cpp',
    'ReSharper.CPP_LOCAL_TYPEDEF_IDENTIFIER':    CPP + 'entity.name.type.cpp',
    'ReSharper.CPP_CONCEPT_IDENTIFIER':          CPP + 'entity.name.type.cpp',
    'ReSharper.CPP_TEMPLATE_PARAMETER_IDENTIFIER': CPP + 'entity.name.type.parameter',
    'ReSharper.CPP_NON_TYPE_TEMPLATE_PARAMETER_IDENTIFIER': CPP + 'entity.name.type.parameter',
    'ReSharper.CPP_DEPENDENT_NAME_IDENTIFIER':   CPP + 'entity.name.type.cpp',
    'ReSharper.CPP_GLOBAL_FUNCTION_IDENTIFIER':  CPP + 'entity.name.function.cpp',
    'ReSharper.CPP_GLOBAL_FUNCTION_USAGE_IDENTIFIER': CPP + 'entity.name.function.cpp',
    'ReSharper.CPP_DEDUCTION_GUIDE_IDENTIFIER':  CPP + 'entity.name.function.cpp',
    'ReSharper.CPP_MEMBER_FUNCTION_IDENTIFIER':  CPP + 'entity.name.function.member.cpp',
    'ReSharper.CPP_MEMBER_FUNCTION_USAGE_IDENTIFIER': CPP + 'entity.name.function.member.cpp',
    'ReSharper.CPP_STATIC_MEMBER_FUNCTION_IDENTIFIER': CPP + 'entity.name.function.member.static.cpp',
    'ReSharper.CPP_STATIC_MEMBER_FUNCTION_USAGE_IDENTIFIER': CPP + 'entity.name.function.member.static.cpp',
    'ReSharper.CPP_OVERLOADED_OPERATOR_IDENTIFIER': CPP + 'entity.name.function.operator.cpp',
    'ReSharper.CPP_PREPROCESSOR_MACRO_IDENTIFIER': CPP + 'entity.name.function.preprocessor.cpp',
    'ReSharper.CPP_PREPROCESSOR_MACRO_PARAMETER_IDENTIFIER': ('cpp', 'x) (('),
    'ReSharper.CPP_UE4_REFLECTION_SPECIFIER_IDENTIFIER': CPP + 'entity.name.function.preprocessor.cpp',
    'ReSharper.CPP_CLASS_FIELD_IDENTIFIER':      CPP + 'variable.other.property.cpp',
    'ReSharper.CPP_STRUCT_FIELD_IDENTIFIER':     CPP + 'variable.other.property.cpp',
    'ReSharper.CPP_UNION_MEMBER_IDENTIFIER':     CPP + 'variable.other.property.cpp',
    'ReSharper.CPP_STATIC_FIELD_IDENTIFIER':     CPP + 'variable.other.property.static.cpp',
    'ReSharper.CPP_ENUM_ENUMERATOR_IDENTIFIER':  CPP + 'variable.other.enummember.cpp',
    'ReSharper.CPP_CONSTANT_IDENTIFIER':         CPP + 'variable.other.constant.cpp',
    'ReSharper.CPP_GLOBAL_VARIABLE_IDENTIFIER':  CPP + 'variable.other.global.cpp',
    'ReSharper.CPP_LOCAL_VARIABLE_IDENTIFIER':   CPP + 'variable.other.local.cpp',
    'ReSharper.CPP_PARAMETER_VARIABLE_IDENTIFIER': CPP + 'variable.parameter.cpp',
    'ReSharper.CPP_MODULE_IDENTIFIER':           CPP + 'entity.name.namespace.cpp',
    # ---------------------------------------------------------------- Godot GDScript (godot-tools grammar, explicit)
    'GD_KEYWORD':                  GD + 'keyword.language.gdscript',
    'GD_FLOW_KEYWORDS':            GD + 'keyword.control.flow.gdscript',
    'GD_ANNOTATION':               GD + 'entity.name.function.decorator.gdscript',
    'GD_METHOD_DECLARATION':       GD + 'meta.function.gdscript entity.name.function.gdscript',
    'GD_METHOD_CALL':              GD + 'meta.function-call.gdscript entity.name.function.gdscript',
    'GD_STATIC_METHOD_CALL':       GD + 'meta.function-call.gdscript entity.name.function.gdscript',
    'GD_GLOBAL_FUNCTION':          GD + 'meta.function-call.gdscript entity.name.function.gdscript',
    'GD_CLASS_TYPE':               GD + 'entity.name.type.class.gdscript',
    'GD_ENGINE_TYPE':              GD + 'entity.name.type.class.gdscript',
    'GD_BASE_TYPE':                GD + 'entity.name.type.class.builtin.gdscript',
    'GD_GLOBAL_VARIABLE_AUTOLOAD': GD + 'entity.name.type.class.gdscript',
    'GD_GLOBAL_VARIABLE_BUILT_IN': GD + 'entity.name.type.class.gdscript',
    'GD_MEMBER':                   GD + 'variable.other.property.gdscript',
    'GD_NUMBER':                   GD + 'constant.numeric.integer.gdscript',
    'GD_STRING':                   GD + 'string.quoted.gdscript',
    'GD_STRING_FORMAT':            GD + 'string.quoted.gdscript meta.format.percent.gdscript constant.character.format.placeholder.other.gdscript',
    'GD_STRING_NAME':              GD + 'string.quoted.gdscript meta.literal.nodepath.gdscript constant.character.escape.gdscript',
    'GD_NODE_STRING_PATH':         GD + 'string.quoted.gdscript meta.literal.nodepath.gdscript constant.character.escape.gdscript',
    'GD_NODE_PATH':                GD + 'meta.literal.nodepath.bare.gdscript constant.character.escape.gdscript',
    'GD_COMMENT':                  GD + 'comment.line.number-sign.gdscript',
    'GD_DOC_COMMENT':              GD + 'comment.line.number-sign.gdscript',
    'GD_NOTE':                     GD + 'comment.line.number-sign.gdscript',
    'GD_WARNING':                  GD + 'comment.line.number-sign.gdscript',
    'GD_DANGER':                   GD + 'comment.line.number-sign.gdscript',
    'GD_BAD_CHARACTER':            GD.strip(),
    # ---------------------------------------------------------------- Godot scenes / resources (.tscn/.tres)
    'TSCN_NODE_RESOURCE':          TSCN + 'keyword.control.gdresource',
    'TSCN_NODE_TYPE':              TSCN + 'support.class.library.gdresource',
    'TSCN_ATTRIBUTES':             TSCN + 'variable.other.property.gdresource',
    'TSCN_ATTRIBUTE_VALUES':       TSCN + 'constant.numeric.float.gdresource',
    'TSCN_STRING':                 TSCN + 'string.quoted.double.basic.line.gdresource',
    'TSCN_RES_STRING':             TSCN + 'support.function.any-method.gdresource',
    'TSCN_MEMBER_REF':             TSCN + 'string.quoted.double.basic.line.gdresource',
    'TSCN_SYNTAX_TOKENS':          TSCN + 'punctuation.definition.keyValue.gdresource',
}

NOTES = {
    'ReSharper.CSHARP_CLASS_IDENTIFIER': 'C# identifiers: explicit Roslyn semantic-token fallback scopes (C# Dev Kit)',
    'ReSharper.CSHARP_DOC_COMMENT_TAG_NAME': 'Roslyn classifies XML doc parts (xmlDocCommentName etc.) -> comment.documentation.*.cs, so VS Code shows them in comment colour',
    'ReSharper.CSHARP_PREPROCESSOR_INACTIVE_BRANCH': 'Roslyn excludedCode -> support.other.excluded.cs (explicit); resolves to the theme support colour',
    'ReSharper.CSHARP_ACCESSOR_IDENTIFIER': 'get/set accessors: Roslyn/TextMate keyword, not a method',
    'ReSharper.CSHARP_TUPLE_COMPONENT_NAME': 'Roslyn classifies tuple element names as fields (explicit)',
    'ReSharper.CSHARP_LATE_BOUND_IDENTIFIER': 'dynamic member: Roslyn emits no semantic token, TextMate property access',
    'ReSharper.CSHARP_ALIAS_IDENTIFIER': 'Roslyn colours aliases as their target type',
    'ReSharper.CSHARP_PREPROCESSOR_KEYWORD': 'Roslyn maps PreprocessorKeyword -> semantic type macro -> entity.name.function.preprocessor (explicit); it overrides TextMate keyword.preprocessor',
    'ReSharper.CSHARP_METHOD_DECLARATION_IDENTIFIER': 'current backend ids (CSharpHighlightingAttributeIds METHOD_DECLARATION/_CALL, STATIC_*, EXTENSION_*); CSHARP_METHOD_IDENTIFIER / CSHARP_STATIC_METHOD_IDENTIFIER / CSHARP_EXTENSION_METHOD_IDENTIFIER are the frontend/bundled-scheme names and are kept too',
    'ReSharper.FORMAT_STRING_ITEM': 'format placeholders {0} are plain string text in VS Code',
    'ReSharper.IDENTIFIER': 'generic .NET identifier: Roslyn semantic variable',
    'ReSharper.ASP_NET_MVC_ACTION': 'MVC/route references live inside string literals; VS Code shows string colour',
    'ReSharper.ASP_NET_RAZOR_KEYWORD': 'Razor semantic token razorDirective (C# extension, explicit)',
    'ReSharper.ASP_NET_RAZOR_CODE_BLOCK_TAG': 'Razor semantic token razorTransition (explicit)',
    'ReSharper.ASP_NET_RAZOR_TRANSITION_ESCPAE': 'name is misspelt in Rider itself; @@ escape -> razorTransition (explicit)',
    'ReSharper.ASP_NET_RAZOR_TAG_HELPER_ELEMENT': 'Razor semantic token razorTagHelperElement (explicit)',
    'ReSharper.ASP_NET_BLOCK_TAG': 'WebForms has no VS Code grammar: <% %> treated like a Razor transition',
    'ReSharper.T4_DIRECTIVE': 'T4 has no VS Code grammar: directives/attributes aliased to Razor/HTML equivalents',
    'ReSharper.T4_MACRO': '$(Macro) / %VAR% appear inside directive attribute values -> string colour',
    'ReSharper.XAML_CLASS': 'XAML via VS Code XML grammar: element names are tags',
    'ReSharper.XAML_FIELD': 'x:Name values are XML attribute strings in VS Code',
    'ReSharper.IL_KEYWORD': 'IL viewer has no VS Code grammar: aliased to core keys',
    'ReSharper.FSHARP_KEYWORD': 'F#: bundled TextMate grammar (Ionide semantic tokens not assumed)',
    'ReSharper.FSHARP_CLASS_IDENTIFIER': 'F# TextMate scopes every type name as entity.name.type.fsharp',
    'ReSharper.FSHARP_UNION_CASE_IDENTIFIER': 'F# TextMate leaves union cases / active patterns unscoped (default foreground)',
    'ReSharper.FSHARP_VALUE_IDENTIFIER': 'F# TextMate: let/member bindings are variable.fsharp',
    'ReSharper.FSHARP_FUNCTION_IDENTIFIER': 'F# TextMate: function bindings are variable.fsharp like values',
    'ReSharper.FSHARP_PREPROCESSOR_INACTIVE_BRANCH': 'F# TextMate does not mark inactive #if code (default foreground)',
    'ReSharper.ReSharper.ShaderLab_BLOCK_COMMENT': 'VS Code shaderlab grammar has no /* */ outside CG blocks; aliased to line comment',
    'ReSharper.ReSharper.ShaderLab_ENABLED_SHADER_KEYWORD': 'shader keywords after #pragma multi_compile are plain text in VS Code (all four states)',
    'ReSharper.CPP_NAMESPACE_IDENTIFIER': 'C++ identifiers: explicit cpptools semantic-token scopes',
    'ReSharper.CPP_PREPROCESSOR_INACTIVE_BRANCH': 'cpptools dims inactive regions with opacity, no token colour',
    'ReSharper.CPP_STRUCT_IDENTIFIER': 'cpptools emits class for structs/unions',
    'ReSharper.CPP_DOXYGEN_COMMAND_VALUE': 'Doxygen text after a command is comment text in VS Code',
    'ReSharper.CPP_THIS_KEYWORD': 'this/nullptr language constants',
    'ReSharper.BLOCK_SHADERS_IDENTIFIER': 'block-shader identifiers: no grammar, default foreground',
    'GD_KEYWORD': 'GDScript: godot-tools grammar not installed, explicit stacks from tokenising it',
    'GD_NOTE': 'NOTE/WARN/DANGER markers are plain comment text in VS Code',
    'GD_ENGINE_TYPE': 'godot-tools: engine classes entity.name.type.class, builtins (Vector2, void) ...class.builtin',
    'TSCN_NODE_RESOURCE': '.tscn: godot-tools GDResource grammar (explicit)',
    'TSCN_MEMBER_REF': 'method="..." in [connection] is a plain string in VS Code',
}
