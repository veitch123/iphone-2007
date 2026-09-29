# iPhone 2007 Replay

An RSS feed that replays real Apple news from June 2007 in real time. Every
headline is shifted forward 7,056 days and keeps its original US Pacific time of
day, so the original iPhone going on sale (Friday 29 June 2007, 6pm PT) lands
on iPhone Duo launch day, Friday 23 October 2026.

Subscribe: https://veitch123.github.io/iphone-2007/feed.xml

## How it works

- `items.txt` holds the headlines, one per line:
  `YYYY-MM-DD HH:MM (Pacific)|source|headline|url|exact-or-approx`
- `build.py` releases the headlines whose shifted time has passed and writes
  `_site/feed.xml` and `_site/index.html`. Standard library only.
- `.github/workflows/feed.yml` runs the build every 15 minutes and deploys to
  GitHub Pages only when a new headline is due.

Preview any moment locally:

```
python3 build.py 2026-10-23T18:10:00-07:00
open _site/index.html
```

## Timeline

Weekdays line up exactly (7,056 days is 1,008 weeks).

| 2026 | Replays as | What happened in 2007 |
| --- | --- | --- |
| Tue 29 Sep | Tue 5 Jun | New MacBook Pros |
| Mon 5 Oct | Mon 11 Jun | WWDC keynote, Safari for Windows |
| Mon 12 Oct | Mon 18 Jun | Longer battery life and glass screen announced |
| Fri 16 Oct (Duo pre-orders) | Fri 22 Jun | iPhone Guided Tour video |
| Tue 20 Oct | Tue 26 Jun | Service plans announced; first reviews |
| Fri 23 Oct (Duo launch) | Fri 29 Jun | iPhone goes on sale at 6pm PT |
| Sat 24 Oct | Sat 30 Jun | First impressions, sellouts |

Nothing is released ahead of its day: each day's headlines trickle out across
that day at their original times, and the next day's wait for the next day.
The replay starts with 5 June 2007 (29 September 2026) and ends with 2 July 2007
(26 October 2026). Headlines whose exact time is unknown are spaced out across
their day rather than bunched together.
