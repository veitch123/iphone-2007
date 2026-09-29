#!/usr/bin/env python3
"""Build the iPhone 2007 replay feed.

Every headline in items.txt is shifted forward by SHIFT_DAYS, keeping its
original US Pacific wall-clock time, so Friday 29 June 2007 (iPhone launch)
lands on Friday 23 October 2026 (iPhone Duo launch). Only headlines whose
shifted time has passed are written to _site/feed.xml and _site/index.html.

    python3 build.py                              # as of now
    python3 build.py 2026-10-23T18:10:00-07:00    # preview any moment
"""

import hashlib
import html
import os
import sys
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime
from pathlib import Path
from xml.sax.saxutils import escape

try:
    from zoneinfo import ZoneInfo
    PACIFIC = ZoneInfo("America/Los_Angeles")
    UK = ZoneInfo("Europe/London")
except Exception:  # no tz database: the whole replay window is PDT / BST
    PACIFIC = timezone(timedelta(hours=-7), "PDT")
    UK = timezone(timedelta(hours=1), "BST")

SHIFT_DAYS = 7056  # 2007-06-29 -> 2026-10-23
FIRST_DAY = "2007-06-05"  # = Tue 29 Sep 2026, the day the replay started; nothing earlier is ever released
ROOT = Path(__file__).resolve().parent
OUT = ROOT / "_site"
SITE_URL = os.environ.get("SITE_URL", "https://veitch123.github.io/iphone-2007/").rstrip("/") + "/"
TITLE = "iPhone 2007 Replay"
DESCRIPTION = (
    "Real Apple news from June 2007, replayed in real time so the original "
    "iPhone launch (29 June 2007) lands on iPhone Duo launch day, "
    "Friday 23 October 2026. Each headline arrives at its original Pacific time of day."
)


def load_items():
    items = []
    for n, line in enumerate((ROOT / "items.txt").read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) not in (4, 5):
            sys.exit(f"items.txt:{n}: expected 4 or 5 fields, got {len(parts)}")
        stamp, source, headline, url = parts[:4]
        if stamp[:10] < FIRST_DAY:
            continue
        approx = len(parts) == 5 and parts[4].lower().startswith("approx")
        naive = datetime.strptime(stamp, "%Y-%m-%d %H:%M")
        original = naive.replace(tzinfo=PACIFIC)
        replay = (naive + timedelta(days=SHIFT_DAYS)).replace(tzinfo=PACIFIC)
        guid = "iphone2007-" + hashlib.sha1(f"{stamp}|{source}|{headline}".encode()).hexdigest()[:16]
        items.append(dict(original=original, replay=replay, source=source,
                          headline=headline, url=url, approx=approx, guid=guid))
    items.sort(key=lambda i: (i["replay"], i["source"], i["headline"]))
    return items


def original_label(item):
    o = item["original"]
    when = o.strftime("%A %-d %B %Y") if item["approx"] else o.strftime("%A %-d %B %Y, %-I:%M%p").replace("AM", "am").replace("PM", "pm")
    return f"Originally published {when}" + (" (time approximate)" if item["approx"] else " PDT")


def rfc822(dt):
    return format_datetime(dt.astimezone(timezone.utc), usegmt=True)


def next_label(item):
    return item["replay"].astimezone(UK).strftime("%a %-d %b at %H:%M UK time")


def rss_head(site, last_build):
    return "\n".join([
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:dc="http://purl.org/dc/elements/1.1/">',
        "<channel>",
        f"<title>{escape(TITLE)}</title>",
        f"<link>{escape(site)}</link>",
        f'<atom:link href="{escape(site)}feed.xml" rel="self" type="application/rss+xml"/>',
        f"<description>{escape(DESCRIPTION)}</description>",
        "<language>en</language>",
        f"<lastBuildDate>{last_build}</lastBuildDate>",
        "<ttl>30</ttl>",
        "",
    ])


RSS_TAIL = "</channel>\n</rss>\n"


def item_xml(item):
    desc = f"<p>{html.escape(item['source'])}. {html.escape(original_label(item))}.</p>"
    return "\n".join([
        "<item>",
        f"<title>{escape(item['headline'])}</title>",
        f"<link>{escape(item['url'])}</link>",
        f'<guid isPermaLink="false">{item["guid"]}</guid>',
        f"<pubDate>{rfc822(item['replay'])}</pubDate>",
        f"<dc:creator>{escape(item['source'])}</dc:creator>",
        f"<category>{escape(item['source'])}</category>",
        f"<description>{escape(desc)}</description>",
        "</item>",
        "",
    ])


def item_html(item):
    uk = item["replay"].astimezone(UK).strftime("%a %-d %b, %H:%M")
    return (
        f'<li><a href="{html.escape(item["url"])}">{html.escape(item["headline"])}</a>'
        f'<span class="meta">{html.escape(item["source"])} · {uk} UK · '
        f'{html.escape(original_label(item))}</span></li>\n'
    )


def build_rss(released, now):
    last = rfc822(released[0]["replay"]) if released else rfc822(now)
    return rss_head(SITE_URL, last) + "".join(item_xml(i) for i in released) + RSS_TAIL


def build_html(released, upcoming, total, now):
    if upcoming:
        status = f"{len(released)} of {total} headlines released. Next one {next_label(upcoming[0])}."
    else:
        status = f"All {total} headlines released. The replay is over."
    rows = "".join(item_html(i) for i in released) or "<li>Nothing released yet.</li>\n"
    return page(SITE_URL, html.escape(status), rows)


def page(site, status, body):
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{TITLE}</title>
<link rel="alternate" type="application/rss+xml" title="{TITLE}" href="{site}feed.xml">
<style>
:root {{ --bg:#fbfbfa; --fg:#1d1d1f; --muted:#6e6e73; --link:#0a58ca; --rule:#e3e3e6; }}
@media (prefers-color-scheme: dark) {{ :root {{ --bg:#141416; --fg:#f2f2f4; --muted:#9a9aa0; --link:#7ab4ff; --rule:#2c2c30; }} }}
body {{ background:var(--bg); color:var(--fg); font:16px/1.5 -apple-system, BlinkMacSystemFont, "Helvetica Neue", sans-serif; margin:0; padding:32px 16px; }}
main {{ max-width:720px; margin:0 auto; }}
h1 {{ font-size:28px; margin:0 0 8px; }}
p {{ color:var(--muted); margin:0 0 12px; }}
a {{ color:var(--link); }}
.subscribe {{ display:inline-block; margin:4px 0 24px; font-weight:600; }}
ul {{ list-style:none; padding:0; margin:0; }}
li {{ padding:12px 0; border-top:1px solid var(--rule); }}
li a {{ text-decoration:none; font-weight:500; }}
.meta {{ display:block; color:var(--muted); font-size:13px; margin-top:2px; }}
</style>
</head>
<body>
<main>
<h1>{TITLE}</h1>
<p>{html.escape(DESCRIPTION)}</p>
<p>{status}</p>
<a class="subscribe" href="{site}feed.xml">Subscribe: {site}feed.xml</a>
<ul>
{body}
</ul>
</main>
</body>
</html>
"""


def main():
    now = datetime.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    items = load_items()
    released = [i for i in items if i["replay"] <= now][::-1]  # newest first
    upcoming = [i for i in items if i["replay"] > now]
    OUT.mkdir(exist_ok=True)
    (OUT / "feed.xml").write_text(build_rss(released, now), encoding="utf-8")
    (OUT / "index.html").write_text(build_html(released, upcoming, len(items), now), encoding="utf-8")
    print(f"{now.isoformat()}: {len(released)}/{len(items)} released")


if __name__ == "__main__":
    main()
