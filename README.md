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

## Deploy (Vercel — recommended)

1. Push this folder to its own repo, e.g. `alishaaverma/profile-api`.
2. On vercel.com, click **Add New → Project**, import the repo and keep the defaults (`index.py` is the entrypoint).
3. Under **Settings → Environment Variables**, add:
   - `GITHUB_USERNAME` = `alishaaverma`
   - `GITHUB_TOKEN` = a GitHub token with **no scopes**, created under Settings → Developer settings → Tokens (classic).
     Without it you get 60 requests/hour, which is not enough.
4. Point the profile README at the deployment:
   ```bash
   ./set_api_url.sh https://<your-project>.vercel.app
   ```
   Commit and push `alishaaverma/README.md`.

Render also works (`render.yaml` is included). On the free plan, though, the service sleeps when idle.
GitHub's image proxy then times out and the cards show as broken images.

## How "real-time" works

- Data is fetched live from the GitHub REST/GraphQL APIs and cached in memory for up to 10 minutes.
- Responses send `Cache-Control: max-age=CACHE_SECONDS` (default 1800s). GitHub's image proxy (camo) refetches after that,
  so the profile stays within ~30 minutes of live. Lower `CACHE_SECONDS` for fresher cards.
- Each live card shows a `live · <time IST>` stamp with the render time.
- Project cards link through `/go/project/{i}`. That redirects to whichever repo is currently in slot *i*.

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
| `/card/tech-stack`, `/card/what-i-build`, `/card/architecture`, `/card/backend`, `/card/cloud`, `/card/workflow`, `/card/problem-solution`, `/card/achievements`, `/card/collaborate` | content from `app/config.py` |
| `/card/heading?title=&subtitle=&n=` | section heading |
| `/card/button?label=&icon=&primary=` | link buttons (github, linkedin, email, resume) |

Every card accepts `?username=` and `?n=` (the section number).

JSON: `/api/profile`, `/api/projects`, `/api/github/stats`, `/api/activity`, `/api/experience`, `/api/tech-stack`, `/health`.

## Customise

Edit `app/config.py`. It holds the tagline, about text, tech stack, timeline, "currently exploring" percentages,
achievements, workflow and pinned repos (`FEATURED_REPOS`).
