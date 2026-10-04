"""Cards driven by live GitHub data."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone

from .. import config
from ..github import featured, lang_color, time_ago
from .theme import (AMBER, BLUE, BORDER, CARD2, CYAN, GREEN, MUTED, ORANGE, TEXT, compact, d, dot, esc,
                    frame, heading, panel, svg, synced, trunc, wrap)

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

def timeline_opensource(user: dict, stats: dict, calendar: dict, n: int = 7) -> str:
    W, H = 850, 262
    b = frame(W, H)
    b += heading(24, 20, n, "Experience Timeline", "My learning, building and exploring journey.")
    items = config.TIMELINE[:5]
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


def analytics_exploring(user: dict, stats: dict, calendar: dict, n: int = 9) -> str:
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
    b += heading(546, 20, n + 1, "Currently Exploring", "Always learning, always building")
    for i, (label, pct) in enumerate(config.EXPLORING[:5]):
        y = 84 + i * 34
        b += (f'<g class="rise" {d(.3 + i * .12)}>' + dot(552, y - 4, 3.5, ORANGE, "") +
              f'<text x="562" y="{y}" font-size="11" fill="#c9d1d9">{esc(label)}</text>'
              f'<text x="826" y="{y}" text-anchor="end" font-size="10.5" class="mono" fill="{AMBER}">{pct}%</text>'
              f'<rect x="562" y="{y + 7}" width="264" height="6" rx="3" fill="#1d1712"/>'
              f'<rect x="562" y="{y + 7}" width="{264 * pct / 100:.0f}" height="6" rx="3" fill="url(#og)" class="grow" '
              f'filter="url(#glow)" {d(.5 + i * .15)}/></g>')
    return svg(W, H, b, title="GitHub Analytics & Currently Exploring")


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


def playground(repos: dict, api_base: str, n: int = 13) -> str:
    W, H = 850, 292
    b = frame(W, H) + heading(24, 20, n, "API Playground", "Live response from this profile's own API")
    for i, (m, path, desc) in enumerate(ENDPOINTS):
        y = 66 + i * 42
        active = i == 0
        b += (f'<g class="rise" {d(.2 + i * .08)}>' +
              panel(24, y, 250, 36, 8, stroke=ORANGE if active else BORDER, fill="#1a1109" if active else "url(#cardg)") +
              f'<rect x="34" y="{y + 10}" width="34" height="16" rx="4" fill="{GREEN}" fill-opacity=".18" stroke="{GREEN}"/>'
              f'<text x="51" y="{y + 21.5}" text-anchor="middle" font-size="8.5" font-weight="800" fill="{GREEN}">{m}</text>'
              f'<text x="76" y="{y + 16}" font-size="10.5" class="mono">{esc(path)}</text>'
              f'<text x="76" y="{y + 29}" font-size="8.8" class="muted">{esc(desc)}</text></g>')

    rx = 290
    b += panel(rx, 66, 536, 30, 7, fill="#0a0e15")
    b += (f'<text x="{rx + 12}" y="85" font-size="10.5" font-weight="800" fill="{GREEN}">GET</text>'
          f'<text x="{rx + 44}" y="85" font-size="10.5" class="mono">{esc(trunc(api_base.rstrip("/") + "/api/projects", 58))}</text>')
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
