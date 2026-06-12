#!/usr/bin/env python3
"""One-time snapshot puller for the wildcard concept pool.

Pulls Wikipedia Vital Articles (levels 3 + 4) titles from the per-topic tracking
categories, keeping only concept-bearing topics (People and History are excluded at the
source - a person or an event is never a "concept"). Titles only; used as inspiration
pointers, never reproducing article text. Prints one title per line to stdout.

Re-runnable; the draw itself never touches the network. See docs/concepts-sourcing.md.
"""
import json
import re
import sys
import urllib.parse
import urllib.request

BASE = "https://en.wikipedia.org/w/api.php"
UA = "wildcard-skill/1.0 (https://github.com/globalanomalyindex/wildcard; one-time vital-articles snapshot)"
EXCLUDE_TOPICS = ("People", "History")


def get(params):
    url = BASE + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return json.load(urllib.request.urlopen(req, timeout=30))


def all_categories(prefix):
    out, cont = [], None
    while True:
        p = {"action": "query", "list": "allcategories", "acprefix": prefix,
             "aclimit": "500", "format": "json", "formatversion": "2"}
        if cont:
            p["accontinue"] = cont
        d = get(p)
        for c in d["query"]["allcategories"]:
            out.append(c["category"] if isinstance(c, dict) else c)
        cont = d.get("continue", {}).get("accontinue")
        if not cont:
            return out


def topic(cat):
    m = re.search(r" in (.+)$", cat)
    return m.group(1) if m else ""


def category_articles(cat):
    """Article titles via the talk-page members of a tracking category."""
    out, cont = [], None
    while True:
        p = {"action": "query", "list": "categorymembers", "cmtitle": cat,
             "cmnamespace": "1", "cmlimit": "500", "format": "json", "formatversion": "2"}
        if cont:
            p["cmcontinue"] = cont
        d = get(p)
        for m in d["query"]["categorymembers"]:
            t = m["title"]
            if t.startswith("Talk:"):
                out.append(t[5:])
        cont = d.get("continue", {}).get("cmcontinue")
        if not cont:
            return out


def main():
    cats = []
    for level in ("3", "4"):
        cats += ["Category:" + c for c in all_categories(f"Wikipedia level-{level} vital articles in ")]
    keep = [c for c in cats if not any(topic(c).startswith(x) for x in EXCLUDE_TOPICS)]
    titles = set()
    for cat in keep:
        titles.update(category_articles(cat))
    for t in sorted(titles):
        print(t)
    print(f"# {len(titles)} concept-bearing candidates from {len(keep)} topics", file=sys.stderr)


if __name__ == "__main__":
    main()
