# Profile API

Backend for the [alishaaverma](https://github.com/alishaaverma) GitHub profile README.
It renders animated SVG cards from live GitHub data. The README embeds them as `<img>` tags.

GitHub strips JavaScript from READMEs, so the API renders every card on the server. All animation
is CSS/SMIL inside the SVG. That runs fine in GitHub's `<img>` tags.

## Run locally

```bash
pip install -r requirements.txt
cp .env.example .env            # optional; add GITHUB_TOKEN
uvicorn app.main:app --reload
```

Open http://localhost:8000 to preview every card.

## Publish (GitHub Actions — no public server needed)

`.github/workflows/profile-cards.yml` runs every hour (and on every push to `main`). It runs
`generate.py`, which renders all cards from live GitHub data. The cards are force-pushed to the
`output` branch of `alishaaverma/alishaaverma`, and the profile README loads them from
`https://raw.githubusercontent.com/alishaaverma/alishaaverma/output/<card>.svg`.

Setup (once):
1. Create a **fine-grained** token (GitHub → Settings → Developer settings → Fine-grained tokens) with
   access to **only** `alishaaverma/alishaaverma` and **Contents: Read and write**.
2. In this repo, open Settings → Secrets and variables → Actions and add it as `PROFILE_REPO_TOKEN`.
3. Push, then confirm the **Profile cards** run is green in the Actions tab.

To run it locally: `python generate.py --out dist`

The FastAPI server (`app/main.py`, `index.py`) still works for local previews, or for a public deployment.

## Endpoints

| SVG card | Data |
|---|---|
| `/card/hero` | name, location, repos, followers |
| `/card/about` | repos, account age |
| `/card/project/{0-3}` | top repos: stars, forks, language, topics, last push |
| `/card/timeline` | journey built from repo creation years (titles in `TIMELINE_TITLES`), PRs, issues, commits per repo |
| `/card/analytics` | commits, followers, contribution heatmap; live "Currently Exploring" (tools used by repos pushed in the last 90 days) and the newest lines of `TIL.md` in your `til` repo |
| `/card/activity` | latest public events + terminal |
| `/card/playground` | live `/api/projects` response |
| `/card/developer-os` | neofetch-style stats, GitHub API latency |
| `/card/city` | Contribution City: the last year as a 3D city (one building per day), streaks, live weather + AQI, festival themes, a flooded street with paper boats when it rains, and Byte, a coding pet that grows with your best streak, sulks when you stop committing counts the cookies visitors feed it (a friend chick joins every 10), and dresses for the moment: mask when the AQI is bad, umbrella in rain, Santa hat, party hat, diya, nightcap. At night your repos shine as constellations, and one car drives the street per contribution today |
| `/card/tech-stack` | `TECH_STACK` with per-tool repo counts |
| `/card/smart-contracts` | Smart Contract Lab: a live `Profile.sol`, Solidity repos and detected Web3 tools |
| `/card/now-building` | most recently pushed repo, its latest commit and 30-day commit momentum |
| `/card/community` | Community Corner: live 👍 votes on "idea" issues, and AMA questions you have answered |
| `/card/coding-dna` | Night Owl / Early Bird clock from commit times, and generative art from the latest commit hashes |
| `/card/architecture`, `/card/cloud` | most used tools per layer, repos with Docker / GitHub Actions / AWS |
| `/card/achievements` | milestones plus unlockable badges; from 1 Dec to 7 Jan it becomes your year in review (Wrapped) |
| `/card/what-i-build`, `/card/backend`, `/card/workflow`, `/card/problem-solution`, `/card/collaborate` | content from `app/config.py` |
| `/card/heading?title=&subtitle=&n=` | section heading |
| `/card/button?label=&icon=&primary=` | link buttons (github, linkedin, email, resume) |

Every card accepts `?username=` and `?n=` (the section number).

The hero, city and collaborate cards follow the time of day in India (sunrise, daytime, sunset, night):
the sky, sun or moon and the number of lit windows change with each hourly render. On Diwali, Holi,
Eid (both), Navratri/Durga Puja, Dussehra, Ganesh Chaturthi, Janmashtami, Raksha Bandhan, Onam, Gurpurab,
Chhath, Christmas, Halloween, Makar Sankranti, New Year, Independence Day, Republic Day and your birthday
(`BIRTHDAY` in `app/config.py`) the hero and Contribution City also get a festival theme. The dates are
read live from Google's public "Holidays in India" calendar on every render, so festivals that move each
year (Diwali, Holi, Eid) need no updates. If the calendar can't be reached, the fixed-date ones still show.

Every card has a light variant: when the viewer's browser or OS prefers light mode, the card switches
to a light palette (terminals and the code editor stay dark).

JSON: `/api/profile`, `/api/projects`, `/api/github/stats`, `/api/activity`, `/api/experience`, `/api/tech-stack`, `/health`.

## Customise

Edit `app/config.py`. It holds the tagline, about text, tech stack, journey titles, festival dates, "currently exploring" percentages,
workflow and pinned repos (`FEATURED_REPOS`). `TECH_ALIASES` controls how each tech-stack item is spotted in a repo
(languages, topics, description, `package.json` / `requirements.txt` dependencies, Dockerfile, workflows). Adding
topics to your repos on GitHub makes the counts more accurate.

## Feed Byte

The "Feed Byte a cookie" button in the profile README opens an issue titled `Feed Byte 🍪` on the profile
repo. `.github/workflows/feed-byte.yml` in that repo thanks the visitor and closes the issue, and the next
render of Contribution City shows how many cookies Byte got and who fed it last. Issues must be enabled on the
profile repo.

## Today I Learned

Create a public repo named `til` (or change `TIL_REPO` in `app/config.py`) with a `TIL.md`, newest first:

```markdown
- 2026-10-23: Solidity events are a cheap way to log data on-chain
- 2026-10-20: FastAPI background tasks run after the response is sent
```

The analytics card shows the newest two entries.

## Community Corner

- **Vote:** open issues on the profile repo yourself, one per project idea, and give them the label `idea`.
  Visitors vote with a 👍 reaction; the card shows the live counts.
- **Ask Me Anything:** visitors open an issue whose title starts with `AMA`. Answer it in a comment; the card
  shows your latest two answered questions.
