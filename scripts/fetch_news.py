#!/usr/bin/env python3
"""يجلب أخبار الألعاب من خلاصات RSS الرسمية للمواقع الستة ويكتب data/news.json"""
import calendar
import datetime as dt
import html
import json
import re
import sys
from pathlib import Path

import feedparser

UA = "Mozilla/5.0 (compatible; LeaderGamesBot/1.0; +https://github.com)"
OUT = Path(__file__).resolve().parent.parent / "data" / "news.json"
MAX_PER_FEED = 40
MAX_TOTAL = 250
EXCERPT_LEN = 200

# كل مصدر له قائمة روابط بديلة تُجرَّب بالترتيب
SOURCES = {
    "IGN": ["https://feeds.feedburner.com/ign/games-all",
            "https://www.ign.com/rss/v2/articles/feed?categories=games"],
    "GameSpot": ["https://www.gamespot.com/feeds/news/"],
    "Eurogamer": ["https://www.eurogamer.net/feed"],
    "GamesRadar+": ["https://www.gamesradar.com/rss/"],
    "Kotaku": ["https://kotaku.com/rss"],
    "Gematsu": ["https://www.gematsu.com/feed"],
}

PLATFORM_KEYWORDS = {
    "console": [r"\bps5\b", r"\bps4\b", r"playstation", r"\bxbox\b", r"series x",
                r"nintendo", r"\bswitch\b", r"switch 2", r"\bconsole"],
    "pc": [r"\bpc\b", r"\bsteam\b", r"epic games", r"windows", r"\bgog\b",
           r"steam deck", r"\bnvidia\b", r"\bamd\b", r"\brtx\b"],
    "mobile": [r"\bmobile\b", r"\bios\b", r"\bandroid\b", r"iphone", r"\bipad\b",
               r"google play", r"app store"],
}


def clean(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text or "")
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def excerpt(text: str) -> str:
    text = clean(text)
    if len(text) <= EXCERPT_LEN:
        return text
    return text[:EXCERPT_LEN].rsplit(" ", 1)[0] + "…"


def detect_platforms(blob: str) -> list:
    blob = blob.lower()
    found = [p for p, pats in PLATFORM_KEYWORDS.items()
             if any(re.search(x, blob) for x in pats)]
    return found or ["general"]


def find_image(entry) -> str:
    for key in ("media_thumbnail", "media_content"):
        for m in entry.get(key, []) or []:
            if m.get("url"):
                return m["url"]
    for enc in entry.get("enclosures", []) or []:
        if enc.get("type", "").startswith("image") and enc.get("href"):
            return enc["href"]
    for link in entry.get("links", []) or []:
        if link.get("type", "").startswith("image") and link.get("href"):
            return link["href"]
    blobs = [entry.get("summary", "")]
    blobs += [c.get("value", "") for c in entry.get("content", []) or []]
    for b in blobs:
        m = re.search(r'<img[^>]+src=["\']([^"\']+)', b or "")
        if m:
            return m.group(1)
    return ""


def entry_date(entry) -> dt.datetime:
    for key in ("published_parsed", "updated_parsed"):
        t = entry.get(key)
        if t:
            return dt.datetime.fromtimestamp(calendar.timegm(t), dt.timezone.utc)
    return dt.datetime.now(dt.timezone.utc)


def fetch_source(name: str, urls: list) -> list:
    for url in urls:
        try:
            feed = feedparser.parse(url, agent=UA)
        except Exception as exc:  # noqa: BLE001
            print(f"[{name}] error {url}: {exc}", file=sys.stderr)
            continue
        if not feed.entries:
            print(f"[{name}] no entries at {url}", file=sys.stderr)
            continue
        items = []
        for e in feed.entries[:MAX_PER_FEED]:
            link = e.get("link")
            title = clean(e.get("title", ""))
            if not link or not title:
                continue
            tags = " ".join(t.get("term", "") for t in e.get("tags", []) or [])
            summary = e.get("summary", "")
            items.append({
                "title": title,
                "link": link,
                "source": name,
                "date": entry_date(e).isoformat(),
                "excerpt": excerpt(summary),
                "image": find_image(e),
                "platforms": detect_platforms(f"{title} {tags} {clean(summary)}"),
            })
        print(f"[{name}] {len(items)} items")
        return items
    return []


def main() -> int:
    all_items, seen = [], set()
    for name, urls in SOURCES.items():
        for it in fetch_source(name, urls):
            if it["link"] not in seen:
                seen.add(it["link"])
                all_items.append(it)
    if not all_items:
        print("No items fetched from any source; aborting.", file=sys.stderr)
        return 1
    all_items.sort(key=lambda x: x["date"], reverse=True)
    payload = {
        "updated": dt.datetime.now(dt.timezone.utc).isoformat(),
        "count": len(all_items[:MAX_TOTAL]),
        "items": all_items[:MAX_TOTAL],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Wrote {payload['count']} items to {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
