# GitHub Themes generator

Builds the [GitHub Themes](https://plugins.jetbrains.com/plugin/20810-github-themes) JetBrains plugin's
11 UI themes and editor color schemes from GitHub's VS Code theme. It is checked out as a submodule at
`examples/generator/` of the plugin repo, and `update.py --apply` writes into that repo's `resources/theme/`.

`node_modules/`, `__pycache__/`, `parity/.cache/` and `out/` are rebuilt and not tracked; after cloning,
run `npm install --ignore-scripts` in `vsc/` and `parity/` before regenerating.

The generator code is © Yash Pal, all rights reserved; bundled third-party files keep their own licenses
(MIT for GitHub's theme source, Apache-2.0 for JetBrains' themes). See [LICENSE](LICENSE).

Regenerates all 11 UI themes + editor schemes from GitHub's VS Code theme source.

## Pull the latest upstream release

    python3 update.py              # fetch latest primer/github-vscode-theme release, rebuild, audit, list changes
    python3 update.py --apply      # ...and copy changed files into resources/theme/
    python3 update.py --tag v6.3.5 # use a specific release

`update.py` first copies the JetBrains parent-theme chain (Darcula, IntelliJ, expUI, Islands) from
the newest installed JetBrains IDE into `jetbrains/` (build recorded in `jetbrains/SOURCE.json`).
It then downloads the release tarball to a temp dir, replaces `vsc/src` with its `src/`,
re-applies the tritanopia patch, pins `@primer/primitives` to the release's exact version,
rebuilds `vsc/vscode.json`, and stops if the patch changed any upstream variant (it builds the
unpatched release too and compares). Then it runs `gen_themes.py` + `audit2.py`; nothing is
copied into `resources/theme/` unless the audit passes and `--apply` is given.
The pulled version is recorded in `vsc/UPSTREAM.json` and written into each scheme's metaInfo.

## Regenerate without pulling

    cd vsc && npm install --ignore-scripts && node gen.js && cd ..   # -> vsc/vscode.json
    python3 gen_themes.py out && python3 audit2.py out
    cp out/*.theme.json ../../resources/theme/ && cp out/scheme/*.xml ../../resources/theme/scheme/

## Preview images

    python3 preview.py            # all 11 -> ../../public/images/previews/<variant>.png
    python3 preview.py dark-dimmed --out /tmp/prev
    python3 preview.py --banner   # compose ../../public/images/banner.png from the previews
    python3 preview.py --slides   # animated ../../public/images/themes.png: banner, then all 11

Draws an Islands-style IDE window (toolbar, stripes, Project tree, Kotlin editor with a completion
popup, status bar) from the generated `resources/theme/*.theme.json` and schemes, and screenshots it
at 2560x1600 with headless Chrome (`CHROME` overrides the path). It's a mockup, not an IDE screenshot.
Missing keys are drawn magenta and make it exit non-zero.
`--slides` joins the banner (rendered at the previews' 2560x1600) and the previews into a looping
APNG (4 s banner, 2.5 s per theme, 0.6 s left-to-right wipe between them). Headless Chrome crops each
wipe into 12 full-height strips, which become small APNG frames drawn over the previous one, so the
wipe costs about one frame of file size. Only the standard library and Chrome are needed.

## Files

- `vsc/src`: upstream `src/` (minus index.js) + tritanopia patch (colors.js cases for the two
  tritanopia palettes; `themes()` falls back to the colorblind slot). The patch is skipped
  automatically if upstream ever ships tritanopia itself.
- `vsc/gen.js`: builds `vscode.json` (VS Code colors, tokenColors and the flattened Primer palette).
- `gen_themes.py`: the VS Code/Primer → IntelliJ mapping. Primer text colors that fail WCAG AA on
  their IntelliJ surface are nudged minimally; every adjustment is printed.
- `islands_map.py`: repaints every colour key inherited from the JetBrains chain into the GitHub
  palette (Islands semantic tokens mapped explicitly; other colours snapped to the nearest Primer
  colour), so no JetBrains colour shows through. Keys set in `gen_themes.py` take precedence.
- `jetbrains/`: the JetBrains theme chain our themes inherit from (refreshed by `update.py`), plus
  `code_defaults.json`: colour keys IDE code reads with a hardcoded JetBrains default and no theme sets.
- `codekeys.py`: builds `jetbrains/code_defaults.json` by scanning every installed JetBrains IDE's classes
  with `javap` (run by `update.py`; `python3 codekeys.py` to rerun alone).
- `syntax/`: one module per language family mapping IntelliJ syntax keys to VS Code scopes;
  `syntax/MAPPING.md` has the rules for mapping new keys and how to verify them.
- `preview.py`: renders the README/Marketplace preview images (see above).
- `audit2.py`: contrast, accessibility, Islands-structure, parity and JetBrains-leak checks.
- `orig/scheme/`: pre-generator schemes, used only as the editor attribute-name template.
- `LICENSE-github-vscode-theme.txt`: upstream MIT license.
