# Contributing

Thanks for improving materials for the **UofT ASIC Team**.

## After creating a course from this template

1. Run `scripts/init-template.py` with `--id`, `--title`, and `--description` (org is always `uoftasic`).
2. Enable GitHub Pages with **Settings → Pages → Source: GitHub Actions**, so that `.github/workflows/site.yml` can build and deploy the site.
3. Prefer repo names that match course ids (`dd103`, `ic101`, …).

See [TEMPLATE.md](TEMPLATE.md).

## Placeholders

Only these three are fillable:

| Token | Example |
|-------|---------|
| `ad102` | `dd103` |
| `AD102 — Linear Circuits & Fabrication` | `DD103 — RTL on FPGAs & ASICs` |
| `Find out how resistors and capacitors are built on a SKY130 chip, and size your own to hit target values inside an area budget.` | `RTL synthesis intro with Yosys` |

## Conventions

| Item | Convention |
|------|------------|
| Org | `uoftasic` |
| Default branch | `main` |
| Docs pages | kebab-case `.md` under `docs/` |
| Lab IDs | `lab-NN-short-name` |
| Adding a guide page | add `.md` under `docs/guide/` (reading only; activities go in a lab), add it to the Course path, add it to the sidebar in `docs/_quarto.yml` and the chapters in `docs/_quarto-pdf.yml` |
| Adding a lab | `labs/<id>/` + `docs/labs/<id>-overview.md` + a Course path row in `docs/index.md` (`[Lab NN: Title](…).` and one sentence on what you'll do) + a sidebar entry in `docs/_quarto.yml` and a chapter in `docs/_quarto-pdf.yml`, in the same order |
| Binaries | small images in `docs/assets/`; large data → Git LFS or external |

## Docs vs labs

- **`docs/`**: the published site. Guide pages in `docs/guide/` are for reading; lab *writeups* in `docs/labs/` hold every command, as numbered parts. Each part opens with the question it answers and ends in a "you should see" check, and at least one part has the student produce something. A writeup ends with Finishing (You're done when, Questions with collapsed answers, Submit), then Going further for optional parts, then a "Next on the Course path" line. [AGENTS.md](AGENTS.md) has the details.
- **`labs/`**: runnable decks, Python and data. Each `labs/<id>/README.md` links to its writeup on the site and lists its make targets and files.
- **`scripts/`**: utilities; list entry points in `scripts/README.md`.

Do not put grades, solution keys, or PII under `docs/`. Prefer `labs/**/solutions/` and gitignore them on student forks when needed.

## Local docs preview

```bash
quarto preview docs      # -> http://localhost:4200
```

## Pull requests

Keep changes focused. For doc-only PRs, check navigation and math in the local preview when you can. On a pull request that touches `docs/**`, `.github/workflows/site.yml` renders the site and runs `scripts/check_site.py` over it, which lists every local link, image or `#anchor` that doesn't resolve (a broken link fails the run, and the job log lists each one), and `.github/workflows/docs-link-check.yml` checks the links in the Markdown sources, external ones included.
