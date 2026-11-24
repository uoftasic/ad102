#!/usr/bin/env python3
"""Check a rendered Quarto site. Usage: check_site.py SITE_DIR

Two checks over every HTML page outside site_libs:
- every local href/src resolves: the file exists, and so does any #anchor;
- every page Quarto rendered has an <a> whose href is exactly
  https://edu.uoftasic.com/, the navbar's link to all courses. HTML that
  Quarto copies without rendering (no Quarto generator tag) needs no such
  link; the script lists those pages but still checks their local links.
Prints each problem and a count line for each check. Exits 1 if any local
reference is broken or any Quarto page lacks the link, otherwise 0."""
import os, re, sys
from html.parser import HTMLParser
from urllib.parse import urldefrag, unquote

PORTAL = "https://edu.uoftasic.com/"
site = sys.argv[1]
ids, refs, skipped, no_portal = {}, [], [], []

class P(HTMLParser):
    def __init__(self, path):
        super().__init__(); self.path = path; self.ids = set(); self.quarto = self.portal = False
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a: self.ids.add(a["id"])
        if tag == "a" and "name" in a: self.ids.add(a["name"])
        if tag == "a" and a.get("href") == PORTAL: self.portal = True
        if tag == "meta" and a.get("name") == "generator" and (a.get("content") or "").startswith("quarto"): self.quarto = True
        for k in ("href", "src", "poster"):
            v = a.get(k)
            if v and not re.match(r'^(https?:|mailto:|data:|javascript:|//)', v):
                refs.append((self.path, tag, v))

for dp, _, fns in os.walk(site):
    if "site_libs" in dp: continue
    for fn in fns:
        if fn.endswith(".html"):
            p = os.path.join(dp, fn); parser = P(p)
            parser.feed(open(p, encoding="utf-8").read()); ids[os.path.normpath(p)] = parser.ids
            if not parser.quarto: skipped.append(os.path.relpath(p, site))
            elif not parser.portal: no_portal.append(os.path.relpath(p, site))

for page in sorted(skipped): print(f"{page}: not rendered by Quarto, so it needs no link to {PORTAL}")
for page in sorted(no_portal): print(f"{page}: no <a href=\"{PORTAL}\">")
print(f"{len(ids) - len(skipped)} Quarto pages, {len(no_portal)} without a link to {PORTAL}")

bad = []
for page, tag, v in refs:
    url, frag = urldefrag(v)
    target = os.path.normpath(os.path.join(os.path.dirname(page), unquote(url))) if url else os.path.normpath(page)
    if url.endswith("/"): target = os.path.join(target, "index.html")
    if not os.path.exists(target):
        bad.append(f"{os.path.relpath(page, site)}: <{tag}> {v} -> missing file"); continue
    if frag and target in ids and frag not in ids[target]:
        bad.append(f"{os.path.relpath(page, site)}: <{tag}> {v} -> missing anchor #{frag}")
for b in sorted(set(bad)): print(b)
print(f"{len(refs)} local references in {len(ids)} pages, {len(set(bad))} broken")
sys.exit(1 if bad or no_portal else 0)  # non-zero fails the CI job
