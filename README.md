# AD102 — Linear Circuits & Fabrication

Linear analysis, folded together with how passives are actually built on a chip.

Docsify course / lab template for the **UofT ASIC Team** (`uoftasic`). Published docs live under `./docs`; runnable labs, scripts, notebooks, and data stay in the repo root. Zero build for GitHub Pages — Markdown, MathJax, and images work out of the box.

Org: [github.com/uoftasic](https://github.com/uoftasic)

## Live docs

**This template:** https://uoftasic.com/course-template/

**Education hub:** https://edu.uoftasic.com/

After Pages is enabled on a course repo created from this template:

**https://uoftasic.com/ad102/**

## Use this template

1. On [uoftasic/course-template](https://github.com/uoftasic/course-template), click **Use this template** → create a repo named after the course id (e.g. `dd103`, `serdes-lab`).
2. Clone and bootstrap:

```bash
python3 scripts/init-template.py \
  --id ad102 \
  --title "AD102 — Linear Circuits & Fabrication" \
  --description "Linear analysis, folded together with how passives are actually built on a chip."
```

3. Enable **Settings → Pages → Deploy from a branch → `main` / `/docs`**.

See [TEMPLATE.md](TEMPLATE.md) for the checklist. Org is always `uoftasic` — only course id / title / description are filled in.

## Quick start

```bash
git clone https://github.com/uoftasic/ad102.git
cd ad102

# Docs (requires Node.js)
npx docsify-cli serve docs
# → http://localhost:3000

# Sample script
python3 scripts/hello.py

# Sample lab
python3 labs/lab-01/src/main.py
```

Tool-heavy courses that need IIC-OSIC-TOOLS / SKY130 should document the team workbench setup in-course rather than bundling Docker in every repo.

## Layout

| Path | On Pages? | Purpose |
|------|-----------|---------|
| `docs/` | **Yes** | Human-facing Docsify site |
| `docs/labs/` | Yes | Lab *writeups* (procedure, theory) |
| `labs/` | No | Runnable packages (HDL, Python, data, graders) |
| `scripts/` | No | Team utilities / automation |
| `notebooks/` | No | Exploratory / assignment notebooks |
| `data/`, `figures/` | No | Shared datasets / source figures |

## GitHub Pages

| Setting | Value |
|---------|--------|
| Source | Deploy from a branch |
| Branch | `main` |
| Folder | `/docs` |

No Actions deploy step is required for the baseline Docsify site.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE) — Copyright UofT ASIC Team / `uoftasic`
