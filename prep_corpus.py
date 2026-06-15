"""Parse the official GDPR text into a clean, citable corpus.

Reads the EUR-Lex HTML of Regulation (EU) 2016/679 and turns its 99 articles
into retrieval chunks, each tagged with its article number and title so every
answer the app gives can cite a specific Article.

    python prep_corpus.py            # uses data/gdpr_eurlex.html if present
    python prep_corpus.py --download # re-fetch the latest from EUR-Lex

Source: EUR-Lex (https://eur-lex.europa.eu) — Regulation (EU) 2016/679 (GDPR).
EU legal texts are reusable under Commission Decision 2011/833/EU with
attribution; this is the official consolidated text.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup

DATA = Path(__file__).parent / "data"
HTML = DATA / "gdpr_eurlex.html"
URL = "https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32016R0679"
MAX_CHARS = 1100  # split longer articles into paragraph-level chunks


def load_html() -> str:
    if "--download" in sys.argv or not HTML.exists():
        print("Fetching GDPR from EUR-Lex…")
        r = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=120)
        r.raise_for_status()
        HTML.write_text(r.text, encoding="utf-8")
    return HTML.read_text(encoding="utf-8")


def parse_articles(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    paras = soup.find_all("p", class_=["oj-ti-art", "oj-sti-art", "oj-normal"])

    articles: list[dict] = []
    current = None
    expecting_title = False
    for p in paras:
        cls = p.get("class", [])
        text = re.sub(r"\s+", " ", p.get_text(" ", strip=True)).strip()
        if not text:
            continue
        if "oj-ti-art" in cls:
            m = re.match(r"Article\s+(\d+)", text)
            if not m:
                continue
            current = {"article": int(m.group(1)), "title": "", "body": []}
            articles.append(current)
            expecting_title = True
        elif "oj-sti-art" in cls and current is not None and expecting_title:
            current["title"] = text
            expecting_title = False
        elif "oj-normal" in cls and current is not None:
            current["body"].append(text)
    return articles


def chunk(articles: list[dict]) -> list[dict]:
    """One chunk per article, splitting long articles on paragraph boundaries."""
    chunks: list[dict] = []
    for art in articles:
        ref = f"Article {art['article']}"
        header = f"{ref} — {art['title']}"
        buf, size = [], 0
        part = 1

        def flush(buf, part):
            if not buf:
                return
            chunks.append({
                "id": f"art{art['article']:03d}-{part}",
                "article": art["article"],
                "title": art["title"],
                "ref": ref,
                "text": f"{header}\n\n" + " ".join(buf),
            })

        for para in art["body"]:
            if size + len(para) > MAX_CHARS and buf:
                flush(buf, part)
                part += 1
                buf, size = [], 0
            buf.append(para)
            size += len(para)
        flush(buf, part)
        if not art["body"]:  # title-only article still citable
            chunks.append({
                "id": f"art{art['article']:03d}-1", "article": art["article"],
                "title": art["title"], "ref": ref, "text": header,
            })
    return chunks


def main() -> None:
    articles = parse_articles(load_html())
    chunks = chunk(articles)
    (DATA / "corpus.json").write_text(json.dumps(chunks, ensure_ascii=False, indent=1))

    print(f"Parsed {len(articles)} articles -> {len(chunks)} chunks")
    print(f"corpus.json: {(DATA / 'corpus.json').stat().st_size/1024:.0f} KB")
    print("\nSample chunk:")
    sample = next(c for c in chunks if c["article"] == 33)  # breach notification
    print(sample["text"][:320], "…")


if __name__ == "__main__":
    main()
