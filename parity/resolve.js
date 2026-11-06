// Resolve TextMate scope stacks to colours exactly as VS Code does.
// stdin:  {"themes": {variant: {"fg": "#rrggbb", "bg": "#rrggbb", "tokenColors": [...]}}, "stacks": ["source.php entity.name.type.php", ...]}
// stdout: {variant: {stack: {"fg": "#rrggbb", "fontStyle": "italic bold underline strikethrough" | ""}}}
// Each stack is tokenised with a one-rule synthetic grammar (scopeName = first scope, the rule names
// the rest), so selector matching, specificity and parent-scope rules come from vscode-textmate itself.
const fs = require('fs');
const path = require('path');
const vsctm = require('vscode-textmate');
const oniguruma = require('vscode-oniguruma');

const wasm = fs.readFileSync(path.join(__dirname, 'node_modules/vscode-oniguruma/release/onig.wasm')).buffer;

(async () => {
  await oniguruma.loadWASM(wasm);
  const onigLib = Promise.resolve({
    createOnigScanner: (p) => new oniguruma.OnigScanner(p),
    createOnigString: (s) => new oniguruma.OnigString(s),
  });
  const input = JSON.parse(fs.readFileSync(0, 'utf8'));
  const stacks = [...new Set(input.stacks)];
  const out = {};
  for (const [variant, t] of Object.entries(input.themes)) {
    // one grammar per real root scope; each stack is a rule matching its own marker word
    const byRoot = {};
    stacks.forEach((stack, i) => {
      const parts = stack.trim().split(/\s+/);
      (byRoot[parts[0]] = byRoot[parts[0]] || []).push({ i, stack, rest: parts.slice(1).join(' ') });
    });
    const grammars = {};
    for (const [root, items] of Object.entries(byRoot)) {
      grammars[root] = {
        scopeName: root,
        patterns: items.filter((x) => x.rest).map((x) => ({ match: `\\bQ${x.i}Q\\b`, name: x.rest })),
      };
    }
    const registry = new vsctm.Registry({
      onigLib,
      loadGrammar: async (scopeName) => grammars[scopeName] || null,
      theme: { settings: [{ settings: { foreground: t.fg, background: t.bg } }, ...t.tokenColors] },
    });
    const colorMap = registry.getColorMap();
    const res = {};
    for (const [root, items] of Object.entries(byRoot)) {
      const g = await registry.loadGrammar(root);
      for (const x of items) {
        const r = g.tokenizeLine2(`Q${x.i}Q`, vsctm.INITIAL);
        const meta = r.tokens[1];
        const fgIdx = (meta >>> 15) & 0x1ff;
        const fsb = (meta >>> 11) & 0xf;
        const style = [];
        if (fsb & 1) style.push('italic');
        if (fsb & 2) style.push('bold');
        if (fsb & 4) style.push('underline');
        if (fsb & 8) style.push('strikethrough');
        res[x.stack] = { fg: colorMap[fgIdx].toLowerCase(), fontStyle: style.join(' ') };
      }
    }
    out[variant] = res;
  }
  process.stdout.write(JSON.stringify(out));
})().catch((e) => { console.error(e); process.exit(1); });
