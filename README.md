# iPhone 2007 Replay

An RSS feed that replays real Apple news from June 2007 in real time. Every
headline is shifted forward 7,056 days and keeps its original US Pacific time of
day, so the original iPhone going on sale (Friday 29 June 2007, 6pm PT) lands
on iPhone Duo launch day, Friday 23 October 2026.

Subscribe: https://iphone-2007.james-veitch.workers.dev/feed.xml

## How it works

The feed is a Cloudflare Worker (free plan). Each time a reader checks, the
Worker includes only the headlines whose replay time has passed. Nothing runs
between checks, and nothing is scheduled.

- `items.txt` holds the headlines, one per line:
  `YYYY-MM-DD HH:MM (Pacific)|source|headline|url|exact-or-approx`
- `build.py` renders every headline and can build a static copy of the feed
  for any moment, for previewing. Standard library only.
- `make_worker.py` packs the rendered headlines into `worker/src/data.js`.
- `worker/src/index.js` is the Worker itself.

Preview any moment locally:

```
python3 build.py 2026-10-23T18:10:00-07:00
open _site/index.html
```

After changing `items.txt`, republish:

```
python3 make_worker.py
cd worker && npx wrangler deploy
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
