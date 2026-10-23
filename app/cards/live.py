"""Cards driven by live GitHub data."""

from __future__ import annotations

import json
import math
import random
import re
from collections import Counter
from datetime import datetime, timezone

from .. import config
from .. import github as gh
from ..github import featured, lang_color, time_ago
from .theme import (AMBER, BLUE, BORDER, CARD2, CYAN, ETH, FESTIVAL_CSS, FESTIVALS, GREEN, GROUND_FESTIVALS, LOW_SUN,
                    MUTED, ORANGE, SKIES, TEXT, WEATHER_CSS, aqi_color, celestial, compact, d, dot, esc,
                    festival_ground, festival_sky, festival_today, frame, heading, panel, weather_sky,
                    phase_label, sky, sky_phase, stars, svg, synced, trunc, wrap)

STAR = "M8 .25a.75.75 0 0 1 .673.418l1.882 3.815 4.21.612a.75.75 0 0 1 .416 1.279l-3.046 2.97.719 4.192a.75.75 0 0 1-1.088.791L8 12.347l-3.766 1.98a.75.75 0 0 1-1.088-.79l.72-4.194L.818 6.374a.75.75 0 0 1 .416-1.28l4.21-.611L7.327.668A.75.75 0 0 1 8 .25Z"
FORK = "M5 5.372v.878c0 .414.336.75.75.75h4.5a.75.75 0 0 0 .75-.75v-.878a2.25 2.25 0 1 1 1.5 0v.878a2.25 2.25 0 0 1-2.25 2.25h-1.5v2.128a2.251 2.251 0 1 1-1.5 0V8.5h-1.5A2.25 2.25 0 0 1 3.5 6.25v-.878a2.25 2.25 0 1 1 1.5 0ZM5 3.25a.75.75 0 1 0-1.5 0 .75.75 0 0 0 1.5 0Zm6.75.75a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5Zm-3 8.75a.75.75 0 1 0-1.5 0 .75.75 0 0 0 1.5 0Z"


# ------------------------------------------------------------ projects

def _mock(x, y, w, h, accent, variant):
    """Small animated UI mock-up standing in for a project screenshot."""
    o = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="#0a0f17" stroke="{BORDER}"/>'
    o += "".join(f'<circle cx="{x + 10 + i * 9}" cy="{y + 9}" r="2.6" fill="{c}"/>'
                 for i, c in enumerate(("#ff5f56", "#ffbd2e", "#27c93f")))
    o += f'<rect x="{x + 40}" y="{y + 5}" width="{w - 80}" height="8" rx="4" fill="#161d29"/>'
    iy = y + 20
    ih = h - 26
    if variant == 0:  # dashboard with line chart
        o += f'<rect x="{x + 6}" y="{iy}" width="54" height="{ih}" rx="4" fill="#111823"/>'
        for i in range(5):
            o += f'<rect x="{x + 12}" y="{iy + 8 + i * 13}" width="{40 - (i % 2) * 10}" height="5" rx="2.5" fill="{accent if i == 0 else "#243042"}"/>'
        for i in range(3):
            cx = x + 68 + i * ((w - 76) / 3)
            o += (f'<rect x="{cx:.0f}" y="{iy}" width="{(w - 76) / 3 - 6:.0f}" height="26" rx="4" fill="#111823"/>'
                  f'<rect x="{cx + 6:.0f}" y="{iy + 8}" width="24" height="4" rx="2" fill="#2b3646"/>'
                  f'<rect x="{cx + 6:.0f}" y="{iy + 16}" width="36" height="5" rx="2" fill="{accent}" opacity=".8"/>')
        pts = [(0, .7), (.15, .5), (.3, .62), (.45, .3), (.6, .42), (.75, .2), (.9, .32), (1, .1)]
        cw, ch, cx0, cy0 = w - 76, ih - 34, x + 68, iy + 32
        path = "M" + " L".join(f"{cx0 + px * cw:.0f},{cy0 + py * ch:.0f}" for px, py in pts)
        o += (f'<rect x="{cx0}" y="{cy0 - 2}" width="{cw - 6}" height="{ch + 4}" rx="4" fill="#111823"/>'
              f'<path d="{path}" stroke="{accent}" stroke-width="2" fill="none" pathLength="1" '
              f'stroke-dasharray="1" stroke-dashoffset="1" class="draw" filter="url(#glow)"/>')
    elif variant == 1:  # bar chart
        n = 18
        bw = (w - 20) / n
        heights = [.3, .5, .4, .7, .55, .8, .45, .6, .9, .5, .65, .75, .4, .85, .6, .95, .7, .8]
        for i in range(n):
            bh = heights[i] * (ih - 10)
            o += (f'<rect x="{x + 10 + i * bw:.1f}" y="{iy + ih - 4 - bh:.1f}" width="{bw - 3:.1f}" height="{bh:.1f}" rx="1.5" '
                  f'fill="{GREEN if i % 3 else accent}" class="growy" {d(.2 + i * .04)}/>')
    elif variant == 2:  # admin table
        o += f'<rect x="{x + 6}" y="{iy}" width="48" height="{ih}" rx="4" fill="#111823"/>'
        for i in range(6):
            yy = iy + 4 + i * ((ih - 4) / 6)
            o += (f'<rect x="{x + 60}" y="{yy:.0f}" width="{w - 66}" height="{(ih - 4) / 6 - 3:.0f}" rx="3" '
                  f'fill="{"#1a2230" if i == 0 else "#111823"}" class="rise" {d(.2 + i * .08)}/>'
                  f'<rect x="{x + 66}" y="{yy + 4:.0f}" width="{30 + (i * 17) % 40}" height="4" rx="2" fill="{accent if i == 0 else "#2b3646"}"/>'
                  f'<rect x="{x + w - 50}" y="{yy + 4:.0f}" width="30" height="5" rx="2.5" fill="{GREEN if i % 2 else accent}" opacity=".7"/>')
    else:  # integrations hub
        cx, cy = x + w / 2, iy + ih / 2
        nodes = [(-.36, -.28), (-.36, .28), (.36, -.28), (.36, .28)]
        cols = [BLUE, accent, "#bc8cff", CYAN]
        for (nx, ny), c in zip(nodes, cols):
            px, py = cx + nx * w, cy + ny * ih * 1.4
            path = f"M{cx:.0f},{cy:.0f} L{px:.0f},{py:.0f}"
            o += (f'<path d="{path}" stroke="{c}" stroke-width="1.4" class="flow"/>'
                  f'<rect x="{px - 14:.0f}" y="{py - 10:.0f}" width="28" height="20" rx="5" fill="#111823" stroke="{c}"/>'
                  f'<circle r="2.5" fill="{c}"><animateMotion dur="1.8s" repeatCount="indefinite" path="{path}"/></circle>')
        o += f'<rect x="{cx - 22:.0f}" y="{cy - 16:.0f}" width="44" height="32" rx="7" fill="#1a1109" stroke="{accent}" filter="url(#glow)"/>'
    return o


def project_card(repo: dict | None, idx: int, login: str) -> str:
    W, H = 415, 262
    b = panel(.5, .5, W - 1, H - 1, 12) + f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="12" fill="url(#grid)"/>'
    if not repo:
        b += f'<text x="{W / 2}" y="{H / 2}" text-anchor="middle" class="muted" font-size="13">More projects coming soon…</text>'
        return svg(W, H, b, title="Project")
    accent = repo["color"] if repo["color"] != "#8b949e" else ORANGE
    b += f'<g class="fade">{_mock(12, 12, W - 24, 112, accent, idx % 4)}</g>'
    b += f'<text x="16" y="150" font-size="15" font-weight="700" class="rise" {d(.2)}>{esc(trunc(repo["name"].replace("_", " "), 40))}</text>'
    b += f'<text x="{W - 16}" y="150" text-anchor="end" font-size="13" fill="{ORANGE}" class="pulse">↗</text>'
    created = repo.get("created_at")
    if created and (datetime.now(timezone.utc) - datetime.fromisoformat(created.replace("Z", "+00:00"))).days < 30:
        b += (f'<g class="pop" {d(.5)}><rect x="{W - 66}" y="20" width="42" height="18" rx="9" fill="{GREEN}" filter="url(#glow)" class="glowpulse"/>'
              f'<text x="{W - 45}" y="33" text-anchor="middle" font-size="9.5" font-weight="800" fill="#04140a">NEW</text></g>')
    desc = repo["description"] or f"A {repo['language'] or 'software'} project by @{login}."
    for i, line in enumerate(wrap(desc, 60, 2)):
        b += f'<text x="16" y="{171 + i * 15}" font-size="11" class="muted rise" {d(.3)}>{esc(line)}</text>'
    chips = ([repo["language"]] if repo["language"] else []) + [t for t in repo["topics"] if t != (repo["language"] or "").lower()]
    x = 16
    for i, c in enumerate(chips[:4]):
        w = len(c) * 6 + 18
        if x + w > W - 16:
            break
        b += (f'<g class="pop" {d(.4 + i * .08)}><rect x="{x}" y="203" width="{w:.0f}" height="20" rx="5" fill="{CARD2}" stroke="{BORDER}"/>'
              f'<text x="{x + w / 2:.0f}" y="216.5" text-anchor="middle" font-size="10" fill="#c9d1d9">{esc(c)}</text></g>')
        x += w + 6
    b += (f'<g class="fade" {d(.6)}>'
          f'<path transform="translate(16,234) scale(.85)" d="{STAR}" fill="{AMBER}"/>'
          f'<text x="34" y="246" font-size="12" font-weight="700">{compact(repo["stars"])}</text>'
          f'<path transform="translate(70,234) scale(.85)" d="{FORK}" fill="{MUTED}"/>'
          f'<text x="87" y="246" font-size="12" font-weight="700">{compact(repo["forks"])}</text>'
          f'<circle cx="128" cy="242" r="5" fill="{repo["color"]}"/>'
          f'<text x="138" y="246" font-size="11" class="muted">{esc(repo["language"] or "—")}</text>'
          f'<text x="{W - 16}" y="246" text-anchor="end" font-size="10" class="dim mono">updated {esc(time_ago(repo["pushed_at"]))}</text></g>')
    css = "@keyframes draw{to{stroke-dashoffset:0}}.draw{animation:draw 2s .3s ease forwards}"
    return svg(W, H, b, css, title=repo["name"])


# ------------------------------------------------- timeline + open source

def journey(user: dict, repos: dict, limit: int = 5) -> list[tuple[str, str, str, str]]:
    """(year, title, line1, line2) per year, built from when each repo was created.
    Titles come from config.TIMELINE_TITLES when set for that year."""
    by_year: dict[str, list[dict]] = {}
    for r in repos["repos"]:
        if r.get("created_at"):
            by_year.setdefault(r["created_at"][:4], []).append(r)
    joined = (user.get("created_at") or "")[:4]
    items = []
    for year in sorted(set(by_year) | ({joined} if joined else set())):
        rs = by_year.get(year, [])
        langs = [lang for lang, _ in Counter(r["language"] for r in rs if r["language"]).most_common(2)]
        auto = "Joined GitHub" if year == joined else (f"{langs[0]} projects" if langs else "Building")
        title = config.TIMELINE_TITLES.get(year) or auto
        if rs:
            line1 = f"{len(rs)} repo{'s' if len(rs) != 1 else ''}" + (f" · {langs[0]}" if langs else "")
            line2 = trunc(max(rs, key=lambda r: r["created_at"])["name"].replace("_", " ").replace("-", " "), 17)
        else:
            line1, line2 = "Started my journey", ""
        items.append((year, title, line1, line2))
    # keep the year I joined, then the most recent ones
    return items if len(items) <= limit else items[:1] + items[-(limit - 1):]


def timeline_opensource(user: dict, repos: dict, stats: dict, calendar: dict, n: int = 9) -> str:
    W, H = 850, 262
    b = frame(W, H)
    b += heading(24, 20, n, "My Journey", "Built from my repositories, year by year.")
    items = journey(user, repos)
    x0, x1, ly = 72, 448, 120
    b += f'<rect x="{x0}" y="{ly - 1.5}" width="{x1 - x0}" height="3" rx="1.5" fill="#2a1a0c"/>'
    b += f'<rect x="{x0}" y="{ly - 1.5}" width="{x1 - x0}" height="3" rx="1.5" fill="url(#og)" class="grow" filter="url(#glow)"/>'
    step = (x1 - x0) / max(1, len(items) - 1)
    for i, (year, title, l1, l2) in enumerate(items):
        x = x0 + i * step
        b += (f'<g class="pop" {d(.4 + i * .25)}><circle cx="{x:.0f}" cy="{ly}" r="9" fill="{ORANGE}" opacity=".25"/>'
              f'<circle cx="{x:.0f}" cy="{ly}" r="5" fill="{AMBER}" filter="url(#glow)"/></g>')
        b += (f'<g class="rise" {d(.5 + i * .25)}>'
              f'<text x="{x:.0f}" y="{ly + 34}" text-anchor="middle" font-size="14" font-weight="800">{esc(year)}</text>'
              f'<text x="{x:.0f}" y="{ly + 52}" text-anchor="middle" font-size="10.2" font-weight="700" fill="{AMBER}">{esc(title)}</text>'
              f'<text x="{x:.0f}" y="{ly + 67}" text-anchor="middle" font-size="9.2" class="muted">{esc(l1)}</text>'
              f'<text x="{x:.0f}" y="{ly + 80}" text-anchor="middle" font-size="9.2" class="muted">{esc(l2)}</text></g>')
    b += synced(24, 246, right=False)

    b += f'<line x1="514" y1="22" x2="514" y2="{H - 22}" stroke="{BORDER}"/>'
    b += heading(530, 20, n + 1, "Open Source Activity", "Contributing to the developer community")
    boxes = [(user["public_repos"], "Repositories"), (stats["prs"], "Pull Requests"),
             (stats["issues"], "Issues"), (calendar["total"], "Contributions")]
    for i, (v, label) in enumerate(boxes):
        x = 530 + i * 75
        b += (f'<g class="pop" {d(.3 + i * .1)}>' + panel(x, 68, 69, 56, 8) +
              f'<text x="{x + 34.5}" y="96" text-anchor="middle" font-size="18" font-weight="800" fill="url(#og)">{compact(v)}</text>'
              f'<text x="{x + 34.5}" y="113" text-anchor="middle" font-size="8.6" class="muted">{label}</text></g>')
    b += f'<text x="530" y="148" font-size="11.5" font-weight="700" class="fade" {d(.6)}>Top Contributions</text>'
    top = stats["top_repos"][:4] or [("No public commits yet", 0)]
    mx = max(c for _, c in top) or 1
    for i, (repo, c) in enumerate(top):
        y = 170 + i * 21
        b += (f'<g class="rise" {d(.7 + i * .1)}>' + dot(536, y - 4, 3, ORANGE, "") +
              f'<text x="546" y="{y}" font-size="10.5" fill="#c9d1d9">{esc(trunc(repo, 24))}</text>'
              f'<rect x="690" y="{y - 7}" width="{60 * c / mx:.0f}" height="5" rx="2.5" fill="url(#og)" class="grow" {d(.9 + i * .1)}/>'
              f'<text x="826" y="{y}" text-anchor="end" font-size="10" class="muted mono">{c} commits</text></g>')
    return svg(W, H, b, title="Experience Timeline & Open Source Activity")


# ------------------------------------------------- analytics + exploring

HEAT = ["#161b22", "#4a2a12", "#8a4210", "#d4651a", "#ff9b50"]


def analytics_exploring(user: dict, stats: dict, calendar: dict, repos: dict, tech: dict,
                        til: list[dict] | None = None, n: int = 12) -> str:
    W, H = 850, 262
    b = frame(W, H)
    b += heading(24, 20, n, "GitHub Analytics", "My contribution activity")
    chips = [(stats["commits"], "Commits", ORANGE), (user["public_repos"], "Repositories", BLUE),
             (user["followers"], "Followers", GREEN), (user["following"], "Following", "#bc8cff")]
    for i, (v, label, c) in enumerate(chips):
        x = 24 + i * 123
        b += (f'<g class="pop" {d(.2 + i * .1)}>' + panel(x, 64, 115, 44, 8) +
              f'<circle cx="{x + 20}" cy="86" r="11" fill="{c}" fill-opacity=".15" stroke="{c}"/>'
              f'<circle cx="{x + 20}" cy="86" r="3.5" fill="{c}"/>'
              f'<text x="{x + 38}" y="85" font-size="15" font-weight="800">{compact(v)}</text>'
              f'<text x="{x + 38}" y="99" font-size="9" class="muted">{label}</text></g>')

    weeks = calendar["weeks"][-53:]
    cell, gap = 7.6, 1.7
    gx, gy = 40, 136
    last_month = None
    for wi, week in enumerate(weeks):
        x = gx + wi * (cell + gap)
        m = week[0]["date"][5:7]
        if m != last_month and wi < len(weeks) - 2:
            label = datetime.strptime(week[0]["date"], "%Y-%m-%d").strftime("%b")
            b += f'<text x="{x:.1f}" y="{gy - 6}" font-size="8.5" class="dim">{label}</text>'
            last_month = m
        for day in week:
            dow = datetime.strptime(day["date"], "%Y-%m-%d").weekday()  # Mon=0
            row = (dow + 1) % 7  # Sunday first, like GitHub
            b += (f'<rect x="{x:.1f}" y="{gy + row * (cell + gap):.1f}" width="{cell}" height="{cell}" rx="1.6" '
                  f'fill="{HEAT[min(day["level"], 4)]}" class="fade" style="animation-delay:{.3 + wi * .018:.2f}s">'
                  f'<title>{day["count"]} contributions on {day["date"]}</title></rect>')
    for i, lbl in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        b += f'<text x="24" y="{gy + i * (cell + gap) + 7:.1f}" font-size="8" class="dim">{lbl}</text>'
    b += (f'<text x="24" y="226" font-size="10.5" class="fade" {d(1.2)}><tspan fill="{AMBER}" font-weight="700">'
          f'{calendar["total"]:,}</tspan><tspan class="muted"> contributions in the last year</tspan></text>')
    lx = 400
    b += f'<text x="{lx}" y="226" font-size="8.5" class="dim">Less</text>'
    for i, c in enumerate(HEAT):
        b += f'<rect x="{lx + 22 + i * 11}" y="218" width="8" height="8" rx="1.5" fill="{c}"/>'
    b += f'<text x="{lx + 80}" y="226" font-size="8.5" class="dim">More</text>'
    b += synced(24, 248, right=False)

    b += f'<line x1="530" y1="22" x2="530" y2="{H - 22}" stroke="{BORDER}"/>'
    b += heading(546, 20, n + 1, "Currently Exploring", "Live: what my last 90 days of repos use")
    items = exploring(repos, tech)[:3 if til else 5]
    top = max((c for _, c, _ in items), default=1)
    for i, (label, count, new) in enumerate(items):
        y = 84 + i * 28
        b += (f'<g class="rise" {d(.3 + i * .12)}>' + dot(552, y - 4, 3.5, ORANGE, "") +
              f'<text x="562" y="{y}" font-size="11" fill="#c9d1d9">{esc(label)}</text>'
              f'<text x="826" y="{y}" text-anchor="end" font-size="10" class="mono ink" fill="{AMBER}">'
              f'{count} repo{"s" if count != 1 else ""}{f" · +{new} new" if new else ""}</text>'
              f'<rect x="562" y="{y + 6}" width="264" height="5" rx="2.5" fill="#1d1712"/>'
              f'<rect x="562" y="{y + 6}" width="{264 * count / top:.0f}" height="5" rx="2.5" fill="url(#og)" class="grow" '
              f'filter="url(#glow)" {d(.5 + i * .15)}/></g>')
    if not items:
        b += f'<text x="552" y="90" font-size="10.5" class="muted">Nothing pushed in the last 90 days — yet.</text>'
    if til:
        ty = 84 + len(items) * 28 + 10
        b += f'<text x="546" y="{ty}" font-size="11.5" font-weight="700" class="fade" {d(.8)}>📒 Today I Learned</text>'
        for i, entry in enumerate(til[:2]):
            y = ty + 20 + i * 30
            when = datetime.strptime(entry["date"], "%Y-%m-%d").strftime("%d %b") if entry["date"] else ""
            lines = wrap(entry["text"], 44, 2)
            b += (f'<g class="rise" {d(.9 + i * .1)}><rect x="546" y="{y - 11}" width="3" height="{14 * len(lines) + 2}" rx="1.5" fill="{ORANGE}"/>'
                  + "".join(f'<text x="556" y="{y + j * 13}" font-size="10" fill="#c9d1d9">{esc(line)}</text>' for j, line in enumerate(lines))
                  + (f'<text x="826" y="{y}" text-anchor="end" font-size="8.5" class="dim">{when}</text>' if when else "") + "</g>")
    return svg(W, H, b, title="GitHub Analytics & Currently Exploring")


def exploring(repos: dict, tech: dict, days: int = 90) -> list[tuple[str, int, int]]:
    """(TECH_STACK item, repos pushed in the last `days` using it, of which created in the last 30 days)."""
    now = datetime.now(timezone.utc)
    age = lambda iso: (now - datetime.fromisoformat(iso.replace("Z", "+00:00"))).days if iso else 10 ** 6
    recent = {r["name"] for r in repos["repos"] if age(r["pushed_at"]) <= days}
    fresh = {r["name"] for r in repos["repos"] if age(r.get("created_at")) <= 30}
    out = []
    for items in config.TECH_STACK.values():
        for name, _, _ in items:
            if config.TECH_ALIASES.get(name) == ["*"]:  # Git/GitHub: every repo, says nothing
                continue
            used = set(gh.tech_repo_names(tech, name)) & recent
            if used:
                out.append((name, len(used), len(used & fresh)))
    return sorted(out, key=lambda t: (-t[1], -t[2]))


# ------------------------------------------------- activity + terminal

KIND_STYLE = {
    "push": (ORANGE, "↑"), "pr": ("#bc8cff", "⇄"), "issue": (GREEN, "!"), "comment": (BLUE, "✎"),
    "create": (CYAN, "+"), "delete": ("#ff7b72", "−"), "star": (AMBER, "★"), "fork": (BLUE, "⑂"),
    "release": (GREEN, "◆"), "other": (MUTED, "•"),
}


def activity_terminal(user: dict, repos: dict, events: list[dict], n: int = 11) -> str:
    W, H = 850, 282
    b = frame(W, H)
    b += heading(24, 20, n, "Latest Activity", "Real time activity from GitHub")
    shown = events[:5]
    if not shown:
        b += '<text x="24" y="100" font-size="12" class="muted">No public activity in the last 90 days.</text>'
    for i, e in enumerate(shown):
        y = 70 + i * 38
        color, glyph = KIND_STYLE.get(e["kind"], KIND_STYLE["other"])
        b += (f'<g class="rise" {d(.2 + i * .12)}>' + panel(24, y, 392, 32, 7) +
              f'<circle cx="42" cy="{y + 16}" r="10" fill="{color}" fill-opacity=".14" stroke="{color}"/>'
              f'<text x="42" y="{y + 20}" text-anchor="middle" font-size="11" font-weight="800" fill="{color}">{glyph}</text>'
              f'<text x="60" y="{y + 14}" font-size="10.8" fill="#c9d1d9">{esc(trunc(e["text"], 46))}</text>'
              f'<text x="60" y="{y + 26}" font-size="8.8" class="dim">{esc(time_ago(e["at"]))}</text>'
              f'<text x="406" y="{y + 20}" text-anchor="end" font-size="9.5" class="dim mono">{esc(e["ref"])}</text></g>')
    b += synced(24, 270, right=False)

    b += heading(436, 20, n + 1, "Live Terminal", "Generated from live GitHub data")
    tx, ty, tw, th = 436, 64, 390, 196
    b += panel(tx, ty, tw, th, 10, stroke="#2b3646", fill="#0a0e15")
    for i, c in enumerate(("#ff5f56", "#ffbd2e", "#27c93f")):
        b += f'<circle cx="{tx + 14 + i * 13}" cy="{ty + 13}" r="4" fill="{c}"/>'
    b += f'<text x="{tx + tw - 12}" y="{ty + 17}" text-anchor="end" font-size="9.5" class="dim mono">bash</text>'
    langs = ", ".join(l for l, _ in repos["languages"][:4]) or "—"
    last_push = next((e for e in events if e["kind"] == "push"), None)
    last = f"{last_push['repo'].split('/')[-1]} · {time_ago(last_push['at'])}" if last_push else "—"
    session = [
        ("whoami", user["name"]),
        ("role", user["bio"] or config.PROFILE["role"]),
        ("gh stats", f"{user['public_repos']} repos · ★ {repos['total_stars']} · {user['followers']} followers"),
        ("cat languages", langs),
        ("git log -1", last),
    ]
    prompt = f"{user['login']}@dev:~$ "
    pw = len(prompt) * 6.6
    t = .4
    y = ty + 44
    for i, (cmd, out) in enumerate(session):
        b += (f'<text x="{tx + 12}" y="{y}" font-size="11" class="mono fade" fill="{GREEN}" {d(t - .1)}>{esc(prompt)}</text>'
              f'<text x="{tx + 12 + pw:.0f}" y="{y}" font-size="11" class="mono type" {d(t)}>{esc(cmd)}</text>')
        b += (f'<text x="{tx + 12}" y="{y + 15}" font-size="11" class="mono fade" fill="{AMBER}" {d(t + .6)}>'
              f'{esc(trunc(out, 54))}</text>')
        t += 1.0
        y += 30
    b += (f'<text x="{tx + 12}" y="{y}" font-size="11" class="mono fade" fill="{GREEN}" {d(t)}>{esc(prompt)}</text>'
          f'<rect x="{tx + 12 + pw:.0f}" y="{y - 10}" width="7" height="13" fill="{ORANGE}" class="blink"/>')
    return svg(W, H, b, title="Latest Activity & Live Terminal")


# ---------------------------------------------------------- playground

_TOKEN = re.compile(r'("(?:[^"\\]|\\.)*")(\s*:)?|(-?\d+(?:\.\d+)?)|(true|false|null)')


def _json_line(line: str) -> str:
    out, pos = "", 0
    for m in _TOKEN.finditer(line):
        out += esc(line[pos:m.start()])
        if m.group(1):
            col = "#ff9e64" if m.group(2) else "#a5d6ff"
            out += f'<tspan fill="{col}">{esc(m.group(1))}</tspan>{esc(m.group(2) or "")}'
        elif m.group(3):
            out += f'<tspan fill="#79c0ff">{m.group(3)}</tspan>'
        else:
            out += f'<tspan fill="#ff7b72">{m.group(4)}</tspan>'
        pos = m.end()
    return out + esc(line[pos:])


ENDPOINTS = [("GET", "/api/projects", "Get all projects"), ("GET", "/api/github/stats", "Get GitHub statistics"),
             ("GET", "/api/activity", "Latest public activity"), ("GET", "/api/experience", "Experience timeline"),
             ("GET", "/api/tech-stack", "Get technologies")]


def playground(repos: dict, request_url: str, n: int = 13) -> str:
    W, H = 850, 292
    b = frame(W, H) + heading(24, 20, n, "API Playground", "Live response from this profile's own API")
    for i, (m, path, desc) in enumerate(ENDPOINTS):
        y = 66 + i * 42
        active = i == 0
        b += (f'<g class="rise" {d(.2 + i * .08)}>' +
              panel(24, y, 250, 36, 8, stroke=ORANGE if active else BORDER, fill="#1a1109" if active else "url(#cardg)") +
              f'<rect x="34" y="{y + 10}" width="34" height="16" rx="4" fill="{GREEN}" fill-opacity=".18" stroke="{GREEN}"/>'
              f'<text x="51" y="{y + 21.5}" text-anchor="middle" font-size="8.5" font-weight="800" fill="{GREEN}">{m}</text>'
              f'<text x="76" y="{y + 16}" font-size="10.5" class="mono ink">{esc(path)}</text>'
              f'<text x="76" y="{y + 29}" font-size="8.8" class="muted">{esc(desc)}</text></g>')

    rx = 290
    b += panel(rx, 66, 536, 30, 7, fill="#0a0e15")
    b += (f'<text x="{rx + 12}" y="85" font-size="10.5" font-weight="800" fill="{GREEN}">GET</text>'
          f'<text x="{rx + 44}" y="85" font-size="10.5" class="mono">{esc(trunc(request_url, 58))}</text>')
    b += (f'<rect x="{rx + 430}" y="70" width="102" height="22" rx="5" fill="url(#og)" class="glowpulse"/>'
          f'<text x="{rx + 481}" y="85" text-anchor="middle" font-size="10.5" font-weight="800" fill="#1a0d02">Send Request</text>')
    for i, t in enumerate(("Response", "Headers", "cURL")):
        x = rx + i * 78
        b += f'<text x="{x + 6}" y="116" font-size="10.5" fill="{ORANGE if i == 0 else MUTED}" font-weight="{700 if i == 0 else 400}">{t}</text>'
    b += f'<rect x="{rx + 2}" y="121" width="56" height="2" fill="{ORANGE}"/>'
    b += (f'<text x="826" y="116" text-anchor="end" font-size="9.5" class="mono fade" {d(.8)}>'
          f'<tspan fill="{GREEN}">200 OK</tspan><tspan class="dim">  ·  application/json</tspan></text>')

    top = featured(repos["repos"], 4)
    lines = ['{', '  "status": "success",', f'  "total": {len(repos["repos"])},', '  "projects": [']
    for i, r in enumerate(top):
        item = json.dumps({"name": r["name"], "lang": r["language"], "stars": r["stars"]})
        lines.append(f'    {item}{"," if i < len(top) - 1 else ""}')
    lines += ['  ]', '}']
    b += panel(rx, 128, 536, H - 128 - 18, 8, fill="#0a0e15")
    for i, line in enumerate(lines[:11]):
        y = 146 + i * 12.4
        b += (f'<text x="{rx + 10}" y="{y:.1f}" font-size="8.5" class="dim mono">{i + 1:>2}</text>'
              f'<text x="{rx + 30}" y="{y:.1f}" font-size="10" class="mono fade" fill="{TEXT}" {d(1 + i * .12)}>{_json_line(line)}</text>')
    return svg(W, H, b, title="API Playground")


# ---------------------------------------------------------- developer os

def developer_os(user: dict, repos: dict, events: list[dict], n: int = 19) -> str:
    W, H = 850, 262
    b = frame(W, H) + heading(24, 20, n, "Developer OS", "System status and tools I work with")
    tx, ty, tw, th = 24, 64, 486, 180
    b += panel(tx, ty, tw, th, 10, stroke="#2b3646", fill="#0a0e15")
    b += (f'<text x="{tx + 14}" y="{ty + 22}" font-size="11" class="mono"><tspan fill="{GREEN}">{esc(user["login"])}@dev:~$</tspan>'
          f'<tspan> neofetch</tspan></text>')
    # logo
    lx, ly = tx + 22, ty + 40
    b += (f'<g class="pop" {d(.2)}><rect x="{lx}" y="{ly}" width="96" height="96" rx="18" fill="#140c05" stroke="{ORANGE}" filter="url(#glow)"/>'
          f'<path d="M{lx + 22} {ly + 32} l18 16 -18 16" stroke="{AMBER}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>'
          f'<rect x="{lx + 46}" y="{ly + 60}" width="28" height="6" rx="3" fill="{AMBER}" class="blink"/></g>')
    created = datetime.fromisoformat(user["created_at"].replace("Z", "+00:00"))
    days = (datetime.now(timezone.utc) - created).days
    uptime = f"{days // 365} years, {(days % 365) // 30} months"
    langs = ", ".join(l for l, _ in repos["languages"][:3]) or "—"
    info = [
        ("User", f"{user['login']}@github"),
        ("Name", user["name"]),
        ("Location", user["location"] or "Earth"),
        ("Uptime", uptime),
        ("Repos", f"{user['public_repos']} public · ★ {repos['total_stars']}"),
        ("Languages", langs),
        ("Network", f"{user['followers']} followers · {user['following']} following"),
        ("Editor", "VS Code"),
    ]
    ix = tx + 138
    for i, (k, v) in enumerate(info):
        y = ty + 46 + i * 15.5
        b += (f'<text x="{ix}" y="{y:.1f}" font-size="10.5" class="mono fade" {d(.3 + i * .1)}>'
              f'<tspan fill="{ORANGE}" font-weight="700">{k:<10}</tspan><tspan fill="#c9d1d9">{esc(trunc(v, 36))}</tspan></text>')
    total = sum(c for _, c in repos["languages"]) or 1
    x = ix
    bw = tw - (ix - tx) - 16
    for i, (lang, c) in enumerate(repos["languages"][:6]):
        w = bw * c / total
        b += (f'<rect x="{x:.1f}" y="{ty + th - 22}" width="{max(w - 1.5, 1):.1f}" height="8" rx="2" fill="{lang_color(lang)}" '
              f'class="grow" {d(1 + i * .12)}><title>{esc(lang)}: {c} repos</title></rect>')
        x += w

    sx = 526
    b += panel(sx, 64, 300, 180, 10)
    b += f'<text x="{sx + 14}" y="{86}" font-size="12" font-weight="700">System Status</text>'
    last_push = next((e for e in events if e["kind"] == "push"), None)
    rows = [
        ("GitHub API", f"Connected · {user['latency_ms']} ms", GREEN),
        ("Profile API", "Online", GREEN),
        ("Data Sync", "Live", GREEN),
        ("Last Push", time_ago(last_push["at"]) if last_push else "—", AMBER),
        ("Last Event", time_ago(events[0]["at"]) if events else "—", AMBER),
        ("Deployment", "Ready", GREEN),
    ]
    for i, (k, v, c) in enumerate(rows):
        y = 110 + i * 21
        b += (f'<g class="rise" {d(.4 + i * .1)}><text x="{sx + 14}" y="{y}" font-size="10.5" fill="#c9d1d9">{k}</text>'
              f'<circle cx="{sx + 150}" cy="{y - 3.5}" r="3.5" fill="{c}" class="pulse" style="animation-delay:{i * .3:.1f}s"/>'
              f'<text x="{sx + 160}" y="{y}" font-size="10" class="mono" fill="{c}">{esc(v)}</text></g>')
    b += synced(826, 256)
    return svg(W, H, b, title="Developer OS")


# ---------------------------------------------------------- now building

def now_building(data: dict | None, n: int | None = 7) -> str:
    W, H = 850, 236
    b = frame(W, H)
    b += heading(24, 20, n, "Now Building", "The repository I'm working on right now, live from GitHub")
    if not data:
        b += f'<text x="{W / 2}" y="140" text-anchor="middle" font-size="13" class="muted">Something new is on the way…</text>'
        return svg(W, H, b, title="Now Building")
    repo, commits, latest = data["repo"], data["commits"], data["latest"]
    days_since = (datetime.now(timezone.utc) - datetime.fromisoformat(repo["pushed_at"].replace("Z", "+00:00"))).days
    status, scolor = (("ACTIVE", GREEN) if days_since <= 3 else ("IN PROGRESS", AMBER) if days_since <= 14
                      else ("ON PAUSE", MUTED))

    # left: the repo
    lx = 24
    b += f'<g class="rise" {d(.15)}>' + panel(lx, 66, 470, 150, 10, stroke=ORANGE, extra='stroke-opacity=".45"')
    sw = len(status) * 6.6 + 26
    b += (f'<rect x="{lx + 16}" y="80" width="{sw:.0f}" height="20" rx="10" fill="{scolor}" fill-opacity=".15" stroke="{scolor}"/>'
          f'<circle cx="{lx + 27}" cy="90" r="3.5" fill="{scolor}" class="pulse"/>'
          f'<text x="{lx + 36}" y="94" font-size="9.5" font-weight="800" fill="{scolor}">{status}</text>')
    b += (f'<text x="{lx + 470 - 16}" y="94" text-anchor="end" font-size="10" class="dim mono">'
          f'last push {esc(time_ago(repo["pushed_at"]))}</text>')
    b += f'<text x="{lx + 16}" y="126" font-size="19" font-weight="800">{esc(trunc(repo["name"].replace("_", " "), 38))}</text>'
    if repo["language"]:
        b += (f'<circle cx="{lx + 20}" cy="141" r="4.5" fill="{repo["color"]}"/>'
              f'<text x="{lx + 30}" y="145" font-size="10.5" class="muted">{esc(repo["language"])}</text>')
    desc = wrap(repo["description"] or "Work in progress — follow along on GitHub.", 70, 1)
    b += f'<text x="{lx + (110 if repo["language"] else 16)}" y="145" font-size="10.5" class="muted">{esc(desc[0])}</text></g>'
    # terminal line with the latest commit
    ty = 160
    b += (f'<g class="fade" {d(.4)}><rect x="{lx + 12}" y="{ty}" width="446" height="44" rx="7" fill="#0a0e15" stroke="#1d2633"/>'
          f'<text x="{lx + 24}" y="{ty + 17}" font-size="10" class="mono"><tspan fill="{GREEN}">$</tspan>'
          f'<tspan fill="#c9d1d9"> git log -1 --oneline</tspan></text></g>')
    if latest:
        b += (f'<text x="{lx + 24}" y="{ty + 34}" font-size="10" class="mono type" {d(.9)}>'
              f'<tspan fill="{AMBER}">{esc(latest["sha"])}</tspan>'
              f'<tspan fill="#c9d1d9"> {esc(trunc(latest["message"], 58))}</tspan></text>')

    # right: 30-day momentum
    rx, rw = 512, 314
    b += f'<g class="rise" {d(.3)}>' + panel(rx, 66, rw, 150, 10)
    b += f'<text x="{rx + 16}" y="88" font-size="11.5" font-weight="700">30-day momentum</text>'
    b += (f'<text x="{rx + rw - 16}" y="88" text-anchor="end" font-size="10" class="mono ink" fill="{AMBER}">'
          f'{len(commits)} commit{"s" if len(commits) != 1 else ""}</text></g>')
    today = datetime.now(timezone.utc).date()
    per_day = Counter(c["date"][:10] for c in commits)
    counts = [per_day.get(str(today.fromordinal(today.toordinal() - (29 - i))), 0) for i in range(30)]
    top = max(counts) or 1
    bx, bbase, bwid = rx + 16, 162, (rw - 32) / 30
    for i, c in enumerate(counts):
        h = 3 if not c else 6 + 52 * c / top
        b += (f'<rect x="{bx + i * bwid:.1f}" y="{bbase - h:.1f}" width="{bwid - 2.5:.1f}" height="{h:.1f}" rx="1.5" '
              f'fill="{ORANGE if c else "#1d2633"}" class="growy" style="animation-delay:{.4 + i * .03:.2f}s">'
              f'<title>{c} commits</title></rect>')
    active = sum(1 for c in counts if c)
    b += (f'<text x="{rx + 16}" y="182" font-size="10" class="muted">{active} of 30 days active</text>'
          f'<text x="{rx + rw - 16}" y="182" text-anchor="end" font-size="10" class="dim">today →</text>'
          f'<rect x="{rx + 16}" y="192" width="{rw - 32}" height="7" rx="3.5" fill="#1d1712"/>'
          f'<rect x="{rx + 16}" y="192" width="{(rw - 32) * active / 30:.0f}" height="7" rx="3.5" fill="url(#og)" '
          f'class="grow" filter="url(#glow)" {d(.8)}/>')
    b += synced(826, H - 8)
    return svg(W, H, b, title="Now Building")


# ------------------------------------------------------------ coding DNA

# persona -> hours (local time of each commit) and how the share is described
CODER_TYPES = [
    ("Night Owl", set(range(22, 24)) | set(range(0, 5)), "between 10 PM and 5 AM"),
    ("Early Bird", set(range(5, 11)), "between 5 and 11 AM"),
    ("Daytime Coder", set(range(11, 18)), "between 11 AM and 6 PM"),
    ("Evening Coder", set(range(18, 22)), "between 6 and 10 PM"),
]


def _hsl(h: float, s: float, l: float) -> str:
    import colorsys

    r, g, b_ = colorsys.hls_to_rgb(h, l, s)
    return f"#{int(r * 255):02x}{int(g * 255):02x}{int(b_ * 255):02x}"


def coding_dna(commits: list[dict], n: int | None = 8) -> str:
    """When I code (a 24-hour clock of my commits) and generative art grown from my commit hashes."""
    W, H = 850, 270
    b = frame(W, H)
    b += heading(24, 20, n, "Coding DNA", "When I code, and art generated from my latest commits")
    if not commits:
        b += f'<text x="{W / 2}" y="150" text-anchor="middle" font-size="13" class="muted">Waiting for my first public commits…</text>'
        return svg(W, H, b, title="Coding DNA")

    hours = Counter(int(c["date"][11:13]) for c in commits)
    days = Counter(datetime.fromisoformat(c["date"].replace("Z", "+00:00")).strftime("%A") for c in commits)
    total = len(commits)
    persona, span, words = max(CODER_TYPES, key=lambda t: sum(hours[h] for h in t[1]))
    share = round(100 * sum(hours[h] for h in span) / total)
    peak_hour = max(range(24), key=lambda h: hours[h])

    # 24-hour radial clock
    cx, cy, r0, r1 = 150, 162, 26, 68
    top = max(hours.values())
    b += f'<circle cx="{cx}" cy="{cy}" r="{r1 + 6}" fill="#0b1018" stroke="{BORDER}"/>'
    b += f'<circle cx="{cx}" cy="{cy}" r="{r0 - 4}" fill="url(#cardg)" stroke="{BORDER}"/>'
    for h in range(24):
        a = math.radians(h * 15 - 90)
        length = (r1 - r0) * (hours[h] / top) if hours[h] else 2
        in_span = h in span
        x1, y1 = cx + r0 * math.cos(a), cy + r0 * math.sin(a)
        x2, y2 = cx + (r0 + length) * math.cos(a), cy + (r0 + length) * math.sin(a)
        b += (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{ORANGE if in_span else "#4a5a72"}" '
              f'stroke-width="5.5" stroke-linecap="round" class="fade" style="animation-delay:{.3 + h * .04:.2f}s">'
              f'<title>{hours[h]} commits at {h:02d}:00</title></line>')
    for h, label in ((0, "12AM"), (6, "6AM"), (12, "12PM"), (18, "6PM")):
        a = math.radians(h * 15 - 90)
        b += (f'<text x="{cx + (r1 + 22) * math.cos(a):.0f}" y="{cy + (r1 + 14) * math.sin(a) + 3:.0f}" text-anchor="middle" '
              f'font-size="8.5" class="dim">{label}</text>')
    icon = {"Night Owl": "🦉", "Early Bird": "🐦", "Daytime Coder": "☀", "Evening Coder": "🌆"}[persona]
    b += f'<text x="{cx}" y="{cy + 6}" text-anchor="middle" font-size="18">{icon}</text>'

    # habits
    tx = 290
    b += (f'<g class="rise" {d(.3)}><text x="{tx}" y="96" font-size="24" font-weight="800" fill="url(#og)">{persona}</text>'
          f'<text x="{tx}" y="116" font-size="11" fill="#c9d1d9">{share}% of my commits land {words}</text></g>')
    weekend = round(100 * (days["Saturday"] + days["Sunday"]) / total)
    facts = [("Peak hour", f"{peak_hour % 12 or 12} {'AM' if peak_hour < 12 else 'PM'}"),
             ("Busiest day", max(days, key=days.get)),
             ("Weekend commits", f"{weekend}%"),
             ("Commits sampled", str(total))]
    for i, (k, v) in enumerate(facts):
        y = 146 + i * 24
        b += (f'<g class="rise" {d(.45 + i * .08)}>' + dot(tx + 4, y - 4, 3, ORANGE, "") +
              f'<text x="{tx + 14}" y="{y}" font-size="10.5" class="muted">{k}</text>'
              f'<text x="{tx + 210}" y="{y}" text-anchor="end" font-size="11" font-weight="700" fill="{AMBER}">{esc(v)}</text></g>')

    # generative art from the latest commit hashes (and today's date, so it shifts daily)
    ax, ay = 690, 150
    seed = datetime.now(timezone.utc).strftime("%Y%m%d")
    petals = commits[:24]
    art = ""
    for i, c in enumerate(petals):
        hb = bytes.fromhex(c["sha"][:12])
        angle = i * 360 / len(petals) + hb[0] / 255 * 12
        length = 26 + hb[1] / 255 * 50
        width = 4 + hb[2] / 255 * 10
        color = _hsl(((hb[3] / 255) * .25 + int(seed) % 97 / 97) % 1, .85, .6)
        art += (f'<ellipse cx="{ax}" cy="{ay - length / 2:.1f}" rx="{width:.1f}" ry="{length / 2:.1f}" fill="{color}" '
                f'fill-opacity=".55" transform="rotate({angle:.1f} {ax} {ay})"><title>{c["sha"][:7]} · {esc(c["repo"])}</title></ellipse>')
    b += f'<rect x="560" y="66" width="266" height="178" rx="10" fill="#0b1018" stroke="{BORDER}"/>'
    b += f'<g class="spin" style="animation-duration:90s">{art}</g>'
    b += f'<circle cx="{ax}" cy="{ay}" r="9" fill="url(#og)" filter="url(#glow)"/>'
    b += (f'<text x="693" y="238" text-anchor="middle" font-size="8.5" class="dim">'
          f'grown from my last {len(petals)} commit hashes · redraws on every push</text>')
    b += synced(24, H - 8, right=False)
    return svg(W, H, b, title="Coding DNA")


# ---------------------------------------------------- smart contract lab

SOL_KEYWORDS = {"pragma", "solidity", "contract", "public", "external", "function", "event", "indexed",
                "require", "emit", "true", "false", "returns", "view"}
SOL_TYPES = {"string", "uint256", "bool", "address"}
_SOL_TOKEN = re.compile(r'(//.*$|"[^"]*"|\b\d[\d.]*\b|\b[A-Za-z_]\w*\b|\S)')

# (label, alias looked up with tech_count)
WEB3_TOOLS = [("Hardhat", "hardhat"), ("Foundry", "foundry"), ("Truffle", "truffle"), ("Ethers.js", "ethers"),
              ("Web3.js", "web3"), ("OpenZeppelin", "@openzeppelin/*"), ("MetaMask", "metamask")]


def _sol_line(line: str) -> str:
    """Syntax-highlight one line of Solidity as tspans."""
    out, pos = "", 0
    for m in _SOL_TOKEN.finditer(line):
        out += esc(line[pos:m.start()])
        tok = m.group(0)
        if tok.startswith("//"):
            color = "#6a737d"
        elif tok.startswith('"'):
            color = "#a5d6ff"
        elif tok[0].isdigit():
            color = AMBER
        elif tok in SOL_KEYWORDS:
            color = ETH
        elif tok in SOL_TYPES:
            color = CYAN
        elif tok[0].isupper():
            color = "#ffa657"
        else:
            color = ""
        out += f'<tspan fill="{color}">{esc(tok)}</tspan>' if color else esc(tok)
        pos = m.end()
    return out + esc(line[pos:])


def _eth_diamond(cx, cy, s=14) -> str:
    return (f'<g class="float" filter="url(#glow)">'
            f'<polygon points="{cx},{cy - s} {cx + s * .62:.1f},{cy + s * .1:.1f} {cx},{cy + s * .45:.1f} {cx - s * .62:.1f},{cy + s * .1:.1f}" fill="{ETH}" fill-opacity=".9"/>'
            f'<polygon points="{cx},{cy + s * .6:.1f} {cx + s * .62:.1f},{cy + s * .25:.1f} {cx},{cy + s:.1f} {cx - s * .62:.1f},{cy + s * .25:.1f}" fill="{ETH}" fill-opacity=".6"/>'
            f'<polygon points="{cx},{cy - s} {cx},{cy + s * .45:.1f} {cx + s * .62:.1f},{cy + s * .1:.1f}" fill="#fff" fill-opacity=".18"/></g>')


def smart_contract_lab(user: dict, repos: dict, tech: dict, n: int | None = 4) -> str:
    sol = gh.tech_repo_names(tech, "Solidity")
    by_name = {r["name"]: r for r in repos["repos"]}
    sol_repos = sorted((by_name[n] for n in sol if n in by_name), key=lambda r: r["pushed_at"] or "", reverse=True)
    tools = ["Solidity"] + [label for label, alias in WEB3_TOOLS if gh.tech_count(tech, alias)]

    # editor with a contract written from the live profile
    ident = re.sub(r"\W", "", user["name"].title()) or "Developer"
    code = [
        "// SPDX-License-Identifier: MIT",
        "pragma solidity ^0.8.24;",
        "",
        f"contract {ident} {{",
        f'    string public role = "{config.PROFILE["role"]}";',
        f"    uint256 public solidityRepos = {len(sol)};",
        f"    bool public openToWork = {'true' if config.PROFILE.get('available') else 'false'};",
        "",
        "    event Hired(address indexed by);",
        "",
        "    function hire() external {",
        '        require(openToWork, "busy building");',
        "        emit Hired(msg.sender);",
        "    }",
        "}",
    ]
    ex, ey, ew = 24, 70, 452
    eh = 34 + len(code) * 14 + 26
    W, H = 850, ey + eh + 22

    b = frame(W, H)
    b += f'<circle cx="780" cy="40" r="70" fill="{ETH}" fill-opacity=".10" filter="url(#softglow)" class="glowpulse"/>'
    b += heading(24, 20, n, "Smart Contract Lab", "Solidity & Web3 — where my full-stack work goes on-chain")
    b += _eth_diamond(800, 40)
    b += f'<g class="rise" {d(.1)}>' + panel(ex, ey, ew, eh, 10, stroke="#2b2f55", fill="#0a0c16")
    b += f'<rect x="{ex}" y="{ey}" width="{ew}" height="24" rx="10" fill="#11142a"/>'
    b += f'<rect x="{ex}" y="{ey + 14}" width="{ew}" height="10" fill="#11142a"/>'
    b += (f'<rect x="{ex + 10}" y="{ey + 4}" width="92" height="20" rx="5" fill="#0a0c16"/>'
          f'<circle cx="{ex + 21}" cy="{ey + 14}" r="3.5" fill="{ETH}"/>'
          f'<text x="{ex + 30}" y="{ey + 18}" font-size="10" class="mono" fill="#c9d1d9">Profile.sol</text>')
    b += f'<text x="{ex + ew - 12}" y="{ey + 17}" text-anchor="end" font-size="9" class="mono dim">solc 0.8.24</text></g>'
    for i, line in enumerate(code):
        y = ey + 42 + i * 14
        b += f'<text x="{ex + 12}" y="{y}" font-size="9" class="mono dim">{i + 1:>2}</text>'
        if line:
            b += (f'<text x="{ex + 34}" y="{y}" font-size="10" class="mono type" fill="#c9d1d9" '
                  f'style="animation-delay:{.4 + i * .18:.2f}s">{_sol_line(line)}</text>')
    yb = ey + eh - 10
    b += (f'<text x="{ex + 12}" y="{yb}" font-size="9.5" class="mono fade" fill="{GREEN}" {d(.6 + len(code) * .18)}>'
          f'✓ Compiled Profile.sol · 0 errors</text>')
    b += f'<rect x="{ex + 34 + 1 * 6}" y="{ey + 42 + 14 * (len(code) - 1) - 9}" width="6" height="11" fill="{ETH}" class="blink"/>'

    # right column: live Solidity repos and detected tooling
    rx = 494
    b += (f'<g class="pop" {d(.3)}>' + panel(rx, 70, 332, 52, 10, stroke=ETH, extra='stroke-opacity=".45"') +
          f'<text x="{rx + 16}" y="104" font-size="26" font-weight="800" fill="{ETH}">{len(sol)}</text>'
          f'<text x="{rx + 52}" y="92" font-size="11" font-weight="700">Solidity repositories</text>'
          f'<text x="{rx + 52}" y="107" font-size="9.5" class="muted">detected live from my GitHub</text></g>')
    x, y = rx, 134
    for i, t in enumerate(tools):
        w = len(t) * 6 + 18
        if x + w > rx + 332:
            x, y = rx, y + 26
        b += (f'<g class="pop" {d(.5 + i * .08)}><rect x="{x}" y="{y}" width="{w:.0f}" height="20" rx="5" '
              f'fill="{ETH}" fill-opacity=".12" stroke="{ETH}" stroke-opacity=".5"/>'
              f'<text x="{x + w / 2:.0f}" y="{y + 14}" text-anchor="middle" font-size="10" fill="#c9cbff">{esc(t)}</text></g>')
        x += w + 6
    y += 34
    if not sol_repos:
        b += f'<text x="{rx}" y="{y + 14}" font-size="10.5" class="muted">First public contract coming soon…</text>'
    for i, r in enumerate(sol_repos[:3]):
        yy = y + i * 50
        b += (f'<g class="rise" {d(.7 + i * .12)}>' + panel(rx, yy, 332, 42, 8) +
              f'<rect x="{rx}" y="{yy}" width="3" height="42" rx="1.5" fill="{ETH}"/>'
              f'<text x="{rx + 14}" y="{yy + 17}" font-size="11" font-weight="700">{esc(trunc(r["name"], 34))}</text>'
              f'<text x="{rx + 318}" y="{yy + 17}" text-anchor="end" font-size="9" class="muted">★ {r["stars"]} · {esc(time_ago(r["pushed_at"]))}</text>'
              f'<text x="{rx + 14}" y="{yy + 32}" font-size="9.5" class="muted">{esc(trunc(r["description"] or "Solidity smart contracts", 58))}</text></g>')
    b += synced(826, H - 12)
    return svg(W, H, b, title="Smart Contract Lab")


# --------------------------------------------------- contribution city

# building faces per contribution level 1-4: front, top, side
CITY = [("#3a1d0c", "#6b3615", "#26130a"), ("#6b2f0e", "#a94d18", "#46200b"),
        ("#a8461a", "#e2702e", "#6e2d10"), ("#e0682a", "#ffad6b", "#93401a")]


def _streaks(days: list[dict]) -> tuple[int, int]:
    """(current, longest) runs of days with contributions. Today may still be empty."""
    longest = run = 0
    for day in days:
        run = run + 1 if day["count"] else 0
        longest = max(longest, run)
    current = 0
    for day in reversed(days[:-1] if days and not days[-1]["count"] else days):
        if not day["count"]:
            break
        current += 1
    return current, longest


def _pet(cx: float, base: float, stage: str, mood: str) -> str:
    """The city's coding pet. stage: egg / chick / bird (grows with my best streak);
    mood: happy / waiting / sad / sleeping (how long since my last contribution)."""
    if stage == "egg":
        fx, fy = cx, base - 13
        o = (f'<ellipse cx="{cx}" cy="{base - 13}" rx="10" ry="13" fill="#f3e9d2" stroke="#c9b48a"/>'
             f'<circle cx="{cx - 5}" cy="{base - 20}" r="1.8" fill="#d9c49a"/><circle cx="{cx + 5}" cy="{base - 6}" r="1.4" fill="#d9c49a"/>')
    elif stage == "chick":
        fx, fy = cx + 2, base - 14
        o = (f'<path d="M{cx - 4},{base}v-3M{cx + 4},{base}v-3" stroke="{ORANGE}" stroke-width="1.6"/>'
             f'<circle cx="{cx}" cy="{base - 12}" r="11" fill="#ffd84d" stroke="#e0b52c"/>'
             f'<ellipse cx="{cx - 7}" cy="{base - 10}" rx="4" ry="6" fill="#f2c230" transform="rotate(20 {cx - 7} {base - 10})"/>'
             f'<path d="M{cx + 10},{base - 13}l5,1.5 -5,1.5z" fill="{ORANGE}"/>')
    else:
        fx, fy = cx + 9, base - 24
        o = (f'<path d="M{cx - 4},{base}v-5M{cx + 4},{base}v-5" stroke="#c2410c" stroke-width="1.8"/>'
             f'<path d="M{cx - 13},{base - 14}l-9,-4 2,6 -3,4z" fill="#c2410c"/>'
             f'<ellipse cx="{cx}" cy="{base - 13}" rx="14" ry="11" fill="{ORANGE}" stroke="#c2410c"/>'
             f'<ellipse cx="{cx + 2}" cy="{base - 10}" rx="8" ry="6" fill="#ffd2a8"/>'
             f'<ellipse cx="{cx - 5}" cy="{base - 14}" rx="7" ry="5" fill="#d9480f" transform="rotate(-15 {cx - 5} {base - 14})"/>'
             f'<circle cx="{cx + 9}" cy="{base - 24}" r="8" fill="{ORANGE}" stroke="#c2410c"/>'
             f'<path d="M{cx + 7},{base - 31}l-2,-6M{cx + 10},{base - 32}l1,-6M{cx + 12},{base - 31}l4,-5" stroke="#d9480f" stroke-width="1.8" stroke-linecap="round"/>'
             f'<path d="M{cx + 16},{base - 24}l6,2 -6,2z" fill="#ffd76a"/>')
    # face
    if mood == "happy":
        o += (f'<path d="M{fx - 4},{fy}q1.5,-2.5 3,0M{fx + 1.5},{fy}q1.5,-2.5 3,0" stroke="#1a0d02" stroke-width="1.3"/>'
              f'<circle cx="{fx - 4}" cy="{fy + 3}" r="1.6" fill="#ff7b9c" fill-opacity=".7"/>')
    elif mood == "sleeping":
        o += f'<path d="M{fx - 4},{fy}h3M{fx + 1.5},{fy}h3" stroke="#1a0d02" stroke-width="1.3"/>'
    else:
        o += f'<circle cx="{fx - 2.5}" cy="{fy}" r="1.4" fill="#1a0d02"/><circle cx="{fx + 3}" cy="{fy}" r="1.4" fill="#1a0d02"/>'
        if mood == "sad":
            o += f'<path d="M{fx - 3},{fy + 1.5}q-1,3 0,4q1,-1 0,-4z" fill="#58a6ff"/>'
    cls = {"happy": 'class="float" style="animation-duration:.9s"', "sleeping": 'class="pulse" style="animation-duration:4s"'}
    out = f'<g {cls.get(mood, "")}>{o}</g>'
    if mood == "happy":
        out += "".join(f'<path d="M{cx + dx},{base - 40 - k * 4}c-2,-3 -6,0 0,4c6,-4 2,-7 0,-4z" fill="#ff5e8a" class="twinkle" '
                       f'style="animation-delay:{k * .6}s"/>' for k, dx in enumerate((-10, 12)))
    if mood == "sleeping":
        out += "".join(f'<text x="{cx + 10 + k * 6}" y="{base - 32 - k * 7}" font-size="{8 + k * 2}" font-weight="800" fill="#8fb3ff" '
                       f'class="twinkle" style="animation-delay:{k * .5}s">z</text>' for k in range(3))
    return out


PET_LINES = {
    "happy": "Fed with commits today!",
    "waiting": "Hungry… push a commit?",
    "sad": "{days} days without code…",
    "sleeping": "zzz… wake me with a commit",
}


def contribution_city(user: dict, calendar: dict, weather: dict | None = None, feeds: dict | None = None) -> str:
    """Last year of contributions as a 3D city: one building per day, under the sky, weather and
    festival of the moment in India, with a coding pet that lives on my streak."""
    phase, fest = sky_phase(), festival_today()
    W, H = 850, 270 + (16 if fest in GROUND_FESTIVALS else 0)
    lit, colors = (FESTIVALS[fest][2], FESTIVALS[fest][1]) if fest else (SKIES[phase][3], [AMBER])
    weeks = calendar["weeks"][-53:]
    days = sorted((day for week in weeks for day in week), key=lambda x: x["date"])
    peak = max(days, key=lambda x: x["count"]) if days else {"count": 0, "date": ""}
    top = max(peak["count"], 1)
    current, longest = _streaks(days)

    b = frame(W, H, ember=False) + sky(1, 1, W - 2, H - 2, phase, strong=True)
    if phase == "night":
        b += stars(380, 60, 450, 60, n=28, seed=4)
    if fest != "eid":  # Eid brings its own crescent
        b += f'<g class="fade" {d(.3)}>{celestial(470, 96 if phase in LOW_SUN else 66, phase, r=15)}</g>'
    b += weather_sky(weather, 1, 1, W - 2, 232, seed=calendar["total"])
    if fest:
        b += festival_sky(fest, 370, 66, 450, 90, seed=calendar["total"])
        b += (f'<text x="250" y="118" text-anchor="middle" font-size="20" font-weight="800" fill="url(#og)" '
              f'filter="url(#glow)" class="pop" {d(.5)}>{esc(FESTIVALS[fest][0])}</text>')
    b += heading(24, 20, None, "Contribution City",
                 f"Every building is one day of my last year on GitHub · {calendar['total']:,} contributions")
    chips = [(str(current), "day streak", AMBER), (str(longest), "best streak", AMBER),
             (str(peak["count"]), "best day", AMBER)]
    if weather and weather.get("aqi") is not None:
        chips.append((str(weather["aqi"]), "AQI now", aqi_color(weather["aqi"])))
    x = W - 24
    for i, (v, label, color) in enumerate(reversed(chips)):
        w = 70
        x -= w
        b += (f'<g class="pop" {d(.2 + i * .1)}>' + panel(x, 22, w, 38, 8) +
              f'<text x="{x + w / 2}" y="41" text-anchor="middle" font-size="14" font-weight="800" fill="{color}">{v}</text>'
              f'<text x="{x + w / 2}" y="53" text-anchor="middle" font-size="8.5" class="muted">{label}</text></g>')
        x -= 8

    # oblique projection: weeks run left to right, Sunday is the back row (up and right)
    sx, step, bw, ox = 13.2, 5, 10, 4
    x0 = (W - (len(weeks) * sx + 6 * step + bw)) / 2
    ground = 230
    floor = (f'{x0 - 6:.0f},{ground + 4} {x0 + len(weeks) * sx + 4:.0f},{ground + 4} '
             f'{x0 + len(weeks) * sx + 6 * step + 10:.0f},{ground - 6 * step - 4} {x0 + 6 * step:.0f},{ground - 6 * step - 4}')
    b += f'<polygon points="{floor}" fill="#0b111a" stroke="{BORDER}"/>'
    monsoon = bool(weather) and weather["kind"] in ("rain", "storm")
    if monsoon:  # the streets flood: water over the floor with rings where the drops land
        b += f'<polygon points="{floor}" fill="#2f6fb0" fill-opacity=".38"/>'
        wr = random.Random(7)
        for _ in range(16):
            rx_, ry_ = x0 + wr.random() * len(weeks) * sx, ground - wr.random() * 6 * step
            b += (f'<ellipse cx="{rx_ + (ground - ry_):.0f}" cy="{ry_:.0f}" rx="5" ry="1.6" stroke="#9ec9ff" stroke-opacity=".6" '
                  f'class="pulse" style="animation-delay:{wr.random() * 2:.1f}s"/>')
    rnd = random.Random(calendar["total"])
    today = days[-1]["date"] if days else ""
    blocks = []
    for wi, week in enumerate(weeks):
        for day in week:
            row = (datetime.strptime(day["date"], "%Y-%m-%d").weekday() + 1) % 7  # Sunday = 0
            blocks.append((row, wi, day))
    for row, wi, day in sorted(blocks, key=lambda t: (t[0], t[1])):
        bx = x0 + wi * sx + (6 - row) * step
        by = ground - (6 - row) * step
        tip = f'<title>{day["count"]} contributions on {day["date"]}</title>'
        if not day["count"]:
            b += (f'<polygon points="{bx:.1f},{by} {bx + bw:.1f},{by} {bx + bw + ox:.1f},{by - ox} {bx + ox:.1f},{by - ox}" '
                  f'fill="#141c28">{tip}</polygon>')
            continue
        h = 4 + 58 * (day["count"] / top) ** .5
        front, roof, side = CITY[min(max(day["level"], 1), 4) - 1]
        t = by - h
        o = (f'<g class="growy" style="animation-delay:{.2 + wi * .025:.2f}s">{tip}'
             f'<rect x="{bx:.1f}" y="{t:.1f}" width="{bw}" height="{h:.1f}" fill="{front}"/>'
             f'<polygon points="{bx:.1f},{t:.1f} {bx + ox:.1f},{t - ox:.1f} {bx + bw + ox:.1f},{t - ox:.1f} {bx + bw:.1f},{t:.1f}" fill="{roof}"/>'
             f'<polygon points="{bx + bw:.1f},{t:.1f} {bx + bw + ox:.1f},{t - ox:.1f} {bx + bw + ox:.1f},{by - ox:.1f} {bx + bw:.1f},{by}" fill="{side}"/>')
        for wy in range(int(t + 3), int(by - 3), 5):
            for wx in (bx + 2, bx + 6):
                if rnd.random() < lit:
                    o += (f'<rect x="{wx:.1f}" y="{wy}" width="2" height="2" fill="{rnd.choice(colors)}" class="twinkle" '
                          f'style="animation-delay:{rnd.random() * 3:.1f}s;animation-duration:{3 + rnd.random() * 4:.1f}s"/>')
        if day["date"] == today:  # beacon on today's building
            o += f'<circle cx="{bx + bw / 2 + ox / 2:.1f}" cy="{t - ox - 3:.1f}" r="2.2" fill="#ff4d4d" class="pulse" filter="url(#glow)"/>'
        if day is peak:
            peak_xy = (bx + bw / 2 + ox / 2, t - ox)
        b += o + "</g>"

    if peak["count"]:
        px, py = peak_xy
        when = datetime.strptime(peak["date"], "%Y-%m-%d").strftime("%d %b")
        label = f'{peak["count"]} on {when}'
        b += (f'<g class="fade" {d(2)}><line x1="{px:.1f}" y1="{py - 4:.1f}" x2="{px:.1f}" y2="{py - 16:.1f}" stroke="{AMBER}" stroke-dasharray="2 2"/>'
              f'<text x="{px:.1f}" y="{py - 20:.1f}" text-anchor="middle" font-size="9.5" font-weight="700" fill="{AMBER}">{esc(label)}</text></g>')
    if fest in GROUND_FESTIVALS:
        b += festival_ground(fest, x0, ground + 18, len(weeks) * sx + 30, n=30)
    if monsoon:  # paper boats drifting along the flooded front street
        for i, (bx_, by_) in enumerate(((x0 + 160, ground - 3), (x0 + 420, ground - 12), (x0 + 600, ground - 5))):
            b += (f'<g class="fly" style="animation-duration:{38 + i * 9}s;animation-delay:{-i * 13}s">'
                  f'<path d="M{bx_ - 9},{by_ - 3}h18l-4,5h-10z" fill="#f2f5f9" stroke="#9aa6b8" stroke-width=".6"/>'
                  f'<path d="M{bx_ - 4},{by_ - 3}l4,-8 4,8z" fill="#ffffff" stroke="#9aa6b8" stroke-width=".6"/></g>')

    # the coding pet, on the empty lots at the front left
    idle = 0
    for day in reversed(days):
        if day["count"]:
            break
        idle += 1
    mood = "happy" if idle == 0 else "waiting" if idle == 1 else "sad" if idle < 7 else "sleeping"
    stage = "egg" if longest < 3 else "chick" if longest < 7 else "bird"
    px, pbase = x0 + 70, ground - 2
    line = PET_LINES[mood].format(days=idle)
    # a visitor's cookie (a "Feed Byte" issue) in the last day cheers Byte up
    if feeds and feeds["last_at"] and \
            (datetime.now(timezone.utc) - datetime.fromisoformat(feeds["last_at"].replace("Z", "+00:00"))).days < 1:
        mood, line = "happy", f"Thanks @{trunc(feeds['last_by'], 16)} for the cookie!"
    fed = f" · 🍪 fed {feeds['count']}×" if feeds and feeds["count"] else " · feed me 🍪"
    bw_ = len(line) * 5.3 + 18
    b += (f'<g class="pop" {d(1.6)}>{_pet(px, pbase, stage, mood)}'
          f'<rect x="{px + 22}" y="{pbase - 66}" width="{bw_:.0f}" height="20" rx="10" fill="#ffffff" fill-opacity=".92"/>'
          f'<path d="M{px + 30},{pbase - 47}l-6,8 12,-8z" fill="#ffffff" fill-opacity=".92"/>'
          f'<text x="{px + 22 + bw_ / 2:.0f}" y="{pbase - 52}" text-anchor="middle" font-size="9.5" font-weight="700" '
          f'fill="#1a0d02">{esc(line)}</text>'
          f'<text x="{px}" y="{pbase + 14}" text-anchor="middle" font-size="8" class="dim">'
          f'{esc(config.PET_NAME)} · {stage}{esc(fed)}</text></g>')

    b += synced(24, H - 12, right=False)
    note = FESTIVALS[fest][0] if fest else ""
    if weather:
        note = " · ".join(filter(None, [f'{weather["temp"]}°C, {weather["words"]}',
                                        f'AQI {weather["aqi"]} {weather["aqi_label"]}' if weather.get("aqi") is not None else "",
                                        note]))
    b += (f'<text x="826" y="{H - 12}" text-anchor="end" font-size="9.5" class="dim mono fade" {d(1.3)}>'
          f'{esc(" · ".join(filter(None, [phase_label(phase, user.get("location", "")), note])))}</text>')
    return svg(W, H, b, FESTIVAL_CSS + WEATHER_CSS, title="Contribution City", light=False)
