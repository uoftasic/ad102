# Scripts

Utilities for **AD102 — Linear Circuits & Fabrication** under the UofT ASIC org (`uoftasic`).

## Entry points

| Script | Purpose |
|--------|---------|
| `hello.py` | Smoke-check that Python runs in this clone |
| `init-template.py` | Fill `ad102` / title / description after using the template |
| `check_site.py` | After `quarto render docs`, list every local link, image and `#anchor` in `docs/_site` that doesn't resolve: `python3 scripts/check_site.py docs/_site`. It always exits 0, so read its last line (`… N broken`) |

## Usage

```bash
# From repo root
python3 scripts/hello.py

python3 scripts/init-template.py \
  --id dd103 \
  --title "DD103 — RTL on FPGAs & ASICs" \
  --description "RTL on FPGAs and open-source ASIC flows"
```

## Conventions

- Prefer Python; HDL tooling belongs in `labs/` or the shared workbench.
- No secrets in the repo; use `.env.example` if configuration is needed.
- Document new scripts here when you add them.
