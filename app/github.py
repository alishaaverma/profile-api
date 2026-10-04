"""Live GitHub data with a small in-memory TTL cache.

Each data group (user, repos, events, stats, calendar) is fetched and cached
separately so a card only triggers the requests it actually needs. With a
GITHUB_TOKEN the GraphQL API is used for stats/calendar; without one we fall
back to the REST search API and the public contributions page.
"""

from __future__ import annotations

import asyncio
import re
import time
from collections import Counter
from datetime import datetime, timezone

import httpx

from . import config

API = "https://api.github.com"
TTL = min(config.CACHE_SECONDS, 600)

LANG_COLORS = {
    "Python": "#3572A5", "JavaScript": "#f1e05a", "TypeScript": "#3178c6",
    "Java": "#b07219", "HTML": "#e34c26", "CSS": "#563d7c", "Go": "#00ADD8",
    "Kotlin": "#A97BFF", "Dart": "#00B4AB", "C++": "#f34b7d", "C": "#555555",
    "PHP": "#4F5D95", "Shell": "#89e051", "Jupyter Notebook": "#DA5B0B",
    "Vue": "#41b883", "Rust": "#dea584", "Ruby": "#701516", "C#": "#178600",
    "SCSS": "#c6538c", "Dockerfile": "#384d54",
}

_cache: dict[str, tuple[float, object]] = {}
_locks: dict[str, asyncio.Lock] = {}
_client: httpx.AsyncClient | None = None
_client_loop: asyncio.AbstractEventLoop | None = None


class GitHubError(Exception):
    pass


def lang_color(name: str | None) -> str:
    return LANG_COLORS.get(name or "", "#8b949e")


def _http() -> httpx.AsyncClient:
    # Serverless runtimes may hand us a fresh event loop per invocation.
    global _client, _client_loop
    loop = asyncio.get_running_loop()
    if _client is None or _client.is_closed or _client_loop is not loop:
        _client_loop = loop
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "profile-api",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if config.GITHUB_TOKEN:
            headers["Authorization"] = f"Bearer {config.GITHUB_TOKEN}"
        _client = httpx.AsyncClient(headers=headers, timeout=10.0, follow_redirects=True)
    return _client


async def _cached(key: str, loader):
    now = time.time()
    hit = _cache.get(key)
    if hit and now - hit[0] < TTL:
        return hit[1]
    lock = _locks.setdefault(f"{key}:{id(asyncio.get_running_loop())}", asyncio.Lock())
    async with lock:
        hit = _cache.get(key)
        if hit and time.time() - hit[0] < TTL:
            return hit[1]
        try:
            value = await loader()
        except Exception:
            if hit:  # serve stale data rather than a broken card
                return hit[1]
            raise
        _cache[key] = (time.time(), value)
        return value


async def _get(path: str, **params):
    r = await _http().get(f"{API}{path}", params=params or None)
    if r.status_code != 200:
        raise GitHubError(f"GET {path} -> {r.status_code}: {r.text[:200]}")
    return r.json()


async def _graphql(query: str, **variables):
    r = await _http().post(f"{API}/graphql", json={"query": query, "variables": variables})
    data = r.json()
    if r.status_code != 200 or data.get("errors"):
        raise GitHubError(f"GraphQL error: {str(data)[:300]}")
    return data["data"]


# --------------------------------------------------------------------- user

async def get_user(login: str) -> dict:
    async def load():
        t0 = time.perf_counter()
        u = await _get(f"/users/{login}")
        latency = int((time.perf_counter() - t0) * 1000)
        return {
            "login": u["login"],
            "name": config.PROFILE["name"] or u.get("name") or u["login"],
            "bio": u.get("bio") or "",
            "location": u.get("location") or "",
            "avatar": u.get("avatar_url"),
            "url": u.get("html_url"),
            "followers": u.get("followers", 0),
            "following": u.get("following", 0),
            "public_repos": u.get("public_repos", 0),
            "created_at": u.get("created_at"),
            "latency_ms": latency,
        }

    return await _cached(f"user:{login}", load)


# -------------------------------------------------------------------- repos

async def get_repos(login: str) -> dict:
    async def load():
        raw = await _get(f"/users/{login}/repos", per_page=100, sort="pushed", type="owner")
        repos = [
            {
                "name": r["name"],
                "description": r.get("description") or "",
                "stars": r.get("stargazers_count", 0),
                "forks": r.get("forks_count", 0),
                "language": r.get("language"),
                "color": lang_color(r.get("language")),
                "topics": r.get("topics") or [],
                "url": r["html_url"],
                "homepage": r.get("homepage") or "",
                "pushed_at": r.get("pushed_at"),
            }
            for r in raw
            if not r.get("fork") and not r.get("archived") and r["name"].lower() != login.lower()
        ]
        langs = Counter(r["language"] for r in repos if r["language"])
        return {
            "repos": repos,
            "total_stars": sum(r["stars"] for r in repos),
            "total_forks": sum(r["forks"] for r in repos),
            "languages": langs.most_common(),
        }

    return await _cached(f"repos:{login}", load)


def featured(repos: list[dict], count: int = 4) -> list[dict]:
    if config.FEATURED_REPOS:
        by_name = {r["name"].lower(): r for r in repos}
        picked = [by_name[n.lower()] for n in config.FEATURED_REPOS if n.lower() in by_name]
        if picked:
            return picked[:count]
    # Prefer repos with stars, a description and recent activity.
    ranked = sorted(
        repos,
        key=lambda r: (r["stars"] + r["forks"], bool(r["description"]), r["pushed_at"] or ""),
        reverse=True,
    )
    return ranked[:count]


# ------------------------------------------------------------------- events

def _describe(e: dict) -> tuple[str, str, str]:
    """-> (kind, text, short ref)"""
    t, repo, p = e["type"], e["repo"]["name"].split("/")[-1], e.get("payload") or {}
    if t == "PushEvent":
        n = p.get("size") or len(p.get("commits") or []) or 0
        what = f"{n} commit{'s' if n != 1 else ''}" if n else "commits"
        return "push", f"Pushed {what} to {repo}", (p.get("head") or "")[:7]
    if t == "PullRequestEvent":
        pr = p.get("pull_request") or {}
        action = "Merged" if pr.get("merged") else (p.get("action") or "opened").capitalize()
        return "pr", f"{action} PR #{pr.get('number', p.get('number', ''))} in {repo}", f"#{pr.get('number', '')}"
    if t == "IssuesEvent":
        i = p.get("issue") or {}
        return "issue", f"{(p.get('action') or 'opened').capitalize()} issue #{i.get('number', '')} in {repo}", f"#{i.get('number', '')}"
    if t == "IssueCommentEvent":
        i = p.get("issue") or {}
        return "comment", f"Commented on #{i.get('number', '')} in {repo}", f"#{i.get('number', '')}"
    if t == "CreateEvent":
        kind = p.get("ref_type") or "repository"
        if kind == "repository":
            return "create", f"Created repository {repo}", "new"
        return "create", f"Created {kind} {p.get('ref') or ''} in {repo}", kind
    if t == "DeleteEvent":
        return "delete", f"Deleted {p.get('ref_type', '')} {p.get('ref', '')} in {repo}", "del"
    if t == "WatchEvent":
        return "star", f"Starred {e['repo']['name']}", "★"
    if t == "ForkEvent":
        return "fork", f"Forked {e['repo']['name']}", "fork"
    if t == "ReleaseEvent":
        rel = p.get("release") or {}
        return "release", f"Released {rel.get('tag_name', '')} of {repo}", rel.get("tag_name", "")
    if t == "PublicEvent":
        return "create", f"Made {repo} public", "public"
    if t == "PullRequestReviewEvent":
        return "pr", f"Reviewed a PR in {repo}", "review"
    return "other", f"{t.replace('Event', '')} in {repo}", ""


async def get_events(login: str) -> list[dict]:
    async def load():
        raw = await _get(f"/users/{login}/events/public", per_page=30)
        out = []
        for e in raw:
            kind, text, ref = _describe(e)
            out.append({"kind": kind, "text": text, "ref": ref, "at": e["created_at"],
                        "repo": e["repo"]["name"]})
        return out

    return await _cached(f"events:{login}", load)


# -------------------------------------------------------------------- stats

STATS_QUERY = """
query($login: String!) {
  user(login: $login) {
    pullRequests { totalCount }
    issues { totalCount }
    contributionsCollection {
      totalCommitContributions
      restrictedContributionsCount
      commitContributionsByRepository(maxRepositories: 5) {
        repository { name }
        contributions { totalCount }
      }
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount contributionLevel } }
      }
    }
  }
}
"""

LEVELS = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}


async def _graphql_bundle(login: str) -> dict:
    async def load():
        return (await _graphql(STATS_QUERY, login=login))["user"]

    return await _cached(f"gql:{login}", load)


async def get_stats(login: str) -> dict:
    """PRs, issues, commits and commits per repository."""

    async def load():
        if config.GITHUB_TOKEN:
            u = await _graphql_bundle(login)
            cc = u["contributionsCollection"]
            return {
                "prs": u["pullRequests"]["totalCount"],
                "issues": u["issues"]["totalCount"],
                "commits": cc["totalCommitContributions"] + cc["restrictedContributionsCount"],
                "top_repos": [
                    (c["repository"]["name"], c["contributions"]["totalCount"])
                    for c in cc["commitContributionsByRepository"]
                ],
            }

        async def count(q):
            try:
                return await _get("/search/issues", q=q, per_page=1)
            except GitHubError:
                return {"total_count": 0}

        prs, issues, commits = await asyncio.gather(
            count(f"author:{login} type:pr"),
            count(f"author:{login} type:issue"),
            _get("/search/commits", q=f"author:{login}", per_page=100, sort="author-date"),
        )
        per_repo = Counter(i["repository"]["name"] for i in commits.get("items", []))
        return {
            "prs": prs["total_count"],
            "issues": issues["total_count"],
            "commits": commits.get("total_count", 0),
            "top_repos": per_repo.most_common(5),
        }

    return await _cached(f"stats:{login}", load)


_DAY_RE = re.compile(
    r'data-date="(?P<date>[\d-]+)"\s+id="contribution-day-component-(?P<dow>\d)-(?P<week>\d+)"\s+data-level="(?P<level>\d)"'
)
_TIP_RE = re.compile(r'for="contribution-day-component-(\d)-(\d+)"[^>]*>(No|[\d,]+) contribution')
_TOTAL_RE = re.compile(r"([\d,]+)\s+contributions?\s+in\s+the\s+last\s+year", re.S)


async def get_calendar(login: str) -> dict:
    """{'total': int, 'weeks': [[{'date','count','level'} x7] ...]}"""

    async def load():
        if config.GITHUB_TOKEN:
            cal = (await _graphql_bundle(login))["contributionsCollection"]["contributionCalendar"]
            weeks = [
                [{"date": d["date"], "count": d["contributionCount"], "level": LEVELS.get(d["contributionLevel"], 0)}
                 for d in w["contributionDays"]]
                for w in cal["weeks"]
            ]
            return {"total": cal["totalContributions"], "weeks": weeks}

        r = await _http().get(f"https://github.com/users/{login}/contributions")
        if r.status_code != 200:
            raise GitHubError(f"contributions page -> {r.status_code}")
        html = r.text
        counts = {}
        for dow, week, n in _TIP_RE.findall(html):
            counts[(int(week), int(dow))] = 0 if n == "No" else int(n.replace(",", ""))
        grid: dict[int, list] = {}
        for m in _DAY_RE.finditer(html):
            wk, dow = int(m["week"]), int(m["dow"])
            grid.setdefault(wk, []).append(
                {"date": m["date"], "count": counts.get((wk, dow), 0), "level": int(m["level"]), "dow": dow}
            )
        weeks = [sorted(grid[k], key=lambda d: d["dow"]) for k in sorted(grid)]
        total_m = _TOTAL_RE.search(html)
        total = int(total_m.group(1).replace(",", "")) if total_m else sum(d["count"] for w in weeks for d in w)
        return {"total": total, "weeks": weeks}

    return await _cached(f"calendar:{login}", load)


# ------------------------------------------------------------------ helpers

def time_ago(iso: str | None) -> str:
    if not iso:
        return ""
    dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    secs = int((datetime.now(timezone.utc) - dt).total_seconds())
    for unit, size in (("year", 31536000), ("month", 2592000), ("week", 604800),
                       ("day", 86400), ("hour", 3600), ("minute", 60)):
        if secs >= size:
            n = secs // size
            return f"{n} {unit}{'s' if n > 1 else ''} ago"
    return "just now"
