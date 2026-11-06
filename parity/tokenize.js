// Tokenise snippets with VS Code's own bundled grammars and report the scope stack of each token.
// stdin:  [{"id": "...", "lang": "php", "code": "...", "find": "text", "nth": 1}, ...]
//         lang is a VS Code language id (php, typescript, css, ...) or a grammar scopeName (source.php).
// stdout: {id: {"scopes": "source.php meta.use.php support.class.php", "text": "User"} | {"error": "..."}}
// The scope stack reported is the one of the token that contains the first character of the
// nth occurrence of `find` in `code`.
const fs = require('fs');
const path = require('path');
const vsctm = require('vscode-textmate');
const oniguruma = require('vscode-oniguruma');

const EXT_DIRS = [
  '/Applications/Visual Studio Code.app/Contents/Resources/app/extensions',
  path.join(process.env.HOME, '.vscode/extensions'),
];

function loadContributions() {
  const byScope = {}, byLang = {}, injections = {};
  for (const dir of EXT_DIRS) {
    if (!fs.existsSync(dir)) continue;
    for (const ext of fs.readdirSync(dir)) {
      const pj = path.join(dir, ext, 'package.json');
      if (!fs.existsSync(pj)) continue;
      let pkg; try { pkg = JSON.parse(fs.readFileSync(pj, 'utf8')); } catch { continue; }
      for (const g of (pkg.contributes && pkg.contributes.grammars) || []) {
        if (!g.scopeName || !g.path) continue;
        const file = path.join(dir, ext, g.path);
        // built-in extensions win over marketplace ones for the same scope
        if (!byScope[g.scopeName]) byScope[g.scopeName] = { file, embedded: g.embeddedLanguages || {} };
        if (g.language && !byLang[g.language]) byLang[g.language] = g.scopeName;
        for (const target of g.injectTo || []) (injections[target] = injections[target] || []).push(g.scopeName);
      }
    }
  }
  return { byScope, byLang, injections };
}

(async () => {
  await oniguruma.loadWASM(fs.readFileSync(path.join(__dirname, 'node_modules/vscode-oniguruma/release/onig.wasm')).buffer);
  const { byScope, byLang, injections } = loadContributions();
  const registry = new vsctm.Registry({
    onigLib: Promise.resolve({
      createOnigScanner: (p) => new oniguruma.OnigScanner(p),
      createOnigString: (s) => new oniguruma.OnigString(s),
    }),
    loadGrammar: async (scope) => {
      const c = byScope[scope];
      if (!c) return null;
      const txt = fs.readFileSync(c.file, 'utf8');
      return vsctm.parseRawGrammar(txt, c.file);
    },
    getInjections: (scope) => injections[scope] || [],
  });
  const reqs = JSON.parse(fs.readFileSync(0, 'utf8'));
  const out = {};
  const cache = {};
  for (const r of reqs) {
    try {
      const scope = byScope[r.lang] ? r.lang : byLang[r.lang];
      if (!scope) throw new Error(`no grammar for ${r.lang}`);
      const g = cache[scope] || (cache[scope] = await registry.loadGrammar(scope));
      if (!g) throw new Error(`grammar ${scope} failed to load`);
      // locate target
      let idx = -1, n = r.nth || 1;
      for (let from = 0; n > 0; n--) { idx = r.code.indexOf(r.find, from); if (idx < 0) break; from = idx + 1; }
      if (idx < 0) throw new Error(`"${r.find}" not found`);
      const lines = r.code.split('\n');
      let state = vsctm.INITIAL, offset = 0, found = null;
      for (const line of lines) {
        const res = g.tokenizeLine(line, state);
        if (!found && idx >= offset && idx < offset + line.length + 1) {
          const col = idx - offset;
          for (const t of res.tokens) {
            if (col >= t.startIndex && col < t.endIndex) {
              found = { scopes: t.scopes.join(' '), text: line.slice(t.startIndex, t.endIndex) };
              break;
            }
          }
        }
        state = res.ruleStack;
        offset += line.length + 1;
      }
      out[r.id] = found || { error: 'token not found' };
    } catch (e) {
      out[r.id] = { error: String(e.message || e) };
    }
  }
  process.stdout.write(JSON.stringify(out));
})().catch((e) => { console.error(e); process.exit(1); });
