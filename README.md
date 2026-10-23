# Forever Spellbook

A spellbook, talent calculator and action bar planner for **WoW Forever**.

Pick a class, race, level and talents to see exactly what's in your spellbook, then lay out your action bars the way you would in game.

**Live site:** https://sshillyer.github.io/forever-spellbook/

## Features

- All nine classes: trainer abilities, talents and racials, with full tooltips and Wowhead links
- Talent calculator with per-rank tooltips ("Next rank"), prerequisite arrows, a Fill helper, text search and per-class tags (Crit, Pet, Traps, Curses…)
- Spellbook view for any level and talent build, plus an All abilities list with role filters
- Action bars with drag and drop, and two layouts:
  - **Razer Tartarus + Naga**: 1–= in a 4×3 grid, Z X C, a Shift layer and F1–F12
  - **Standard keyboard**: up to 7 bars of 1–=, one per modifier (none, Shift, Ctrl, Alt, Shift+Alt, Shift+Ctrl, Shift+Ctrl+Alt)
- **Role slots** (Kick, Stun, CC, Snare, Defensive…) that fill with each class's version automatically, so binds stay consistent across alts
- **Missing from bars** highlight for spells you know but haven't placed
- Builds save in your browser. Use **Export / Import** to back them up or move them between PCs.

## Repository layout

| Path | What it is |
| --- | --- |
| `src/index.template.html` | The page (HTML, CSS, JS). `__DATA__` and `__ICONS__` are filled in at build time. |
| `data/data.json` | Classes, abilities, talents (with per-rank text) and racials |
| `data/icons.json` | Spell icons as base64 JPEGs, keyed by Wowhead icon name |
| `data/pulls/` | Raw data as pulled from Wowhead, dated, for reference |
| `scripts/build.mjs` | Builds `dist/index.html` (no dependencies) |
| `tools/` | Python scripts used to apply each Wowhead pull to `data/data.json` |
| `.github/workflows/deploy.yml` | Builds and deploys to GitHub Pages on every push to `main` |

## Build locally

```sh
node scripts/build.mjs
# then open dist/index.html in a browser
```

## Updating the data

The data is pulled from Wowhead's WoW Forever talent calculator and spell tooltips. Each pull is saved under `data/pulls/` and applied with a script in `tools/`. For example:

```sh
python3 tools/apply_talent_ranks.py   # run from the repo root
```

`tools/initial_build_2026-10-09.py` is the original builder. It's kept for history and would overwrite later updates, so don't re-run it.

The longer-term plan is an in-game addon that dumps talents, spells and racials straight from the client, so updates won't depend on Wowhead.

## Credits

Data and icons come from [Wowhead](https://www.wowhead.com/forever). World of Warcraft and its art are trademarks of Blizzard Entertainment. This is an unofficial fan tool.
