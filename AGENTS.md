# Agent guide — UofT ASIC course repos

You are working in a **course repository** for the UofT ASIC Team (`uoftasic`): pedagogical materials for IC / RTL / FPGA / open-source ASIC flows. The site under `docs/` is built with Quarto and published on GitHub Pages by `.github/workflows/site.yml`. Runnable work lives outside `docs/`.

Optimize for clear student learning paths rather than template maintenance. Prefer concrete labs and notes that students can follow end to end over meta documentation.

## Goals

- Teach IC development skills: RTL (SystemVerilog/Verilog), simulation, synthesis, FPGA bring-up, and/or open ASIC flows (e.g. Yosys, LibreLane, SKY130) as the course requires.
- Keep each lab **self-contained**: what you'll build or measure → before you start (guide pages to read, setup) → time (leave optional parts out, or give their time separately) → numbered parts with numbered steps → Finishing → Going further (optional) → a "Next on the Course path" line. Each part opens with the one question it answers and ends in a "you should see" check.
- Every lab has at least one required part where the student produces something: edits a deck or file, writes a test, draws a cell, or computes a number and writes it down before checking it. Ask for a prediction before a run wherever the student can reasonably make one.
- Keep observed numbers and outputs in "you should see". When a check would also explain *why*, ask it as a question at that step and put the answer directly under it in a collapsed `<details><summary>Answer</summary> … </details>` block (blank lines inside, so Markdown and math render).
- Finishing has three things, in this order: **You're done when** (one checkable line tied to the student's own work, not the shipped `PASS`), **Questions** (each with a collapsed answer or a pointer to the step that answers it) and **Submit** (what to hand in, or "nothing"). Optional parts go after it, under Going further, marked "(optional)" in their headers; no required part may depend on one.
- Keep guide pages (`docs/guide/`) **reading only**: concepts, figures, worked examples. Commands and activities belong in the lab writeups; a guide page points to the lab part where the student does it.
- Keep the **Course path** table on `docs/index.md` (alternating Read and Do rows, with time estimates), the sidebar in `docs/_quarto.yml` and the chapter list in `docs/_quarto-pdf.yml` in the same order. The table header is `| # | | What | Time |`; Read and Do are plain text; a Do row is `[Lab 01: Title](labs/…-overview.md).` followed by one sentence on what you'll do; the row times add up to the total on the home page. Lab page titles and sidebar entries use the same "Lab 01: Title" form.
- Lab 01, Part 1 is "Load the course": a link to IC101 Lab 03 for anyone who hasn't set up the workbench, then the desktop, `.designinit`, `mod add <course>`, the tool versions the printed outputs depend on, and only the troubleshooting rows specific to this course, with a link to IC101's Troubleshooting page for the rest.
- Put lookup material (warning catalogues, troubleshooting tables, long tool output) on reference pages and link it from the step where it comes up. Aim for at most about 2,500 words per lab writeup, without cutting teaching content.
- Separate **what students read** (`docs/`) from **what they run** (`labs/`, `scripts/`, `notebooks/`).
- Never publish grades, solution keys, or PII under `docs/`. Put keys in `labs/**/solutions/` and gitignore them on student forks when policy requires.

## Layout (do not fight this)

| Path | Published? | Put here |
|------|------------|----------|
| `docs/` | Yes | Guides, lab writeups, figures for the site |
| `docs/guide/` | Yes | Conceptual notes (flows, tools, theory) |
| `docs/labs/` | Yes | Lab writeups only (`lab-NN-*-overview.md`) |
| `docs/assets/img/` | Yes | Small diagrams / waveforms for docs |
| `labs/<lab-id>/` | No | HDL, Python, testbenches, local data, graders |
| `scripts/` | No | Course utilities / automation |
| `notebooks/` | No | Exploratory or assignment notebooks |
| `data/`, `figures/` | No | Shared datasets / source figures |

Site wiring: `docs/_quarto.yml` (site, sidebar, navbar, per-page PDFs), `docs/_quarto-pdf.yml` (the whole course as one PDF) and `docs/_filters/course.lua` (turns `<details>` answers into collapsible callouts, and moves them to an Answers section at the end of each page in PDFs). Math: `$inline$`, `$$display$$`.

## Adding a lab (preferred unit of coursework)

Lab IDs: `lab-NN-short-name` (e.g. `lab-02-counter-sv`).

1. Create `labs/<lab-id>/` with at least:
   - `README.md` — points at the writeup on the site and says how to run the package
   - `src/` — HDL / Python / entrypoints
   - `data/` — small inputs (large binaries → Git LFS or external)
   - `requirements.txt` or tool notes when needed
2. Add `docs/labs/<lab-id>-overview.md` in the lab shape above: what you'll build or measure, before you start, time, numbered parts each opening with a question and ending in a "you should see" check, Finishing (You're done when, Questions, Submit), Going further, and the Next line.
3. Add a row for it to the Course path table in `docs/index.md`, and add the writeup to the sidebar in `docs/_quarto.yml` and the chapters in `docs/_quarto-pdf.yml` in the same position (and to the navbar in `_quarto.yml` only if it belongs in the top navigation).
4. Cross-link: writeup → GitHub `labs/<lab-id>/`; package README → `docs/labs/<lab-id>-overview.md`.

**Writeups teach; packages execute.** Do not paste long HDL or decks into site pages; reference the files under `labs/`.

A capstone with no package (like AD102's `docs/labs/capstone-floor-plan-overview.md`) still gets a writeup in `docs/labs/` and a Course path row.

## Adding a guide page

1. Add kebab-case Markdown under `docs/guide/` (e.g. `yosys-synth.md`). Reading only: no required commands.
2. Add it to the right Read row of the Course path in `docs/index.md`, and add it to the sidebar in `docs/_quarto.yml` and the chapters in `docs/_quarto-pdf.yml` in the same position.
3. Images under `docs/assets/img/`, linked with paths relative to the page you are writing in (`../assets/img/x.png` from a guide or lab page).
4. Link between pages with paths relative to the page you are writing in (`../guide/x.md` from a lab), because that is how Quarto resolves them; use GitHub URLs for `labs/` and `scripts/`.

## Pedagogy checklist (use when authoring)

- State **learning objectives** in student language (“You will synthesize a counter and inspect the netlist”).
- Assume a clone of this repo and the course’s documented workbench; do not bundle Docker in every lab unless the course already does.
- For EDA-heavy work (LibreLane / SKY130 / IIC-OSIC-TOOLS), use the **team workbench** that IC101 Lab 03 sets up rather than inventing a one-off container story; the course itself only loads into it (Lab 01, Part 1).
- Keep procedures copy-pasteable (`cd`, install, simulate/synth, check artifact).
- Define **expected results** (printout, waveform check, area/timing ballpark, golden hash) so students know they succeeded.
- Progress difficulty across labs; reuse naming and directory conventions so later labs feel familiar.
- Prefer small, inspectable designs over opaque blobs; when using IP or PDK artifacts, keep secrets and huge binaries out of git.

## Tooling norms

- Python helpers and graders: under `labs/<id>/src/` or `scripts/`; list entry points in the nearest `README.md`.
- SystemVerilog/Verilog: under `labs/<id>/src/` (or `rtl/`, `tb/` if you split — stay consistent within the course).
- Heavy outputs (GDS, large FSDB/VCD, PDK caches): local `results/` or LFS — never under `docs/`.
- Preview docs locally: `quarto preview docs` → http://localhost:4200

## What not to do

- Do not add maintainer-only pages to the published site (contributing guides, template notes, notation stubs “for debugging”).
- Do not put solution keys or rubrics in `docs/`. A collapsed answer to a question in a writeup is fine; the reference answer to the part the student designs (a deck, a test) stays in `labs/**/solutions/`.
- Do not replace student-facing content with template/bootstrap instructions; point humans at `CONTRIBUTING.md` / `TEMPLATE.md` only when they are bootstrapping or changing repo conventions.
- Do not change org assumptions: GitHub org is `uoftasic`; course id matches the repo name.

## Quick references

- Repo conventions: `CONTRIBUTING.md`
- Bootstrap tokens / Pages checklist: `TEMPLATE.md`
- Sample lab shape: `labs/lab-01-a-resistor-you-designed/` + `docs/labs/lab-01-a-resistor-you-designed-overview.md`
