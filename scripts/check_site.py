#!/usr/bin/env python3
"""Check every local href/src in a rendered Quarto site: the file exists and
any #anchor exists in it. Usage: check_site.py SITE_DIR"""
import os, re, sys
from html.parser import HTMLParser
from urllib.parse import urldefrag, unquote

site = sys.argv[1]
ids, refs = {}, []

class P(HTMLParser):
    def __init__(self, path):
        super().__init__(); self.path = path; self.ids = set()
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a: self.ids.add(a["id"])
        if tag == "a" and "name" in a: self.ids.add(a["name"])
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
