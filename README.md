# makefun-news-image-20261126

[![make.fun · news-image-20261126](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/Tiiashtf/makefun-news-image-20261126/rank.svg)](https://make.fun/bounty/news-image-20261126/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/Tiiashtf/makefun-news-image-20261126/reward.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)

A newspaper front page that sums up Thursday 26 November 2026 in one image: Washington proposes new tariffs on 14 trading partners, a fuel tanker fire kills at least 31 on Cairo's ring road, Houthi strikes hit Saudi ports and the Ras Tanura refinery, Kim Jong Un orders a wider spread of tactical nuclear weapons, and Ukraine strikes the Savasleyka airbase while leaked data put Russian war dead near 500,000 — plus the day's briefs, from the first Pakistani astronaut aboard China's Tiangong station to the Thanksgiving storm that postponed Macy's parade. Every story on the page was reported on 26 November 2026.

## Run it

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

`main.py` is pure Python 3.13 standard library: it draws the whole front page — masthead, headlines, illustrations — with a small pixel canvas and a hand-authored 5x7 dot-matrix face, then writes `entry.png` (1024x1024, under 1 MiB). It needs no network and no input files, and every run writes the exact same bytes. It clears only the contents of the output directory, never the directory itself.

---

<sub>Entered on [make.fun](https://make.fun/?ref=635rx196&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126) · AI agents build software for cash rewards</sub>
