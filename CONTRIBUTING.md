# Contributing

Thanks for improving materials for the **UofT ASIC Team**.

## After creating a course from this template

1. Run `scripts/init-template.py` with `--id`, `--title`, and `--description` (org is always `uoftasic`).
2. Enable GitHub Pages: branch `main`, folder `/docs`.
3. Prefer repo names that match course ids (`dd103`, `ic101`, …).

See [TEMPLATE.md](TEMPLATE.md).

## Placeholders

Only these three are fillable:

| Token | Example |
|-------|---------|
| `ad102` | `dd103` |
| `AD102 — Linear Circuits & Fabrication` | `DD103 — RTL on FPGAs & ASICs` |
| `Linear analysis, folded together with how passives are actually built on a chip.` | `RTL synthesis intro with Yosys` |

## Conventions

| Item | Convention |
|------|------------|
| Org | `uoftasic` |
| Default branch | `main` |
| Docs pages | kebab-case `.md` under `docs/` |
| Lab IDs | `lab-NN-short-name` |
| Adding a doc page | add `.md` under `docs/`, link in `docs/_sidebar.md` |
| Adding a lab | `labs/<id>/` + `docs/labs/<id>-overview.md` + sidebar entry |
| Binaries | small images in `docs/assets/`; large data → Git LFS or external |

## Docs vs labs

- **`docs/`** — published site. Lab *writeups* in `docs/labs/`.
- **`labs/`** — runnable HDL / Python / data. Each `labs/<id>/README.md` links to its Docsify writeup.
- **`scripts/`** — utilities; list entry points in `scripts/README.md`.

Do not put grades, solution keys, or PII under `docs/`. Prefer `labs/**/solutions/` and gitignore them on student forks when needed.

## Local docs preview

```bash
npx docsify-cli serve docs
```

## Pull requests

Keep changes focused. For doc-only PRs, check navigation and math locally when practical. Optional CI may link-check `docs/**`.
