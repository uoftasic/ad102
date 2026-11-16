# AD102 — Linear Circuits & Fabrication

Find out how resistors and capacitors are built on a SKY130 chip, and size your own to hit target values inside an area budget.

The second course in the UofT ASIC Team **analog track**. Published docs live under `./docs` and are served by GitHub Pages; the runnable SPICE decks live in `labs/`. Students should start at the Course path on the home page.

Org: [github.com/uoftasic](https://github.com/uoftasic)

## Live docs

**This course:** https://uoftasic.com/ad102/

**Education hub:** https://edu.uoftasic.com/

**Prerequisites:** [IC101](https://uoftasic.com/ic101/) then [AD101](https://uoftasic.com/ad101/), in that order.

## Quick start

Every package under `labs/` runs with `make` alone, in a bare container, with no environment setup. On a fresh clone every lab's first `make` ends in `FAIL` on purpose: each package ships a naive design for the student to fix.

Students instead set up the workbench through the `workspace` repo in [IC101](https://uoftasic.com/ic101/) Lab 03, then load this course into it in Lab 01, Part 1. The command below is a quick check that a lab runs in the image:

```bash
git clone https://github.com/uoftasic/ad102.git
cd ad102

docker run --rm --user "$(id -u):$(id -g)" -v "$PWD:/work" -w /work \
  hpretl/iic-osic-tools:2026.08 --skip \
  bash -c 'cd /work/labs/lab-01-a-resistor-you-designed && make'
```

Docs preview (requires [Quarto](https://quarto.org/docs/get-started/) 1.11):

```bash
quarto preview docs                            # -> http://localhost:4200
quarto render docs --profile pdf --to typst    # whole course as one PDF in docs/_book/
```

Tool-heavy courses that need IIC-OSIC-TOOLS / SKY130 should use the team workbench that IC101 Lab 03 sets up, rather than bundling Docker in every repo; the course's Lab 01, Part 1 only loads the course into it.

## Layout

| Path | On Pages? | Purpose |
|------|-----------|---------|
| `docs/` | **Yes** | Human-facing Quarto site (`docs/_quarto.yml`) |
| `docs/guide/` | Yes | Guide pages: reading only |
| `docs/labs/` | Yes | Lab *writeups*: every command, as numbered parts and steps |
| `labs/` | No | Runnable packages (HDL, Python, data, graders) |
| `scripts/` | No | Team utilities / automation |
| `notebooks/` | No | Exploratory / assignment notebooks |
| `data/`, `figures/` | No | Shared datasets / source figures |

## GitHub Pages

| Setting | Value |
|---------|--------|
| Source | GitHub Actions |

`.github/workflows/site.yml` renders `docs/` with Quarto on every push to `main` that changes `docs/`, `scripts/check_site.py` or the workflow itself, and deploys `docs/_site`, which includes a PDF of every page and the whole-course PDF linked from the navbar.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE) — Copyright UofT ASIC Team / `uoftasic`
