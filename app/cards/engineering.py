"""Engineering showcase cards: architecture, backend, cloud, workflow, achievements.

Architecture, cloud and achievements read live GitHub data; the rest is config text.
"""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta, timezone

from .. import config
from .. import github as gh
from .live import _streaks
from .theme import (AMBER, BLUE, BORDER, CARD2, GREEN, ORANGE, bullet_list, compact, count_badge, cube, d, esc,
                    flow_line, frame, heading, panel, svg, synced, trunc, wrap)


def _box(x, y, w, h, title, lines=(), icon=True, delay=0.0, accent=ORANGE):
    o = f'<g class="rise" {d(delay)}>' + panel(x, y, w, h, 9, stroke=accent, extra='stroke-opacity=".55"')
    tx = x + 12
    if icon:
        o += f'<g class="float" style="animation-delay:{delay}s">{cube(x + 24, y + h / 2 - 2, 12)}</g>'
        tx = x + 44
    o += f'<text x="{tx}" y="{y + 20}" font-size="12" font-weight="700">{esc(title)}</text>'
    for i, line in enumerate(l for l in lines if l):
        o += f'<text x="{tx}" y="{y + 35 + i * 12}" font-size="9.5" class="muted">{esc(line)}</text>'
    return o + "</g>"


# ------------------------------------------------------- architecture

def _layer(tech: dict, cat: str, fallback, skip=()) -> list[str]:
    """Most used TECH_STACK items of a category and how many repos use any of them."""
    names = [name for name, _, _ in config.TECH_STACK.get(cat, []) if name not in skip]
    used = sorted((name for name in names if gh.tech_count(tech, name)), key=lambda nm: -gh.tech_count(tech, nm))
    if not used:
        return list(fallback)
    total = gh.tech_count(tech, *used)
    return [trunc(" / ".join(used[:2]), 22), f"used in {total} repo{'s' if total != 1 else ''}"]


def architecture(tech: dict, n: int = 6) -> str:
    A = config.ARCHITECTURE
    W, H = 850, 262
    A = {**A,
         "frontend": (A["frontend"][0], *_layer(tech, "Frontend", A["frontend"][1:])),
         "api": (A["api"][0], *_layer(tech, "Backend", A["api"][1:])),
         "database": (A["database"][0], *_layer(tech, "Database", A["database"][1:])),
         "cloud": (A["cloud"][0], *_layer(tech, "Cloud & DevOps", A["cloud"][1:], skip=("Git", "GitHub")))}
    b = frame(W, H) + heading(24, 20, n, "System Architecture", "My stack per layer, detected from my repositories.")
    # client (laptop)
    cx, cy = 66, 152
    b += f'<circle cx="{cx}" cy="{cy}" r="40" fill="{ORANGE}" fill-opacity=".12" filter="url(#softglow)" class="glowpulse"/>'
    b += f'<circle cx="{cx}" cy="{cy}" r="34" stroke="{ORANGE}" stroke-opacity=".6" stroke-dasharray="4 4" class="spin"/>'
    b += (f'<g class="pop"><rect x="{cx - 20}" y="{cy - 16}" width="40" height="26" rx="3" fill="#0d1a2b" stroke="{BLUE}"/>'
          f'<rect x="{cx - 16}" y="{cy - 12}" width="32" height="18" rx="1" fill="{BLUE}" opacity=".3"/>'
          f'<path d="M{cx - 26} {cy + 12}h52l-4 5h-44z" fill="#1d2b3e" stroke="{BLUE}"/></g>')
    b += (f'<text x="{cx}" y="{cy + 52}" text-anchor="middle" font-size="12" font-weight="700">{esc(A["client"][0])}</text>'
          f'<text x="{cx}" y="{cy + 65}" text-anchor="middle" font-size="9.5" class="muted">{esc(A["client"][1])}</text>')

    fx, ax, bw, bh, by = 140, 318, 150, 68, 118
    b += flow_line(f"M{cx + 36},{cy} L{fx},{cy}")
    b += _box(fx, by, bw, bh, A["frontend"][0], A["frontend"][1:], delay=.2)
    b += flow_line(f"M{fx + bw},{cy} L{ax},{cy}")
    b += _box(ax, by, bw, bh, A["api"][0], A["api"][1:], delay=.35)
    dx = 500
    b += flow_line(f"M{ax + bw},{cy - 8} C{ax + bw + 20},{cy - 8} {dx - 25},{98} {dx},{98}", dots=1)
    b += flow_line(f"M{ax + bw},{cy + 8} C{ax + bw + 20},{cy + 8} {dx - 25},{206} {dx},{206}", dots=1, color=BLUE)
    b += _box(dx, 66, 160, 64, A["database"][0], A["database"][1:], delay=.5)
    b += _box(dx, 174, 160, 64, A["cloud"][0], A["cloud"][1:], delay=.6, accent=BLUE)
    b += panel(676, 66, 150, 172, 10)
    b += bullet_list(686, 92, A["features"][:6], gap=26, size=9.8, delay=.6)
    b += synced(826, 252)
    return svg(W, H, b, title="System Architecture")


# ---------------------------------------------------- backend + database

def _cylinder(cx, top, w, h, color, delay):
    rx, ry = w / 2, 7
    return (f'<g class="pop" {d(delay)} filter="url(#glow)">'
            f'<path d="M{cx - rx},{top} v{h} a{rx},{ry} 0 0,0 {w},0 v{-h}" fill="{color}" fill-opacity=".18" stroke="{color}"/>'
            f'<ellipse cx="{cx}" cy="{top}" rx="{rx}" ry="{ry}" fill="{color}" fill-opacity=".45" stroke="{color}"/>'
            f'<path d="M{cx - rx},{top + h / 2} a{rx},{ry} 0 0,0 {w},0" stroke="{color}" stroke-opacity=".6"/></g>')


# Shown for the TECH_STACK "Database" items: kind, features.
DB_INFO = {
    "MongoDB": ("NoSQL Database", ["Documents", "Collections", "Aggregation"]),
    "PostgreSQL": ("Relational Database", ["Tables", "Relations", "Transactions"]),
    "MySQL": ("Relational Database", ["Tables", "Joins", "Transactions"]),
    "Redis": ("In-Memory Cache", ["Caching", "Session Storage", "Real-time Data"]),
    "SQLite": ("Embedded Database", ["Local Storage", "Zero Config", "Prototyping"]),
}


def backend_database(n: int = 14) -> str:
    W, H = 850, 286
    b = frame(W, H) + heading(24, 20, n, "Backend Engineering", "Robust, scalable and secure backend systems.")
    bw, bh = 108, 32
    xs = [30, 160, 290]
    r1, r2, r3 = 76, 146, 218
    for i, t in enumerate(("Request", "Authentication", "Validation")):
        b += _box(xs[i], r1, bw, bh, t, icon=False, delay=.1 + i * .1)
    b += flow_line(f"M{xs[0] + bw},{r1 + 16} L{xs[1]},{r1 + 16}", dots=1)
    b += flow_line(f"M{xs[1] + bw},{r1 + 16} L{xs[2]},{r1 + 16}", dots=1)
    b += flow_line(f"M{xs[2] + bw / 2},{r1 + bh} C{xs[2] + bw / 2},{r2 + 20} {xs[1] + bw + 30},{r2 + 20} {xs[1] + bw},{r2 + 20}", dots=1)
    b += _box(xs[1] - 20, r2, bw + 40, 42, "Business Logic", icon=True, delay=.45)
    b += flow_line(f"M{xs[1] + bw / 2 - 30},{r2 + 42} C{xs[1] + bw / 2 - 30},{r3 - 10} {xs[2] + bw / 2},{r3 - 20} {xs[2] + bw / 2},{r3}", dots=1)
    for i, t in enumerate(("Response", "Database", "Service Layer")):
        b += _box(xs[i], r3, bw, bh, t, icon=False, delay=.6 + (2 - i) * .1, accent=GREEN if t == "Response" else ORANGE)
    b += flow_line(f"M{xs[2]},{r3 + 16} L{xs[1] + bw},{r3 + 16}", dots=1)
    b += flow_line(f"M{xs[1]},{r3 + 16} L{xs[0] + bw},{r3 + 16}", dots=1, color=GREEN)

    b += f'<line x1="424" y1="22" x2="424" y2="{H - 22}" stroke="{BORDER}"/>'
    b += heading(440, 20, n + 1, "Database Architecture", "Multi-database architecture for flexible apps.")
    b += _box(573, 70, 120, 30, "Application", icon=False, delay=.2)
    dbs = [(name, *DB_INFO.get(name, ("Database", [])), color)
           for name, _, color in config.TECH_STACK.get("Database", [])][:3]
    for i, (name, kind, feats, color) in enumerate(dbs):
        cx = round(633 + (i - (len(dbs) - 1) / 2) * 130)
        b += flow_line(f"M633,100 C633,118 {cx},112 {cx},130", color=color, dots=1, dur=1.8)
        b += _cylinder(cx, 136, 54, 40, color, .4 + i * .15)
        b += (f'<g class="rise" {d(.6 + i * .15)}><text x="{cx}" y="200" text-anchor="middle" font-size="11.5" font-weight="700">{esc(name)}</text>'
              f'<text x="{cx}" y="213" text-anchor="middle" font-size="8.8" fill="{color}">{esc(kind)}</text>')
        for j, f in enumerate(feats):
            b += f'<text x="{cx}" y="{231 + j * 13}" text-anchor="middle" font-size="9" class="muted">{esc(f)}</text>'
        b += "</g>"
    return svg(W, H, b, title="Backend Engineering & Database Architecture")


# -------------------------------------------------------- cloud deploy

def _node_icon(kind, cx, cy):
    if kind == "laptop":
        return (f'<rect x="{cx - 14}" y="{cy - 11}" width="28" height="18" rx="2" stroke="{BLUE}" fill="{BLUE}" fill-opacity=".2"/>'
                f'<path d="M{cx - 18} {cy + 9}h36" stroke="{BLUE}" stroke-width="2"/>')
    if kind == "git":
        return (f'<rect x="{cx - 12}" y="{cy - 12}" width="24" height="24" rx="4" transform="rotate(45 {cx} {cy})" fill="#F05032"/>'
                f'<circle cx="{cx - 3}" cy="{cy - 4}" r="2.4" fill="#fff"/><circle cx="{cx + 4}" cy="{cy + 4}" r="2.4" fill="#fff"/>'
                f'<path d="M{cx - 3} {cy - 4}L{cx + 4} {cy + 4}" stroke="#fff" stroke-width="1.6"/>')
    if kind == "actions":
        return (f'<g class="spin" style="animation-duration:6s"><circle cx="{cx}" cy="{cy}" r="10" stroke="{BLUE}" stroke-width="5" stroke-dasharray="4 3.85"/></g>'
                f'<circle cx="{cx}" cy="{cy}" r="4" fill="{BLUE}"/>')
    if kind == "docker":
        o = ""
        for r, cols in ((0, 3), (1, 2)):
            for c in range(cols):
                o += f'<rect x="{cx - 12 + c * 8 + r * 4}" y="{cy - r * 8}" width="7" height="7" fill="#2496ED"/>'
        return o + f'<path d="M{cx - 16} {cy + 9}h32c-3 6-10 8-18 8s-12-4-14-8z" fill="#2496ED"/>'
    # aws / cloud
    return (f'<path d="M{cx - 14} {cy + 8}a7 7 0 0 1 1-14a10 10 0 0 1 19-1a7 7 0 0 1 8 15z" fill="#FF9900" fill-opacity=".25" stroke="#FF9900" stroke-width="1.6"/>'
            f'<text x="{cx + 1}" y="{cy + 5}" text-anchor="middle" font-size="7.5" font-weight="800" fill="#FF9900">aws</text>')


SERVICE_INFO = {
    "S3": "File Storage", "Lambda": "Serverless", "Amplify": "Hosting & CI/CD", "Cloudfront": "CDN",
    "EC2": "Virtual Server", "RDS": "Managed SQL", "DynamoDB": "NoSQL Store", "Vercel": "Hosting",
}


def cloud_deploy(tech: dict, n: int = 16) -> str:
    W, H = 850, 236
    b = frame(W, H) + heading(24, 20, n, "Cloud & Deployment", "From code to production · repo counts from GitHub.")
    nodes = [("laptop", "Local", "Development", 0),
             ("git", "Git", "Version Control", len(tech["repos"])),
             ("actions", "GitHub Actions", "CI/CD Pipeline", gh.tech_repos(tech, "github-actions")),
             ("docker", "Docker", "Containerization", gh.tech_count(tech, "Docker")),
             ("aws", "AWS", "Cloud Platform", gh.tech_count(tech, "AWS"))]
    cy = 110
    xs = [80 + i * 172 for i in range(len(nodes))]
    for i in range(len(nodes) - 1):
        b += flow_line(f"M{xs[i] + 30},{cy} L{xs[i + 1] - 30},{cy}", dur=1.6)
    for i, ((kind, t, s, repos), x) in enumerate(zip(nodes, xs)):
        b += (f'<g class="pop" {d(.15 + i * .15)}><circle cx="{x}" cy="{cy}" r="28" fill="{CARD2}" stroke="{ORANGE}" stroke-opacity=".6" filter="url(#glow)"/>'
              f'{_node_icon(kind, x, cy)}{count_badge(x + 21, cy - 21, repos, r=9)}</g>'
              f'<g class="rise" {d(.3 + i * .15)}><text x="{x}" y="{cy + 48}" text-anchor="middle" font-size="12" font-weight="700">{esc(t)}</text>'
              f'<text x="{x}" y="{cy + 62}" text-anchor="middle" font-size="9.5" class="muted">{esc(s)}</text></g>')
    # the remaining Cloud & DevOps items of TECH_STACK
    services = [(t, SERVICE_INFO.get(t, "Cloud Service"), color) for t, _, color in config.TECH_STACK.get("Cloud & DevOps", [])
                if t not in {"AWS", "Docker", "Git", "GitHub"}][:5]
    x = (W - len(services) * 142 + 12) / 2
    for i, (t, s, color) in enumerate(services):
        repos = gh.tech_count(tech, t)
        b += (f'<g class="rise" {d(1 + i * .1)}>' + panel(round(x), 192, 130, 30, 7) +
              f'<rect x="{x + 10:.0f}" y="200" width="14" height="14" rx="3" fill="{color}" fill-opacity=".25" stroke="{color}"/>'
              f'<text x="{x + 32}" y="205" font-size="10" font-weight="700">{esc(t)}</text>'
              f'<text x="{x + 32}" y="216" font-size="8.5" class="muted">{esc(s)}</text>')
        if repos:
            b += f'<text x="{x + 122}" y="205" text-anchor="end" font-size="9" font-weight="700" fill="{ORANGE}">{repos} repo{"s" if repos != 1 else ""}</text>'
        b += "</g>"
        x += 142
    return svg(W, H, b, title="Cloud & Deployment")


# ------------------------------------------------------------ workflow

def workflow(n: int = 17) -> str:
    W, H = 850, 178
    b = frame(W, H) + heading(24, 20, n, "Developer Workflow", "My development process from idea to production.")
    steps = config.WORKFLOW[:8]
    step = (W - 136) / (len(steps) - 1)
    cy = 98
    cycle = len(steps) * .6
    for i in range(len(steps) - 1):
        x = 68 + i * step
        b += f'<path d="M{x + 18:.0f},{cy} L{x + step - 18:.0f},{cy}" stroke="{ORANGE}" stroke-opacity=".5" class="flow"/>'
    for i, (t, s) in enumerate(steps):
        x = 68 + i * step
        hexa = " ".join(f"{x + 17 * c:.1f},{cy + 17 * s_:.1f}" for c, s_ in
                        ((0, -1), (.87, -.5), (.87, .5), (0, 1), (-.87, .5), (-.87, -.5)))
        b += (f'<g class="pop" {d(.1 + i * .1)}><polygon points="{hexa}" fill="#1a1109" stroke="{ORANGE}"/>'
              f'<polygon points="{hexa}" fill="{ORANGE}" class="step" filter="url(#glow)" '
              f'style="animation-delay:{i * .6:.1f}s;animation-duration:{cycle:.1f}s"/>'
              f'<text x="{x:.0f}" y="{cy + 4}" text-anchor="middle" font-size="11" font-weight="800" fill="{AMBER}">{i + 1}</text></g>'
              f'<g class="rise" {d(.3 + i * .1)}><text x="{x:.0f}" y="{cy + 38}" text-anchor="middle" font-size="11" font-weight="700">{esc(t)}</text>'
              f'<text x="{x:.0f}" y="{cy + 52}" text-anchor="middle" font-size="8.6" class="muted">{esc(s)}</text></g>')
    css = "@keyframes step{0%,100%{opacity:0}5%,14%{opacity:.45}24%{opacity:0}}.step{opacity:0;animation:step 4.8s ease-in-out infinite}"
    return svg(W, H, b, css, title="Developer Workflow")


# ----------------------------------------------------- problem -> solution

def problem_solution(n: int = 18) -> str:
    rows = config.PROBLEM_SOLUTION[:6]
    W, H = 850, 76 + len(rows) * 30 + 10
    b = frame(W, H) + heading(24, 20, n, "Problem → Solution", "Real world problems and how I solve them.")
    for i, (p, s) in enumerate(rows):
        y = 70 + i * 30
        b += (f'<g class="rise" {d(.15 + i * .1)}>' + panel(24, y, 802, 24, 6) +
              f'<circle cx="40" cy="{y + 12}" r="4" fill="#ff7b72"/>'
              f'<text x="52" y="{y + 16}" font-size="11" fill="#c9d1d9">{esc(p)}</text>'
              f'<path d="M300,{y + 12} L380,{y + 12}" stroke="{ORANGE}" class="flow"/>'
              f'<path d="M376,{y + 8} l6,4 -6,4" stroke="{ORANGE}" stroke-width="1.6" fill="none"/>'
              f'<circle cx="402" cy="{y + 12}" r="4" fill="{GREEN}" class="pulse"/>'
              f'<text x="414" y="{y + 16}" font-size="11" fill="{AMBER}">{esc(s)}</text></g>')
    return svg(W, H, b, title="Problem to Solution")


# --------------------------------------------------------- achievements

def _calendar_days(calendar: dict) -> list[dict]:
    return sorted((day for week in calendar["weeks"] for day in week), key=lambda x: x["date"])


def _badges(user: dict, repos: dict, stats: dict, calendar: dict, tech: dict) -> list[tuple]:
    """(name, glyph, colour, progress, target) for every badge; unlocked when progress >= target."""
    _, longest = _streaks(_calendar_days(calendar))
    return [
        ("First Commit", "✦", "#ff8c42", stats["commits"], 1),
        ("Solidity Dev", "◆", "#8c8cff", gh.tech_count(tech, "Solidity"), 1),
        ("Week Streak", "7", "#ff6a3d", longest, 7),
        ("Month Streak", "30", "#ff4d4d", longest, 30),
        ("Century", "100", "#58a6ff", stats["commits"], 100),
        ("Polyglot", "</>", "#3fb950", len(repos["languages"]), 5),
        ("First Star", "★", "#f0b72f", repos["total_stars"], 1),
        ("Open Sourcer", "PR", "#bc8cff", stats["prs"], 5),
    ]


def _badge_row(badges: list[tuple], y: float, W: int = 850) -> str:
    out = ""
    step = (W - 48) / len(badges)
    for i, (name, glyph, color, have, need) in enumerate(badges):
        cx = 24 + step * (i + .5)
        done = have >= need
        c = color if done else "#4a5566"
        glow, muted = (' filter="url(#glow)"', "") if done else ("", ' class="muted"')
        out += f'<g class="pop" {d(1 + i * .08)}>'
        out += (f'<circle cx="{cx:.0f}" cy="{y + 20}" r="19" fill="{c}" fill-opacity="{.18 if done else .08}" stroke="{c}" '
                f'stroke-width="1.6"{glow}/>'
                f'<text x="{cx:.0f}" y="{y + 20 + (5 if len(glyph) == 1 else 4)}" text-anchor="middle" '
                f'font-size="{14 if len(glyph) == 1 else 10.5}" font-weight="800" fill="{c}">{esc(glyph)}</text>')
        if not done:  # padlock
            out += (f'<rect x="{cx + 9:.0f}" y="{y + 29}" width="10" height="8" rx="1.5" fill="#56606c"/>'
                    f'<path d="M{cx + 11:.0f},{y + 29}v-2.5a3,3 0 0 1 6,0v2.5" stroke="#56606c" stroke-width="1.5"/>')
        out += f'<text x="{cx:.0f}" y="{y + 54}" text-anchor="middle" font-size="9.5" font-weight="700"{muted}>{esc(name)}</text>'
        if done:
            out += f'<text x="{cx:.0f}" y="{y + 67}" text-anchor="middle" font-size="8.5" fill="{GREEN}">✓ unlocked</text>'
        else:
            out += (f'<rect x="{cx - 24:.0f}" y="{y + 61}" width="48" height="4" rx="2" fill="#1d2633"/>'
                    f'<rect x="{cx - 24:.0f}" y="{y + 61}" width="{48 * min(have, need) / need:.0f}" height="4" rx="2" fill="{color}"/>'
                    f'<text x="{cx:.0f}" y="{y + 76}" text-anchor="middle" font-size="8" class="dim">{min(have, need)} / {need}</text>')
        out += "</g>"
    return out


def achievements(user: dict, repos: dict, stats: dict, calendar: dict, tech: dict, n: int = 18) -> str:
    created = datetime.fromisoformat(user["created_at"].replace("Z", "+00:00"))
    years = max(1, (datetime.now(timezone.utc) - created).days // 365)
    items = [
        (compact(repos["total_stars"]), "Stars Earned", "#ff8c42"),
        (compact(stats["commits"]), "Commits", "#58a6ff"),
        (compact(stats["prs"]), "Pull Requests", "#f0b72f"),
        (compact(calendar["total"]), "Contributions in last year", "#3fb950"),
        (compact(user["public_repos"]), "Public Repositories", "#ff6a3d"),
        (f"{years}+", "Years on GitHub", "#bc8cff"),
    ]
    badges = _badges(user, repos, stats, calendar, tech)
    unlocked = sum(1 for *_, have, need in badges if have >= need)
    W, H = 850, 292
    b = frame(W, H) + heading(24, 20, n, "GitHub Achievements", "Milestones, synced from my GitHub account")
    b += f'<line x1="24" y1="186" x2="826" y2="186" stroke="{BORDER}"/>'
    b += (f'<text x="24" y="204" font-size="11.5" font-weight="700">Badges</text>'
          f'<text x="80" y="204" font-size="10" class="muted">{unlocked} of {len(badges)} unlocked · '
          f'locked ones unlock themselves as I hit them</text>')
    b += _badge_row(badges, 208)
    b += synced(826, 40)
    step = (W - 48) / len(items)
    cy = 104
    for i, (value, label, color) in enumerate(items):
        cx = 24 + step * (i + .5)
        pts = " ".join(f"{cx + 28 * c:.1f},{cy + 28 * s:.1f}" for c, s in
                       ((0, -1), (.87, -.5), (.87, .5), (0, 1), (-.87, .5), (-.87, -.5)))
        inner = " ".join(f"{cx + 17 * c:.1f},{cy + 17 * s:.1f}" for c, s in
                         ((0, -1), (.87, -.5), (.87, .5), (0, 1), (-.87, .5), (-.87, -.5)))
        b += (f'<g class="pop" {d(.2 + i * .12)}>'
              f'<polygon points="{pts}" fill="{color}" fill-opacity=".18" filter="url(#softglow)" class="glowpulse" style="animation-delay:{i * .4}s"/>'
              f'<polygon points="{pts}" fill="{CARD2}" stroke="{color}" stroke-width="1.6" filter="url(#glow)"/>'
              f'<polygon points="{inner}" fill="{color}" fill-opacity=".2" stroke="{color}" stroke-opacity=".6"/>'
              f'<text x="{cx:.1f}" y="{cy + 4.5}" text-anchor="middle" font-size="{13 if len(value) <= 3 else 11}" font-weight="800" '
              f'fill="{color}">{esc(value)}</text></g>')
        for j, line in enumerate(wrap(label, 16, 2)):
            b += f'<text x="{cx:.0f}" y="{cy + 48 + j * 13}" text-anchor="middle" font-size="10.5" font-weight="600" class="rise" {d(.4 + i * .12)}>{esc(line)}</text>'
    return svg(W, H, b, title="GitHub Achievements")


# -------------------------------------------------------- year in review

def wrapped_season() -> bool:
    """1 Dec - 7 Jan (India time): the achievements card turns into the year in review."""
    today = (datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)).date()
    return today.month == 12 or (today.month == 1 and today.day <= 7)


def year_in_review(user: dict, repos: dict, stats: dict, calendar: dict, tech: dict, n: int = 18) -> str:
    today = (datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)).date()
    year = str(today.year if today.month == 12 else today.year - 1)
    days = [day for day in _calendar_days(calendar) if day["date"].startswith(year)]
    total = sum(day["count"] for day in days)
    months = Counter()
    for day in days:
        months[day["date"][5:7]] += day["count"]
    busiest = datetime.strptime(max(months, key=months.get), "%m").strftime("%B") if total else "—"
    _, longest = _streaks(days)
    best = max(days, key=lambda x: x["count"]) if total else None
    new_repos = [r for r in repos["repos"] if (r.get("created_at") or "").startswith(year)]
    before = {r["language"] for r in repos["repos"] if r["language"] and (r.get("created_at") or "") < year}
    new_langs = sorted({r["language"] for r in new_repos if r["language"]} - before)
    top_repo = stats["top_repos"][0][0] if stats["top_repos"] else "—"

    W, H = 850, 292
    b = frame(W, H)
    import random
    rnd = random.Random(int(year))
    for _ in range(40):  # confetti
        b += (f'<rect x="{rnd.random() * W:.0f}" y="{rnd.random() * H:.0f}" width="4" height="7" rx="1" '
              f'fill="{rnd.choice([ORANGE, AMBER, GREEN, BLUE, "#bc8cff", "#ff4fa3"])}" fill-opacity=".5" '
              f'transform="rotate({rnd.randint(0, 90)} {rnd.random() * W:.0f} {rnd.random() * H:.0f})" class="twinkle" '
              f'style="animation-delay:{rnd.random() * 3:.1f}s"/>')
    b += heading(24, 20, n, f"My {year} Wrapped", "My year on GitHub, in review")
    b += (f'<text x="826" y="54" text-anchor="end" font-size="40" font-weight="900" fill="url(#og)" filter="url(#glow)" '
          f'class="pop" {d(.2)}>{year}</text>')
    tiles = [(f"{total:,}", "contributions"), (busiest, "busiest month"), (f"{longest} days", "longest streak"),
             (str(best["count"]) if best else "0", f"best day · {datetime.strptime(best['date'], '%Y-%m-%d'):%d %b}" if best else "best day"),
             (str(len(new_repos)), "new repositories"), (trunc(top_repo, 16), "most commits went to"),
             (", ".join(new_langs[:3]) or "—", "new languages"), (str(stats["prs"]), "pull requests")]
    for i, (value, label) in enumerate(tiles):
        col, row = i % 4, i // 4
        x, y = 24 + col * 202, 80 + row * 100
        b += (f'<g class="rise" {d(.3 + i * .1)}>' + panel(x, y, 194, 88, 10) +
              f'<text x="{x + 16}" y="{y + 44}" font-size="{22 if len(value) <= 10 else 15}" font-weight="800" fill="url(#og)">{esc(value)}</text>'
              f'<text x="{x + 16}" y="{y + 68}" font-size="10.5" class="muted">{esc(label)}</text></g>')
    b += synced(24, H - 10, right=False)
    b += f'<text x="826" y="{H - 10}" text-anchor="end" font-size="9.5" class="dim">back to achievements on 8 January</text>'
    return svg(W, H, b, title=f"{year} Wrapped")

