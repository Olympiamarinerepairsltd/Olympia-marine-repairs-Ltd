from __future__ import annotations

import hashlib
import html
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import feedparser
import requests

BASE_DIR = Path(__file__).resolve().parents[1]
CONTENT_DIR = BASE_DIR / "content"
SOURCES_FILE = CONTENT_DIR / "rss-sources.json"
MANUAL_FILE = CONTENT_DIR / "manual-newsletter-items.json"
OUTPUT_FILE = CONTENT_DIR / "newsletter-hub.json"
MAX_ITEMS = 20

TAG_RE = re.compile(r"<[^>]+>")
WS_RE = re.compile(r"\s+")


def load_json(path: Path, default):
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def clean_text(value: str | None) -> str:
    if not value:
        return ""
    value = html.unescape(value)
    value = TAG_RE.sub(" ", value)
    value = WS_RE.sub(" ", value).strip()
    return value


def iso_now() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def iso_from_struct(struct_time) -> str:
    if not struct_time:
        return iso_now()
    return (
        datetime.fromtimestamp(time.mktime(struct_time), tz=timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def make_id(seed: str) -> str:
    return hashlib.sha1(seed.encode("utf-8")).hexdigest()[:12]


def normalize_manual_items(raw_manual: dict) -> list[dict]:
    items = []

    for item in raw_manual.get("items", []):
        url = (item.get("url") or "").strip()
        seed = url or f"manual-{item.get('date', '')}-{item.get('title', {}).get('en', '')}"

        items.append(
            {
                "id": item.get("id") or make_id(seed),
                "type": "manual",
                "featured": bool(item.get("featured", False)),
                "sourceLabel": item.get("sourceLabel", "Olympia Marine Repairs Ltd"),
                "category": item.get("category", "company"),
                "url": url,
                "publishedAt": item.get("date") or iso_now(),
                "title": {
                    "el": clean_text(item.get("title", {}).get("el")),
                    "en": clean_text(item.get("title", {}).get("en")),
                },
                "summary": {
                    "el": clean_text(item.get("summary", {}).get("el")),
                    "en": clean_text(item.get("summary", {}).get("en")),
                },
            }
        )

    return items


def fetch_feed(source: dict) -> list[dict]:
    url = (source.get("url") or "").strip()
    if not url:
        return []

    response = requests.get(
        url,
        timeout=20,
        headers={"User-Agent": "OlympiaMarineRepairsRSSBot/1.0"},
    )
    response.raise_for_status()

    parsed = feedparser.parse(response.content)
    items = []

    for entry in parsed.entries[: int(source.get("limit", 5))]:
        link = (entry.get("link") or "").strip()
        title = clean_text(entry.get("title"))
        summary = clean_text(entry.get("summary") or entry.get("description"))
        published_at = iso_from_struct(
            entry.get("published_parsed") or entry.get("updated_parsed")
        )

        if not link or not title:
            continue

        items.append(
            {
                "id": make_id(link),
                "type": "rss",
                "featured": False,
                "sourceLabel": source.get("label", "RSS"),
                "category": source.get("category", "industry"),
                "url": link,
                "publishedAt": published_at,
                "title": {
                    "el": title,
                    "en": title
                },
                "summary": {
                    "el": summary[:240],
                    "en": summary[:240]
                },
            }
        )

    return items


def main() -> None:
    CONTENT_DIR.mkdir(parents=True, exist_ok=True)

    sources_data = load_json(SOURCES_FILE, {"sources": []})
    manual_data = load_json(MANUAL_FILE, {"items": []})

    items = normalize_manual_items(manual_data)

    for source in sources_data.get("sources", []):
      if not source.get("enabled", True):
          continue

      try:
          items.extend(fetch_feed(source))
      except Exception as exc:
          print(f"Skipping source {source.get('label', source.get('url'))}: {exc}")

    deduped = []
    seen_urls = set()

    for item in items:
        url = item.get("url")
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)
        deduped.append(item)

    deduped.sort(key=lambda x: x.get("publishedAt", ""), reverse=True)

    payload = {
        "updatedAt": iso_now(),
        "items": deduped[:MAX_ITEMS],
    }

    OUTPUT_FILE.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print(f"Wrote {len(payload['items'])} items to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()