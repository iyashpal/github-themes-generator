# Mapping IntelliJ syntax keys to VS Code scopes

Editor syntax colours must be **identical to VS Code** with the GitHub VS Code theme, in all 11
variants. Each IntelliJ `TextAttributesKey` (`PHP_KEYWORD`, `TS.TYPE_PARAMETER`, `CSS.PROPERTY_NAME`, …)
maps to the TextMate scope stack VS Code gives the **same construct**. Colours are never hand-picked:
`gen_themes.py` resolves each stack against each variant's `tokenColors` with vscode-textmate
(`parity/resolve.js`), so one map serves every variant. A colour is only wrong if the mapping points at
the wrong construct, or a real key is unmapped.

Read this when JetBrains adds keys, a new language needs mapping, or a key looks wrong.

## Module format

One module per language family, `syntax/<family>.py` (format in the `syntax/__init__.py` docstring):

```python
SAMPLES = {                     # name -> (VS Code grammar scopeName or language id, code)
    'php': ('text.html.php', r'''<?php
namespace App\Actions;
use App\Models\User;
...'''),
}
MAP = {
    'PHP_KEYWORD':   ('php', 'function', 1),   # token containing 1st char of 1st occurrence of 'function'
    'PHP_CLASS':     ('php', 'User', 2),       # nth occurrence: make `find` unique or count carefully
    'PHP_TAG':       'text.html.php meta.embedded.block.php punctuation.section.embedded.begin.php',  # explicit stack
    'PHP_BRACES':    ('=', 'DEFAULT_BRACES'),  # alias: same colour as another key (any module)
}
NOTES = {'PHP_IDENTIFIER': 'one IntelliJ key covers namespace decls (entity) and use paths (support); chose support'}
```

* Prefer **sample-based** entries: realistic code in the language, each key pointing at the token it
  highlights in IntelliJ. The scope then comes from VS Code's real grammar (`parity/tokenize.js` loads
  every grammar bundled with VS Code plus `~/.vscode/extensions`).
* Use an **explicit stack** only when VS Code has no grammar for the language, or no sample can produce
  the construct. Write the stack the de-facto VS Code extension's grammar would produce (Kotlin:
  `source.kotlin entity.name.function.declaration.kotlin`; Twig:
  `text.html.twig meta.tag.template.block.twig keyword.control.twig`) and get the semantic parts right
  (`keyword.control`, `entity.name.function`, `string.quoted`, `variable.parameter`, `support.class`,
  `constant.numeric`, `comment.line`, `punctuation.definition.tag`, …), because those decide the colour.
  Say in NOTES that it is explicit.
* Use an **alias** only when the key is genuinely the same construct as a key mapped elsewhere, e.g. the
  `DEFAULT_*` keys in `core.py` (`DEFAULT_KEYWORD`, `DEFAULT_STRING`, `DEFAULT_BRACES`,
  `DEFAULT_FUNCTION_CALL`, `DEFAULT_PARAMETER`, …). If VS Code colours the construct differently in this
  language, map it with a sample instead.

## Which keys to map

* `parity/inventory.json`: every key JetBrains' bundled Default/Darcula schemes set (`parity/inventory.py`
  rebuilds it from the installed IDEs). These **must** be mapped, or JetBrains colours leak.
* `parity/keyscan.json`: key-like strings found in highlighter classes (`parity/keyscan.py`). Many are
  noise (message texts, enum names). Map one only once you've confirmed it is a real `TextAttributesKey`
  of a real highlighting construct.
* Keys with an IntelliJ fallback (`PHP_KEYWORD` → `DEFAULT_KEYWORD`) still get mapped: every real key gets
  an explicit, VS Code-accurate value.
* Non-syntax keys (console, terminal, debugger, diff, inlay, coverage, UI) are not mapped here; they are
  set in `scheme()` in `gen_themes.py`.

To see what a key paints, look at the language's Colors & Fonts demo text and its tag→key map in the IDE
jars: `python3 -I parity/classstrings.py <jar> <ClassNameSubstring>` prints a class's string constants
(demo text with `<tag>` markup, tag names, key names). Find the class with
`unzip -l <jar> | grep -i ColorSettingsPage` (or `ColorsPage`, `ColorPage`, `Highlighter`).
`javap -c -p -classpath <jar> <fqcn>` shows which key a tag or visitor uses.

## Rules for choosing the VS Code construct

1. **Same construct, same tokenisation.** Write the sample so VS Code's grammar sees the construct the
   way it does in real files (inside a class or function where relevant).
2. **Semantic highlighting.** The GitHub theme ships `semanticHighlighting: true`. Where VS Code's
   language server emits semantic tokens (JavaScript/TypeScript built in; Java via vscode-java; Python via
   Pylance; C/C++ via cpptools), the colour of identifiers comes from the semantic token's fallback scope,
   not the TextMate scope. VS Code's fallback table:
   `namespace→entity.name.namespace, type→entity.name.type, type.defaultLibrary→support.type,
   class→entity.name.type.class, class.defaultLibrary→support.class, interface→entity.name.type.interface,
   enum→entity.name.type.enum, function→entity.name.function, function.defaultLibrary→support.function,
   method→entity.name.function.member, macro→entity.name.function.preprocessor,
   variable→variable.other.readwrite, variable.readonly→variable.other.constant,
   variable.readonly.defaultLibrary→support.constant, parameter→variable.parameter,
   property→variable.other.property, property.readonly→variable.other.constant.property,
   enumMember→variable.other.enummember, event→variable.other.event, decorator→entity.name.decorator,
   label→entity.name.label, typeParameter→entity.name.type.parameter`.
   For identifier-like keys in those languages (variables, parameters, properties, functions, classes,
   type parameters), use an explicit stack `<root> <fallback scope>` (e.g. `source.ts variable.parameter`)
   and say so in NOTES. Keywords, strings, numbers, comments and punctuation stay sample-based. PHP is
   TextMate only.
3. **One key, several VS Code colours.** Where one IntelliJ key covers constructs VS Code colours
   differently (e.g. `PHP_IDENTIFIER`), pick the construct most common in real code and explain in NOTES.
4. **Punctuation.** Map braces, brackets, parens, commas, dots, semicolons and operators via samples too:
   VS Code colours some punctuation (`punctuation.definition.string` takes the string colour,
   `punctuation.definition.tag` in HTML, `keyword.operator`).
5. **Font style.** Don't add bold or italic; font style comes from the theme via the scope.

## Verify

* `python3 syntax_check.py <family>` tokenises the samples and prints, per key, the resolved colour in
  GitHub Light, Light Default and Dark Default plus the scope stack. Iterate until it shows **0 errors**
  and every stack is the token you meant (not the whitespace before it, not only the enclosing meta scope).
* To check a family against IntelliJ itself: take each Colors & Fonts demo text, strip the `<tag>` markup,
  tokenise it with `node parity/tokenize.js` (one request per tagged range, `find` = the tagged text),
  resolve the colour with `node parity/resolve.js` (input formats in each script's header; themes from
  `vsc/vscode.json` `[variant].tokenColors`), and compare with our colour for the tag's key. Untagged
  tokens are lexer keys: spot-check keywords, strings, numbers, comments, operators and punctuation the
  same way.
* `python3 parity/verify.py out` checks the whole output against VS Code, sample targeting and coverage.
