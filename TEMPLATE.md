# Template bootstrap (UofT ASIC)

Create a course or lab-notes repo from this template under **`uoftasic`**, fill the three course fields, enable Pages.

## Fixed vs fillable

| Item | Value |
|------|--------|
| GitHub org | `uoftasic` (hardcoded — do not change) |
| Team | UofT ASIC Team |

| Token | Meaning | Example |
|-------|---------|---------|
| `ad102` | Repo slug / course id | `dd103`, `ic101`, `serdes-lab` |
| `AD102 — Linear Circuits & Fabrication` | Display name | `DD103 — RTL on FPGAs & ASICs` |
| `Linear analysis, folded together with how passives are actually built on a chip.` | One-line blurb | `RTL synthesis intro with Yosys` |

## Init script

```bash
python3 scripts/init-template.py \
  --id dd103 \
  --title "DD103 — RTL on FPGAs & ASICs" \
  --description "RTL on FPGAs and open-source ASIC flows"
```

Dry run: add `--dry-run`.

## After-clone checklist

- [ ] Repo created under `uoftasic` with id matching `ad102`
- [ ] `scripts/init-template.py` run (or manual replace of the three tokens)
- [ ] Pushed to `main`
- [ ] Pages: **Settings → Pages → `main` / `/docs`**
- [ ] Live: `https://uoftasic.com/<course-id>/` (org Pages; hub: https://edu.uoftasic.com/)
- [ ] Sidebar navigates Home → Getting started → Lab 01
- [ ] Math + sample figure render on the home page
- [ ] (Maintainers of this template) **Settings → Template repository** enabled

## Naming

Prefer course ids already used by the team (`ic###`, `ad###`, `dd###`) or a clear kebab-case lab name. Keep the GitHub repo name equal to `ad102` so Pages and clone URLs stay predictable.

## Related

Each course from this template publishes at `https://uoftasic.com/<course-id>/` with zero-build Docsify docs under `docs/` and first-class `labs/` / `scripts/` trees. The education hub is https://edu.uoftasic.com/.
