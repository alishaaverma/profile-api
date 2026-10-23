"""Profile API: animated SVG cards + JSON endpoints backed by live GitHub data."""

from __future__ import annotations

import asyncio
import traceback

from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response

from . import config
from . import github as gh
from .cards import engineering as eng
from .cards import live
from .cards import profile as prof
from .cards.theme import ORANGE, esc, frame, svg

app = FastAPI(title="GitHub Profile API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["GET"], allow_headers=["*"])

CACHE = f"public, max-age={config.CACHE_SECONDS}, s-maxage={config.CACHE_SECONDS}, stale-while-revalidate=86400"


def _svg(body: str, cache: str = CACHE) -> Response:
    return Response(body, media_type="image/svg+xml; charset=utf-8", headers={"Cache-Control": cache})


def _error_card(msg: str) -> Response:
    b = frame(850, 90, ember=False)
    b += f'<text x="24" y="40" font-size="14" font-weight="700" fill="{ORANGE}">Card temporarily unavailable</text>'
    b += f'<text x="24" y="62" font-size="11" class="muted mono">{esc(msg[:120])}</text>'
    # short cache so the card recovers quickly
    return _svg(svg(850, 90, b, title="error"), cache="public, max-age=120, s-maxage=120")


def _user(username: str | None) -> str:
    return (username or config.GITHUB_USERNAME).strip()


async def _render(fn):
    try:
        return _svg(await fn())
    except Exception as e:  # never return a broken image to GitHub
        traceback.print_exc()
        return _error_card(str(e))


# -------------------------------------------------------------- cards

@app.get("/card/hero")
async def card_hero(username: str | None = None):
    async def f():
        return prof.hero(await gh.get_user(_user(username)))
    return await _render(f)


@app.get("/card/about")
async def card_about(username: str | None = None, n: int = 2):
    async def f():
        return prof.about(await gh.get_user(_user(username)), n)
    return await _render(f)


@app.get("/card/city")
async def card_city(username: str | None = None):
    async def f():
        login = _user(username)
        user, cal = await asyncio.gather(gh.get_user(login), gh.get_calendar(login))
        return live.contribution_city(user, cal)
    return await _render(f)


@app.get("/card/smart-contracts")
async def card_smart_contracts(username: str | None = None):
    async def f():
        login = _user(username)
        user, repos, tech = await asyncio.gather(gh.get_user(login), gh.get_repos(login), gh.get_tech(login))
        return live.smart_contract_lab(user, repos, tech)
    return await _render(f)


@app.get("/card/tech-stack")
async def card_tech(username: str | None = None, n: int = 3):
    async def f():
        return prof.tech_stack(await gh.get_tech(_user(username)), n)
    return await _render(f)


@app.get("/card/what-i-build")
async def card_build(n: int = 4):
    return await _render(lambda: asyncio.sleep(0, prof.what_i_build(n)))


@app.get("/card/heading")
async def card_heading(title: str, subtitle: str = "", n: int | None = None):
    return await _render(lambda: asyncio.sleep(0, prof.section_heading(title, subtitle, n)))


@app.get("/card/project/{index}")
async def card_project(index: int, username: str | None = None):
    async def f():
        login = _user(username)
        repos = await gh.get_repos(login)
        top = gh.featured(repos["repos"], 4)
        return live.project_card(top[index] if 0 <= index < len(top) else None, index, login)
    return await _render(f)


@app.get("/card/architecture")
async def card_architecture(username: str | None = None, n: int = 6):
    async def f():
        return eng.architecture(await gh.get_tech(_user(username)), n)
    return await _render(f)


@app.get("/card/timeline")
async def card_timeline(username: str | None = None, n: int = 7):
    async def f():
        login = _user(username)
        user, stats, cal = await asyncio.gather(gh.get_user(login), gh.get_stats(login), gh.get_calendar(login))
        return live.timeline_opensource(user, stats, cal, n)
    return await _render(f)


@app.get("/card/analytics")
async def card_analytics(username: str | None = None, n: int = 9):
    async def f():
        login = _user(username)
        user, stats, cal = await asyncio.gather(gh.get_user(login), gh.get_stats(login), gh.get_calendar(login))
        return live.analytics_exploring(user, stats, cal, n)
    return await _render(f)


@app.get("/card/activity")
async def card_activity(username: str | None = None, n: int = 11):
    async def f():
        login = _user(username)
        user, repos, events = await asyncio.gather(gh.get_user(login), gh.get_repos(login), gh.get_events(login))
        return live.activity_terminal(user, repos, events, n)
    return await _render(f)


@app.get("/card/playground")
async def card_playground(request: Request, username: str | None = None, n: int = 13):
    async def f():
        return live.playground(await gh.get_repos(_user(username)), str(request.base_url) + "api/projects", n)
    return await _render(f)


@app.get("/card/backend")
async def card_backend(n: int = 14):
    return await _render(lambda: asyncio.sleep(0, eng.backend_database(n)))


@app.get("/card/cloud")
async def card_cloud(username: str | None = None, n: int = 16):
    async def f():
        return eng.cloud_deploy(await gh.get_tech(_user(username)), n)
    return await _render(f)


@app.get("/card/workflow")
async def card_workflow(n: int = 17):
    return await _render(lambda: asyncio.sleep(0, eng.workflow(n)))


@app.get("/card/problem-solution")
async def card_problem(n: int = 18):
    return await _render(lambda: asyncio.sleep(0, eng.problem_solution(n)))


@app.get("/card/developer-os")
async def card_devos(username: str | None = None, n: int = 19):
    async def f():
        login = _user(username)
        user, repos, events = await asyncio.gather(gh.get_user(login), gh.get_repos(login), gh.get_events(login))
        return live.developer_os(user, repos, events, n)
    return await _render(f)


@app.get("/card/achievements")
async def card_achievements(username: str | None = None, n: int = 20):
    async def f():
        login = _user(username)
        user, repos, stats, cal = await asyncio.gather(
            gh.get_user(login), gh.get_repos(login), gh.get_stats(login), gh.get_calendar(login))
        return eng.achievements(user, repos, stats, cal, n)
    return await _render(f)


@app.get("/card/collaborate")
async def card_collaborate(username: str | None = None, n: int = 21):
    async def f():
        return prof.collaborate(await gh.get_user(_user(username)), n)
    return await _render(f)


@app.get("/card/button")
async def card_button(label: str = Query(..., max_length=30), icon: str = "", primary: bool = False):
    return await _render(lambda: asyncio.sleep(0, prof.button(label, icon, primary)))


# ----------------------------------------------------------- redirects

@app.get("/go/project/{index}")
async def go_project(index: int, username: str | None = None):
    """Clickable link for /card/project/{index}; always points at the live pick."""
    login = _user(username)
    try:
        top = gh.featured((await gh.get_repos(login))["repos"], 4)
        if 0 <= index < len(top):
            return RedirectResponse(top[index]["url"], status_code=302)
    except Exception:
        pass
    return RedirectResponse(f"https://github.com/{login}?tab=repositories", status_code=302)


# ---------------------------------------------------------------- JSON

def _json(data, status=200):
    return JSONResponse(data, status_code=status, headers={"Cache-Control": CACHE})


@app.get("/api/profile")
async def api_profile(username: str | None = None):
    return _json({"status": "success", "profile": await gh.get_user(_user(username))})


@app.get("/api/projects")
async def api_projects(username: str | None = None):
    repos = await gh.get_repos(_user(username))
    return _json({"status": "success", "total": len(repos["repos"]), "projects": repos["repos"]})


@app.get("/api/github/stats")
async def api_stats(username: str | None = None):
    login = _user(username)
    user, repos, stats, cal = await asyncio.gather(
        gh.get_user(login), gh.get_repos(login), gh.get_stats(login), gh.get_calendar(login))
    return _json({
        "status": "success",
        "repositories": user["public_repos"], "followers": user["followers"], "following": user["following"],
        "stars": repos["total_stars"], "forks": repos["total_forks"], "languages": dict(repos["languages"]),
        "commits": stats["commits"], "pull_requests": stats["prs"], "issues": stats["issues"],
        "top_repositories": [{"name": n, "commits": c} for n, c in stats["top_repos"]],
        "contributions_last_year": cal["total"],
    })


@app.get("/api/activity")
async def api_activity(username: str | None = None):
    return _json({"status": "success", "events": await gh.get_events(_user(username))})


@app.get("/api/experience")
async def api_experience():
    return _json({"status": "success", "timeline": [
        {"year": y, "title": t, "details": f"{a} {b}"} for y, t, a, b in config.TIMELINE]})


@app.get("/api/tech-stack")
async def api_tech(username: str | None = None):
    tech = await gh.get_tech(_user(username))
    return _json({"status": "success", "stack": {
        k: [{"name": n, "repos": gh.tech_count(tech, n)} for n, _, _ in v] for k, v in config.TECH_STACK.items()}})


@app.get("/health")
async def health():
    return {"status": "ok", "username": config.GITHUB_USERNAME, "token": bool(config.GITHUB_TOKEN)}


# ------------------------------------------------------------- preview

PREVIEW_CARDS = ["hero", "city", "about", "tech-stack", "smart-contracts", "what-i-build", "project/0", "project/1", "project/2", "project/3",
                 "architecture", "timeline", "analytics", "activity", "playground", "backend", "cloud", "workflow",
                 "problem-solution", "developer-os", "achievements", "collaborate"]


@app.get("/", response_class=HTMLResponse)
async def preview(username: str | None = None):
    q = f"?username={esc(username)}" if username else ""
    imgs = "\n".join(
        f'<img src="/card/{c}{q}" style="width:{"49.3%" if c.startswith("project") else "100%"}" alt="{c}">'
        for c in PREVIEW_CARDS)
    return f"""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Profile API preview</title><style>body{{background:#0d1117;margin:0;padding:24px 16px;color:#e6edf3;font-family:system-ui}}
main{{max-width:850px;margin:auto;display:flex;flex-wrap:wrap;gap:12px 1.4%}}img{{display:block;height:auto}}</style></head>
<body><main>{imgs}</main></body></html>"""
