# ⚾ The 1000 Club

> Count down from **1000** to exactly **0** using MLB players' career home run totals.

A Wordle-style daily baseball puzzle game. Every day, a new starting rule challenges how you begin your countdown. Reach exactly zero in as few picks as possible.

**[▶ Play Now](https://yourusername.github.io/the-1000-club/)**

---

## How to Play

1. **Goal:** Reduce the counter from **1000 to exactly 0** using career HR totals
2. **Daily Rule:** Your first player must satisfy the day's rule (e.g. "must be a CF" or "must have played for the Yankees")
3. **Search:** Type any MLB player's name — past or present
4. **No Repeats:** Each player can only be used once per game
5. **Lives:** You get **3 lives**. Going over the remaining count costs a life
6. **Score:** Fewest picks wins. Beat the daily **par** for a perfect score!

## Scoring

| Result | Description |
|--------|-------------|
| 🌟 Perfect | Matched or beat par |
| 🎯 Great | 1–2 picks above par |
| ✅ Nice | 3–5 picks above par |
| ⚾ Got It | Solved but well above par |
| 💀 Struck Out | Used all 3 lives |

Share your results with the emoji grid — just like Wordle!

---

## Running Locally

Just open `index.html` in a browser. No build step required.

```bash
git clone https://github.com/yourusername/the-1000-club.git
cd the-1000-club
open index.html
```

## Deploying to GitHub Pages

1. Push this repo to GitHub
2. Go to **Settings → Pages**
3. Set source to **Deploy from a branch → main → / (root)**
4. Your game will be live at `https://yourusername.github.io/the-1000-club/`

---

## Player Data

- **`players.json`** — 250+ MLB players with career HR totals, positions, and teams
- **Nightly updates** — A GitHub Action runs every morning at 6 AM UTC, fetching the latest career HR totals for all active players from the free [MLB Stats API](https://statsapi.mlb.com)
- No API key required

### Manually triggering an update

In your repo on GitHub, go to **Actions → Update Active Player Stats → Run workflow**.

---

## Project Structure

```
/
├── index.html              # Entire game (HTML + CSS + JS, single file)
├── players.json            # Player database
├── scripts/
│   └── update_stats.py     # Nightly stats updater
└── .github/
    └── workflows/
        └── update-players.yml  # GitHub Action schedule
```

---

## Contributing

Want to add more players or improve the rule set? PRs welcome!

- Add players to `players.json` following the existing schema
- New rules can be added in the `RULES` array in `index.html`

```json
{
  "name": "Player Name",
  "hr": 123,
  "positions": ["CF", "RF"],
  "teams": ["NYY", "BOS"],
  "active": false
}
```

---

*Built with vanilla HTML/CSS/JS. No frameworks. No dependencies. Just baseball.*
