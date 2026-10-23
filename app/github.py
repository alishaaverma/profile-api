"""Live GitHub data with a small in-memory TTL cache.

Each data group (user, repos, events, stats, calendar, tech) is fetched and cached
separately so a card only triggers the requests it actually needs. With a
GITHUB_TOKEN the GraphQL API is used for stats/calendar; without one we fall
back to the REST search API and the public contributions page.
"""

from __future__ import annotations

import asyncio
import json
import re
import time
from collections import Counter
from datetime import datetime, timedelta, timezone

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
    "SCSS": "#c6538c", "Dockerfile": "#384d54", "Solidity": "#AA6746",
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
            "hireable": u.get("hireable"),       # the "Available for hire" checkbox; None if unset
            "email": u.get("email") or "",       # public email, if shown on the profile
            "blog": u.get("blog") or "",         # the Website field
            "twitter": u.get("twitter_username") or "",
            "latency_ms": latency,
        }

    return await _cached(f"user:{login}", load)


async def get_socials(login: str) -> list[dict]:
    """Social accounts on my GitHub profile: [{'provider': 'linkedin', 'url': ...}]."""

    async def load():
        try:
            return [{"provider": s.get("provider", ""), "url": s.get("url", "")}
                    for s in await _get(f"/users/{login}/social_accounts")]
        except GitHubError:
            return []

    return await _cached(f"socials:{login}", load)


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
                "created_at": r.get("created_at"),
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


async def get_now_building(login: str, repos: dict) -> dict | None:
    """The most recently pushed repo and its commits from the last 30 days:
    {'repo': {...}, 'commits': [{'sha','message','date'}], 'latest': {...} | None}"""

    async def load():
        if not repos["repos"]:
            return None
        repo = max(repos["repos"], key=lambda r: r["pushed_at"] or "")
        path = f"/repos/{login}/{repo['name']}/commits"
        since = (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ")

        def parse(raw):
            return [{"sha": c["sha"][:7], "message": (c["commit"]["message"] or "").splitlines()[0],
                     "date": c["commit"]["author"]["date"]} for c in raw]

        try:
            commits = parse(await _get(path, since=since, per_page=100))
            latest = commits[0] if commits else (parse(await _get(path, per_page=1)) or [None])[0]
        except GitHubError:  # e.g. an empty repository
            commits, latest = [], None
        return {"repo": repo, "commits": commits, "latest": latest}

    return await _cached(f"building:{login}", load)


async def get_commit_log(login: str) -> list[dict]:
    """My 100 most recent commits across public repos, newest first:
    [{'sha', 'date', 'repo', 'message'}]; 'date' keeps the author's own UTC offset, so its hour is local time."""

    async def load():
        try:
            raw = await _get("/search/commits", q=f"author:{login}", sort="author-date", order="desc", per_page=100)
        except GitHubError:
            return []
        return [{"sha": i["sha"], "date": i["commit"]["author"]["date"], "repo": i["repository"]["name"],
                 "message": (i["commit"]["message"] or "").partition("\n")[0]}
                for i in raw.get("items", [])]

    return await _cached(f"commitlog:{login}", load)


def featured(repos: list[dict], count: int = 4) -> list[dict]:
    if config.FEATURED_REPOS:
        by_name = {r["name"].lower(): r for r in repos}
        picked = [by_name[n.lower()] for n in config.FEATURED_REPOS if n.lower() in by_name]
        if picked:
            return picked[:count]
    if config.FEATURED_SORT == "newest":
        return sorted(repos, key=lambda r: r["created_at"] or "", reverse=True)[:count]
    if config.FEATURED_SORT == "updated":
        return sorted(repos, key=lambda r: r["pushed_at"] or "", reverse=True)[:count]
    # "popular": prefer repos with stars, a description and recent activity.
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


# --------------------------------------------------------------------- tech

TECH_QUERY = """
query($login: String!) {
  user(login: $login) {
    repositories(first: 100, ownerAffiliations: OWNER, isFork: false, orderBy: {field: PUSHED_AT, direction: DESC}) {
      nodes {
        name
        description
        isArchived
        repositoryTopics(first: 20) { nodes { topic { name } } }
        languages(first: 10) { edges { size node { name } } }
        dockerfile: object(expression: "HEAD:Dockerfile") { __typename }
        workflows: object(expression: "HEAD:.github/workflows") { __typename }
        packageJson: object(expression: "HEAD:package.json") { ... on Blob { text } }
        requirements: object(expression: "HEAD:requirements.txt") { ... on Blob { text } }
      }
    }
  }
}
"""

_WORD_RE = re.compile(r"[a-z0-9@][a-z0-9+#./_-]*")


def _words(s: str | None) -> set[str]:
    return {w.strip("./-") for w in _WORD_RE.findall((s or "").lower())} - {""}


def _npm_deps(blob: dict | None) -> set[str]:
    try:
        pkg = json.loads((blob or {}).get("text") or "{}")
    except ValueError:
        return set()
    if not isinstance(pkg, dict):
        return set()
    return {k.lower() for key in ("dependencies", "devDependencies") for k in (pkg.get(key) or {})}


def _pip_deps(blob: dict | None) -> set[str]:
    out = set()
    for line in ((blob or {}).get("text") or "").splitlines():
        name = re.split(r"[\s<>=!~\[;@#]", line.strip(), maxsplit=1)[0].lower().replace("_", "-")
        if name and not name.startswith("-"):
            out.add(name)
    return out


async def get_tech(login: str) -> dict:
    """{'repos': {name: {tokens}}, 'languages': Counter(language -> repo count),
        'bytes': Counter(language -> bytes of code), 'exact': whether 'bytes' is real bytes}

    Tokens are what a repo shows about the tech it uses; match them against
    config.TECH_ALIASES with tech_count(). With a GITHUB_TOKEN, one GraphQL call
    also reads every repo's languages, package.json, requirements.txt, Dockerfile
    and workflows; without one, only the primary language, topics and text are used.
    """

    async def load():
        repos, langs, sizes = {}, Counter(), Counter()
        if config.GITHUB_TOKEN:
            nodes = (await _graphql(TECH_QUERY, login=login))["user"]["repositories"]["nodes"]
            for r in nodes:
                if r["isArchived"] or r["name"].lower() == login.lower():
                    continue
                names = [e["node"]["name"] for e in r["languages"]["edges"]]
                sizes.update({e["node"]["name"]: e["size"] for e in r["languages"]["edges"]})
                tokens = {n.lower() for n in names} | {t["topic"]["name"] for t in r["repositoryTopics"]["nodes"]}
                tokens |= _words(r["name"].replace("-", " ").replace("_", " ")) | _words(r["description"])
                tokens |= _npm_deps(r["packageJson"]) | _pip_deps(r["requirements"])
                if r["dockerfile"]:
                    tokens.add("docker")
                if r["workflows"]:
                    tokens.add("github-actions")
                repos[r["name"]] = tokens
                langs.update(names)
        else:
            for r in (await get_repos(login))["repos"]:
                tokens = set(r["topics"]) | _words(r["name"].replace("-", " ").replace("_", " ")) | _words(r["description"])
                if r["language"]:
                    tokens.add(r["language"].lower())
                    langs[r["language"]] += 1
                repos[r["name"]] = tokens
            sizes = langs.copy()  # no token: weigh each language by its repos instead
        return {"repos": repos, "languages": langs, "bytes": sizes, "exact": bool(config.GITHUB_TOKEN)}

    return await _cached(f"tech:{login}", load)


def _matches(key: str, tokens: set[str]) -> bool:
    if key.endswith("*"):
        return any(t.startswith(key[:-1]) for t in tokens)
    return key in tokens


def tech_repo_names(tech: dict, *names: str) -> list[str]:
    """Repos that use any of these TECH_STACK items (or other alias-less names)."""
    keys = [k for name in names for k in config.TECH_ALIASES.get(name, [name.lower()])]
    return [repo for repo, tokens in tech["repos"].items() if any(_matches(k, tokens) for k in keys)]


def tech_count(tech: dict, *names: str) -> int:
    return len(tech_repo_names(tech, *names))


def tech_repos(tech: dict, marker: str) -> int:
    """How many repos carry a raw token, e.g. 'github-actions'."""
    return sum(1 for tokens in tech["repos"].values() if marker in tokens)


# ---------------------------------------------------------------- festivals

# Google's public "Holidays in India" calendar: no key needed, and it already
# knows the dates of festivals that move every year (Diwali, Holi, Eid...).
HOLIDAY_ICS = ("https://calendar.google.com/calendar/ical/"
               "en.indian%23holiday%40group.v.calendar.google.com/public/basic.ics")

# calendar event name -> (festival theme, days before, days after); earlier rows win a clash
FESTIVAL_EVENTS = [
    (re.compile(r"diwali|deepavali", re.I), "diwali", 2, 2),  # Dhanteras to Bhai Dooj
    (re.compile(r"govardhan|bhai du", re.I), "diwali", 0, 0),
    (re.compile(r"\bholi\b|holika", re.I), "holi", 0, 0),
    (re.compile(r"ramzan id|bakrid|\beid\b|id-ul-fitr|id-ul-zuha", re.I), "eid", 0, 1),
    (re.compile(r"christmas", re.I), "christmas", 0, 0),
    (re.compile(r"dussehra|vijaya ?dashami", re.I), "dussehra", 0, 0),
    (re.compile(r"sharad navratri", re.I), "navratri", 0, 8),  # nine nights
    (re.compile(r"durga puja|maha saptami|maha ashtami|maha navami", re.I), "navratri", 0, 0),
    (re.compile(r"ganesh chaturthi", re.I), "ganesh", 0, 1),
    (re.compile(r"janmashtami", re.I), "janmashtami", 0, 0),
    (re.compile(r"raksha bandhan", re.I), "rakhi", 0, 0),
    (re.compile(r"\bonam\b", re.I), "onam", 0, 0),
    (re.compile(r"guru nanak", re.I), "gurpurab", 0, 0),
    (re.compile(r"chhat", re.I), "chhath", 0, 1),
    (re.compile(r"makar sankranti|pongal|lohri", re.I), "sankranti", 1, 1),
    (re.compile(r"new year's day", re.I), "newyear", 1, 0),
    (re.compile(r"republic day", re.I), "republic", 0, 0),
    (re.compile(r"independence day", re.I), "independence", 0, 0),
]


async def get_festival_dates() -> dict[str, str]:
    """{'YYYY-MM-DD': festival theme} from the live holiday calendar; {} if it can't be read."""

    async def load():
        try:
            # a separate client: the GitHub token must not go to Google
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                r = await client.get(HOLIDAY_ICS)
            r.raise_for_status()
        except httpx.HTTPError:
            return {}
        text = re.sub(r"\r?\n[ \t]", "", r.text)  # unfold long lines
        best: dict[str, tuple[int, str]] = {}
        for event in text.split("BEGIN:VEVENT")[1:]:
            start = re.search(r"^DTSTART[^:\n]*:(\d{8})", event, re.M)
            summary = re.search(r"^SUMMARY[^:\n]*:(.*)$", event, re.M)
            if not start or not summary:
                continue
            for rank, (pattern, theme, before, after) in enumerate(FESTIVAL_EVENTS):
                if pattern.search(summary.group(1)):
                    day = datetime.strptime(start.group(1), "%Y%m%d")
                    for offset in range(-before, after + 1):
                        key = (day + timedelta(days=offset)).strftime("%Y-%m-%d")
                        if key not in best or rank < best[key][0]:
                            best[key] = (rank, theme)
                    break
        return {k: theme for k, (_, theme) in best.items()}

    return await _cached("festivals", load)


# --------------------------------------------------------------- feed Byte

async def get_byte_feeds(login: str) -> dict | None:
    """Visitors feed the city's pet by opening a "Feed Byte" issue on my profile repo:
    {'count', 'last_by', 'last_at'}; None if the search fails."""

    async def load():
        try:
            raw = await _get("/search/issues", q=f'repo:{login}/{login} is:issue in:title "Feed Byte"',
                             sort="created", order="desc", per_page=1)
        except GitHubError:
            return None
        items = raw.get("items") or []
        return {"count": raw.get("total_count", 0),
                "last_by": items[0]["user"]["login"] if items else "",
                "last_at": items[0]["created_at"] if items else ""}

    return await _cached(f"feeds:{login}", load)


# ------------------------------------------------------- community: votes, AMA

async def get_ideas(login: str) -> list[dict]:
    """Open issues labelled "idea" on my profile repo, most 👍 first:
    [{'title', 'votes', 'url'}]. I post the ideas; visitors vote with a 👍 reaction."""

    async def load():
        try:
            raw = await _get(f"/repos/{login}/{login}/issues", labels="idea", state="open", per_page=30)
        except GitHubError:
            return []
        ideas = [{"title": i["title"], "votes": (i.get("reactions") or {}).get("+1", 0), "url": i["html_url"]}
                 for i in raw if "pull_request" not in i]
        return sorted(ideas, key=lambda i: -i["votes"])

    return await _cached(f"ideas:{login}", load)


async def get_ama(login: str, limit: int = 2) -> list[dict]:
    """The newest "AMA" issues on my profile repo that I have answered in a comment:
    [{'question', 'answer', 'asker', 'url'}]."""

    async def load():
        try:
            raw = await _get("/search/issues", q=f'repo:{login}/{login} is:issue in:title "AMA"',
                             sort="created", order="desc", per_page=15)
        except GitHubError:
            return []
        out = []
        for item in raw.get("items", []):
            if not item.get("comments") or item["user"]["login"].lower() == login.lower():
                continue
            try:
                comments = await _get(f"/repos/{login}/{login}/issues/{item['number']}/comments", per_page=30)
            except GitHubError:
                continue
            answer = next((c["body"] for c in comments if c["user"]["login"].lower() == login.lower()), "")
            if answer:
                question = re.sub(r"^\s*AMA\s*[:\-—]?\s*", "", item["title"], flags=re.I) or (item.get("body") or "")
                out.append({"question": question.strip(), "answer": " ".join(answer.split()),
                            "asker": item["user"]["login"], "url": item["html_url"]})
            if len(out) == limit:
                break
        return out

    return await _cached(f"ama:{login}", load)


# ---------------------------------------------------------- today I learned

_TIL_LINE = re.compile(r"^\s*[-*]\s+(?:\*\*)?(\d{4}-\d{2}-\d{2})?(?:\*\*)?\s*[:—–-]?\s*(.+?)\s*$")


async def get_til(login: str, limit: int = 3) -> list[dict]:
    """Newest entries of TIL.md in my config.TIL_REPO repo: [{'date', 'text'}].
    One bullet per thing learned, newest at the top, e.g. "- 2026-10-23: Solidity events are cheap logs"."""

    async def load():
        url = f"https://raw.githubusercontent.com/{login}/{config.TIL_REPO}/HEAD/TIL.md"
        try:
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                r = await client.get(url)
        except httpx.HTTPError:
            return []
        if r.status_code != 200:
            return []
        out = []
        for line in r.text.splitlines():
            m = _TIL_LINE.match(line)
            if m:
                out.append({"date": m.group(1) or "", "text": re.sub(r"[`*_]", "", m.group(2))})
            if len(out) == limit:
                break
        return out

    return await _cached(f"til:{login}", load)


# ------------------------------------------------------------------ weather

# WMO weather code -> (kind drawn on the city, words)
WEATHER_CODES = [
    ((0,), "clear", "clear sky"), ((1,), "clear", "mostly clear"), ((2,), "clouds", "partly cloudy"),
    ((3,), "clouds", "overcast"), ((45, 48), "fog", "foggy"), (tuple(range(51, 58)), "rain", "drizzle"),
    (tuple(range(61, 68)), "rain", "rain"), (tuple(range(71, 78)), "snow", "snow"),
    ((80, 81, 82), "rain", "showers"), ((85, 86), "snow", "snow showers"), ((95, 96, 99), "storm", "thunderstorm"),
]
AQI_LEVELS = [(50, "good"), (100, "moderate"), (150, "unhealthy for some"), (200, "unhealthy"),
              (300, "very unhealthy"), (10_000, "hazardous")]


async def get_weather() -> dict | None:
    """Current weather and air quality at config.WEATHER_LAT/LON from Open-Meteo (free, no key):
    {'temp', 'kind', 'words', 'aqi', 'aqi_label', 'sunrise', 'sunset'} (times as "HH:MM" IST);
    None if it can't be read."""

    async def load():
        where = {"latitude": config.WEATHER_LAT, "longitude": config.WEATHER_LON, "timezone": "Asia/Kolkata"}
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                wx, air = await asyncio.gather(
                    client.get("https://api.open-meteo.com/v1/forecast",
                               params={**where, "current": "temperature_2m,weather_code,precipitation",
                                       "daily": "sunrise,sunset", "forecast_days": 1}),
                    client.get("https://air-quality-api.open-meteo.com/v1/air-quality",
                               params={**where, "current": "us_aqi"}))
            now, aq, daily = wx.json()["current"], air.json().get("current", {}), wx.json().get("daily", {})
        except (httpx.HTTPError, ValueError, KeyError):
            return None
        code = now.get("weather_code", 0)
        kind, words = next(((k, w) for codes, k, w in WEATHER_CODES if code in codes), ("clouds", "cloudy"))
        # the model reports a trace of "drizzle" under thin cloud; only draw rain when real rain falls
        if kind == "rain" and (now.get("precipitation") or 0) < 0.5:
            kind, words = "clouds", "cloudy"
        aqi = aq.get("us_aqi")
        label = next(name for limit, name in AQI_LEVELS if aqi is None or aqi <= limit) if aqi is not None else ""
        if kind in ("clear", "clouds") and aqi and aqi > 150:
            kind, words = "smog", "smoggy"
        sun = {k: (daily.get(k) or [""])[0][11:16] for k in ("sunrise", "sunset")}
        return {"temp": round(now.get("temperature_2m", 0)), "kind": kind, "words": words, "aqi": aqi, "aqi_label": label,
                **sun}

    return await _cached("weather", load)


async def get_profile_views(login: str, previous: str) -> dict:
    """Profile views from the komarev.com counter that the profile README loads: {'views': int | None}.
    komarev only counts requests from GitHub's image proxy (camo), so reading it from here is free.
    `previous` is the API URL of the views.json published last run, kept when the counter is down."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            r = await client.get(previous, headers={"Accept": "application/vnd.github.raw"})
            state = r.json() if r.status_code == 200 else {}
        except (httpx.HTTPError, ValueError):
            state = {}
        try:
            r = await client.get("https://komarev.com/ghpvc/", params={"username": login, "abbreviated": "false"})
            counts = re.findall(r">([\d,]+)</text>", r.text) if r.status_code == 200 else []
        except httpx.HTTPError:
            counts = []
    if not counts:
        return {"views": state.get("views")}
    return {"views": max(int(counts[-1].replace(",", "")), state.get("views") or 0)}


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
