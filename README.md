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
| `/card/timeline` | PRs, issues, commits per repo, yearly contributions |
| `/card/analytics` | commits, followers, contribution heatmap |
| `/card/activity` | latest public events + terminal |
| `/card/playground` | live `/api/projects` response |
| `/card/developer-os` | neofetch-style stats, GitHub API latency |
| `/card/city` | Contribution City: the last year as a 3D city, one building per day, plus streaks |
| `/card/tech-stack` | `TECH_STACK` with per-tool repo counts |
| `/card/smart-contracts` | Smart Contract Lab: a live `Profile.sol`, Solidity repos and detected Web3 tools |
| `/card/architecture`, `/card/cloud` | most used tools per layer, repos with Docker / GitHub Actions / AWS |
| `/card/achievements` | stars, commits, PRs, yearly contributions, repos, years on GitHub |
| `/card/what-i-build`, `/card/backend`, `/card/workflow`, `/card/problem-solution`, `/card/collaborate` | content from `app/config.py` |
| `/card/heading?title=&subtitle=&n=` | section heading |
| `/card/button?label=&icon=&primary=` | link buttons (github, linkedin, email, resume) |

Every card accepts `?username=` and `?n=` (the section number).

The hero, city and collaborate cards follow the time of day in India (sunrise, daytime, sunset, night):
the sky, sun or moon and the number of lit windows change with each hourly render.

JSON: `/api/profile`, `/api/projects`, `/api/github/stats`, `/api/activity`, `/api/experience`, `/api/tech-stack`, `/health`.

## Customise

Edit `app/config.py`. It holds the tagline, about text, tech stack, timeline, "currently exploring" percentages,
workflow and pinned repos (`FEATURED_REPOS`). `TECH_ALIASES` controls how each tech-stack item is spotted in a repo
(languages, topics, description, `package.json` / `requirements.txt` dependencies, Dockerfile, workflows). Adding
topics to your repos on GitHub makes the counts more accurate.
