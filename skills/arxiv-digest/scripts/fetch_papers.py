#!/usr/bin/env python3
"""Fetch recent AI/ML papers from arXiv RSS feeds and rank by cross-listing."""

import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
import json
import sys
import time
import re
from datetime import datetime, timezone

CATEGORIES = ["cs.AI", "cs.LG", "cs.CL", "cs.CV", "cs.RO", "stat.ML"]
RSS_BASE = "https://rss.arxiv.org/rss"
REQUEST_DELAY = 2
TIMEOUT = 30
MAX_RETRIES = 2
RETRY_BACKOFF = 10

RSS_NAMESPACES = {
    "dc": "http://purl.org/dc/elements/1.1/",
    "arxiv": "http://arxiv.org/schemas/atom",
}


def clean_html(text):
    return re.sub(r"<[^>]+>", "", text).strip()


def fetch_rss(category):
    url = f"{RSS_BASE}/{category}"
    last_error = None

    for attempt in range(MAX_RETRIES + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "ArxivDigest/1.0"})
            with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                data = resp.read().decode("utf-8")
            break
        except urllib.error.HTTPError as e:
            last_error = f"HTTP {e.code}"
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_BACKOFF)
                continue
            return [], last_error
        except Exception as e:
            last_error = str(e)[:100]
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_BACKOFF)
                continue
            return [], last_error
    else:
        return [], last_error or "unknown error"

    try:
        root = ET.fromstring(data)
    except ET.ParseError as e:
        return [], f"XML parse error: {e}"

    papers = []
    for item in root.findall(".//item"):
        try:
            title = item.findtext("title", "").strip()
            link = item.findtext("link", "").strip()
            description = item.findtext("description", "").strip()

            link_match = re.search(r"(?:arxiv\.org/abs/|ar5iv\.labs\.ar5iv\.org/html/)(\d+\.\d+)", description)
            if not link_match:
                link_match = re.search(r"(\d{4}\.\d{4,5})", link + description)
            arxiv_id = link_match.group(1) if link_match else ""

            arxiv_link = f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else link

            creators = item.findall("dc:creator", RSS_NAMESPACES)
            authors = [c.text.strip() for c in creators if c.text]

            abstract_match = re.search(
                r"Abstract\s*:\s*(.+?)(?:\s*\\\\\s*|\s*$)", description, re.DOTALL
            )
            if not abstract_match:
                abstract_match = re.search(
                    r"</p>.*?<p[^>]*>(.+?)</p>", description, re.DOTALL
                )
            if not abstract_match:
                parts = description.split("\n")
                abstract_match = None
                abstract_text = " ".join(
                    p for p in parts if p.strip() and not p.startswith("<") and len(p) > 50
                )
            else:
                abstract_text = abstract_match.group(1).strip()

            abstract_text = clean_html(abstract_text[:600])

            subjects = item.findall("dc:subject", RSS_NAMESPACES)
            cats = [s.text.strip() for s in subjects if s.text] or [category]

            published = item.findtext("pubDate", "")

            if arxiv_id:
                papers.append(
                    {
                        "arxiv_id": arxiv_id,
                        "title": title,
                        "authors": authors,
                        "abstract": abstract_text,
                        "link": arxiv_link,
                        "primary_category": category,
                        "categories": cats,
                        "published": published,
                    }
                )
        except Exception:
            continue

    return papers, None


def rank_papers(papers_dict):
    papers = list(papers_dict.values())
    for p in papers:
        p["cross_list_count"] = len(set(p["categories"]))
    papers.sort(key=lambda p: (-p["cross_list_count"], p["published"]))
    return papers


def main():
    all_papers = {}
    errors = []

    for i, cat in enumerate(CATEGORIES):
        papers, err = fetch_rss(cat)
        if err:
            errors.append(f"{cat}: {err}")
        for p in papers:
            aid = p["arxiv_id"]
            if aid not in all_papers:
                all_papers[aid] = p
            else:
                existing_cats = set(all_papers[aid]["categories"])
                new_cats = set(p["categories"])
                all_papers[aid]["categories"] = list(existing_cats | new_cats)
        if i < len(CATEGORIES) - 1:
            time.sleep(REQUEST_DELAY)

    ranked = rank_papers(all_papers)

    if len(ranked) == 0:
        result = {
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "total_fetched": 0,
            "top_paper": None,
            "additional_papers": [],
            "error": "No papers found" + ("; " + "; ".join(errors) if errors else ""),
        }
    else:
        result = {
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "total_fetched": len(ranked),
            "top_paper": ranked[0],
            "additional_papers": ranked[1:5],
            "error": "; ".join(errors) if errors else None,
        }

    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
