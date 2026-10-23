"""Desi cards: Tech Thali, Desi Dev Corner (rashifal, chai-o-meter, commit mood ring), the Rajdhani
Express of my repos, the Report Card, the Commit Premier League, the Delhi Metro map and Dainik Commit."""

from __future__ import annotations

import hashlib
import math
from collections import Counter
from datetime import datetime, timedelta, timezone

from .. import config
from ..github import lang_color
from .theme import (AMBER, BLUE, BORDER, CYAN, GREEN, ORANGE, TEXT, WEATHER_CSS, compact, d, dot, esc, frame, heading,
                    panel, svg, synced, trunc, wrap)


def _ist() -> datetime:
    return datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)


def _days(calendar: dict) -> list[dict]:
    return sorted((day for week in calendar["weeks"] for day in week), key=lambda x: x["date"])


# ------------------------------------------------------------ tech thali

# what each language is served as, biggest first
DISHES = ["Dal Makhani", "Paneer Masala", "Jeera Rice", "Boondi Raita", "Butter Roti", "Aam ka Achaar", "Gulab Jamun"]


def _size(n: int, exact: bool) -> str:
    if not exact:
        return f"{n} repo{'s' if n != 1 else ''}"
    for unit, step in (("MB", 1 << 20), ("KB", 1 << 10)):
        if n >= step:
            return f"{n / step:.1f} {unit}".replace(".0 ", " ")
    return f"{n} B"


def _katori(cx, cy, r, color, label, delay) -> str:
    """A steel bowl seen from above, filled with the language's colour."""
    gid = f"curry{int(cx)}{int(cy)}"
    return (f'<g class="pop" {d(delay)}>'
            f'<defs><radialGradient id="{gid}" cx=".38" cy=".35" r=".75"><stop offset="0" stop-color="#ffffff" stop-opacity=".35"/>'
            f'<stop offset=".45" stop-color="{color}" stop-opacity="0"/></radialGradient></defs>'
            f'<circle cx="{cx}" cy="{cy + 2}" r="{r + 1}" fill="#000000" fill-opacity=".35"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#c3cad8" stroke="#8b949e" stroke-width="1"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r - 3:.1f}" fill="{color}"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r - 3:.1f}" fill="url(#{gid})"/>'
            f'<text x="{cx}" y="{cy + 3.5}" text-anchor="middle" font-size="{max(8, min(12, r * .5)):.1f}" font-weight="800" '
            f'fill="#ffffff" stroke="#000000" stroke-opacity=".45" stroke-width="2" paint-order="stroke">{esc(label)}</text></g>')


def _short(lang: str) -> str:
    return {"JavaScript": "JS", "TypeScript": "TS", "Python": "Py", "Solidity": "Sol", "Jupyter Notebook": "Nb",
            "Dockerfile": "Dk", "Shell": "Sh", "HTML": "HT"}.get(lang, lang[:3])


def tech_thali(tech: dict, repos: dict, n: int | None = None) -> str:
    """My languages as a thali: each katori sized by how much code I've written in it."""
    W, H = 850, 290
    b = frame(W, H)
    exact = tech.get("exact", False)
    sizes = Counter(tech.get("bytes") or {}) or Counter(dict(repos["languages"]))
    b += heading(24, 20, n, "Tech Thali",
                 "My languages served up, each katori sized by " + ("the code I've written in it" if exact else "the repos using it"))
    items = sizes.most_common(len(DISHES))
    if not items:
        b += f'<text x="{W / 2}" y="160" text-anchor="middle" font-size="13" class="muted">The kitchen is warming up…</text>'
        return svg(W, H, b, title="Tech Thali")
    total = sum(sizes.values())
    top = items[0][1]

    # the steel plate
    cx, cy, R = 200, 172, 104
    b += (f'<circle cx="{cx}" cy="{cy + 6}" r="{R + 4}" fill="#000000" fill-opacity=".3" filter="url(#softglow)"/>'
          f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="#9aa6b8" stroke="#c3cad8" stroke-width="2"/>'
          f'<circle cx="{cx}" cy="{cy}" r="{R - 9}" fill="#7d8899"/>'
          f'<circle cx="{cx}" cy="{cy}" r="{R - 9}" fill="none" stroke="#ffffff" stroke-opacity=".18" stroke-width="2" '
          f'stroke-dasharray="40 260" class="spin" style="animation-duration:14s"/>')
    lang, size = items[0]
    b += _katori(cx, cy, 20 + 14 * (size / top) ** .5, lang_color(lang), _short(lang), .3)
    ring = items[1:]
    for i, (lang, size) in enumerate(ring):
        a = math.radians(-90 + i * 360 / max(len(ring), 1))
        r = 11 + 13 * (size / top) ** .5
        b += _katori(cx + 64 * math.cos(a), cy + 64 * math.sin(a), r, lang_color(lang), _short(lang), .45 + i * .1)
    # steam over the main dish
    b += "".join(f'<path d="M{cx - 8 + k * 8},{cy - 30} q-5,-8 0,-14 q5,-7 0,-14" stroke="#ffffff" stroke-opacity=".55" '
                 f'stroke-width="2" stroke-linecap="round" class="smoke" style="animation-delay:{k * .9:.1f}s"/>' for k in range(3))

    # the menu
    mx = 360
    b += (f'<g class="rise" {d(.25)}><text x="{mx}" y="84" font-size="11" font-weight="700" fill="{AMBER}" letter-spacing="2">'
          f'TODAY\'S MENU</text><line x1="{mx}" y1="92" x2="826" y2="92" stroke="{BORDER}" stroke-dasharray="3 4"/></g>')
    for i, (lang, size) in enumerate(items):
        y = 112 + i * 22
        share = size / total
        b += (f'<g class="rise" {d(.35 + i * .07)}>'
              f'<circle cx="{mx + 6}" cy="{y - 4}" r="5" fill="{lang_color(lang)}"/>'
              f'<text x="{mx + 18}" y="{y}" font-size="11.5" font-weight="700" fill="#c9d1d9">{esc(DISHES[i])}</text>'
              f'<text x="{mx + 130}" y="{y}" font-size="10.5" class="muted">{esc(lang)}</text>'
              f'<rect x="{mx + 250}" y="{y - 9}" width="150" height="7" rx="3.5" fill="#1d1712"/>'
              f'<rect x="{mx + 250}" y="{y - 9}" width="{max(4, 150 * share):.0f}" height="7" rx="3.5" fill="{lang_color(lang)}" '
              f'class="grow" {d(.6 + i * .08)}/>'
              f'<text x="826" y="{y}" text-anchor="end" font-size="10" class="mono ink" fill="{AMBER}">{share * 100:.0f}%</text>'
              f'<title>{esc(lang)}: {_size(size, exact)}</title></g>')
    first, second = items[0][0], (items[1][0] if len(items) > 1 else "")
    special = f"Chef's special: {first} {DISHES[0].split()[0].lower()}" + (f", with a side of {second}" if second else "")
    b += (f'<text x="{mx}" y="{H - 34}" font-size="11" font-style="italic" fill="#c9d1d9" class="fade" {d(1.2)}>'
          f'🍛 {esc(special)}</text>')
    b += synced(826, H - 12)
    return svg(W, H, b, WEATHER_CSS, title="Tech Thali")


# ----------------------------------------------------- desi dev corner

# sidereal sun signs (the rashi a birthday falls in), by start date
RASHIS = [("01-14", "Makara", "♑"), ("02-13", "Kumbha", "♒"), ("03-14", "Meena", "♓"), ("04-14", "Mesha", "♈"),
          ("05-15", "Vrishabha", "♉"), ("06-15", "Mithuna", "♊"), ("07-17", "Karka", "♋"), ("08-17", "Simha", "♌"),
          ("09-17", "Kanya", "♍"), ("10-17", "Tula", "♎"), ("11-16", "Vrishchika", "♏"), ("12-16", "Dhanu", "♐")]

PREDICTIONS = [
    "Shukra sits in your main branch today: merges go smoothly and reviewers smile.",
    "Mangal is in the house of node_modules. Delete it, reinstall, and peace returns.",
    "Shani is watching your CI. Write the test first, then push with confidence.",
    "Guru blesses your {lang} today. Your cleanest code of the week is waiting there.",
    "Budh is strong: a good day to refactor {repo} and name things properly.",
    "Chandra is in your terminal. That bug? It is a missing comma, look closely.",
    "Rahu lurks in production. Avoid deploying after 6 PM, and never on a Friday.",
    "Ketu hides your keys. Check .env before you blame the API.",
    "Surya shines on {repo}. Ship that feature, the stars are aligned (and starred).",
    "Your stars say: one commit a day keeps the Byte pet happy and the streak alive.",
]


def _rashi() -> tuple[str, str]:
    md = config.BIRTHDAY or "01-01"
    name, sym = RASHIS[-1][1:]
    for start, n_, s in RASHIS:
        if md >= start:
            name, sym = n_, s
    return name, sym


# commit-message mood: (name, emoji, colour, words that start the message or appear in it)
MOODS = [
    ("Shipping", "🚀", ORANGE, ("feat", "add", "new", "create", "implement", "launch", "release", "build")),
    ("Bug hunting", "🐛", "#ff5e5e", ("fix", "bug", "error", "issue", "crash", "patch", "resolve", "hotfix")),
    ("Cleaning", "🧹", CYAN, ("refactor", "clean", "remove", "rename", "move", "delete", "simplif", "chore")),
    ("Writing", "📝", BLUE, ("doc", "readme", "comment", "typo", "guide")),
    ("Polishing", "✨", "#bc8cff", ("style", "ui", "css", "design", "theme", "update", "improve", "tweak")),
    ("Experiments", "🧪", GREEN, ("wip", "test", "try", "experiment", "init", "initial", "setup", "first")),
]


def _mood_of(message: str) -> int | None:
    words = message.lower().replace(":", " ").replace("(", " ").split()
    for i, (_, _, _, keys) in enumerate(MOODS):
        if any(w.startswith(k) for w in words[:3] for k in keys):
            return i
    return None


def _donut(cx, cy, r, parts: list[tuple[float, str]], width=12) -> str:
    circ = 2 * math.pi * r
    out, at = f'<circle cx="{cx}" cy="{cy}" r="{r}" stroke="#1d2633" stroke-width="{width}"/>', 0.0
    for i, (share, color) in enumerate(parts):
        out += (f'<circle cx="{cx}" cy="{cy}" r="{r}" stroke="{color}" stroke-width="{width}" '
                f'stroke-dasharray="{max(share * circ - 2, .1):.1f} {circ:.1f}" stroke-dashoffset="{-at * circ:.1f}" '
                f'transform="rotate(-90 {cx} {cy})" class="fade" {d(.5 + i * .12)}/>')
        at += share
    return out


def desi_corner(user: dict, calendar: dict, commits: list[dict], repos: dict, n: int | None = None) -> str:
    """Aaj ka rashifal written from my commits, the chai my week of code took, and the mood of my commit messages."""
    W, H = 850, 300
    b = frame(W, H)
    b += heading(24, 20, n, "Desi Dev Corner", "Aaj ka rashifal, the chai-o-meter and the mood of my commits · all live")
    now = _ist()
    by_name = {r["name"]: r for r in repos["repos"]}

    # ---- rashifal
    x, y, w, h = 24, 70, 330, 206
    name, sym = _rashi()
    seed = int(hashlib.md5(f"{now:%Y-%m-%d}{user['login']}".encode()).hexdigest(), 16)
    recent = [c for c in commits if c["repo"] in by_name][:30]
    langs = Counter(by_name[c["repo"]]["language"] for c in recent if by_name[c["repo"]]["language"])
    lang = (sorted(langs)[seed % len(langs)] if langs else
            (repos["languages"][0][0] if repos["languages"] else "Python"))
    repo = recent[seed % len(recent)]["repo"] if recent else (repos["repos"][0]["name"] if repos["repos"] else "my next repo")
    hours = Counter(int(c["date"][11:13]) for c in commits)
    peak = max(range(24), key=lambda hh: hours[hh]) if hours else 21
    lines = wrap(PREDICTIONS[seed % len(PREDICTIONS)].format(lang=lang, repo=repo), 50, 3)
    b += f'<g class="rise" {d(.3)}>' + panel(x, y, w, h, 10)
    b += (f'<text x="{x + 16}" y="{y + 30}" font-size="26" fill="{AMBER}" filter="url(#glow)">{sym}</text>'
          f'<text x="{x + 50}" y="{y + 22}" font-size="13.5" font-weight="800">{esc(name)} Rashi</text>'
          f'<text x="{x + 50}" y="{y + 37}" font-size="9.5" class="muted">Aaj ka rashifal · {now:%d %b %Y}</text>')
    b += "".join(f'<text x="{x + 16}" y="{y + 64 + i * 16}" font-size="11" font-style="italic" fill="#c9d1d9">'
                 f'{"“" if i == 0 else ""}{esc(t)}{"”" if i == len(lines) - 1 else ""}</text>' for i, t in enumerate(lines))
    lucky = [("Lucky language", lang, lang_color(lang)),
             ("Shubh muhurat to push", f"{peak % 12 or 12}:00 {'AM' if peak < 12 else 'PM'}", AMBER),
             ("Lucky repo", trunc(repo, 22), AMBER)]
    for i, (k, v, color) in enumerate(lucky):
        yy = y + 128 + i * 22
        b += (dot(x + 20, yy - 4, 3, color, "") + f'<text x="{x + 30}" y="{yy}" font-size="10" class="muted">{k}</text>'
              f'<text x="{x + w - 16}" y="{yy}" text-anchor="end" font-size="10.5" font-weight="700" fill="{color}">{esc(v)}</text>')
    b += "</g>"

    # ---- chai-o-meter
    x, w = 366, 220
    days = _days(calendar)
    week = sum(day["count"] for day in days[-7:])
    since = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()[:10]
    late = sum(1 for c in commits if c["date"][:10] >= since and (int(c["date"][11:13]) >= 22 or int(c["date"][11:13]) < 5))
    cups = math.ceil(week / 2) + late
    level = min(1.0, cups / 20)
    label = "Cutting chai" if cups < 5 else "Masala chai mode" if cups < 12 else "Kettle on full"
    b += f'<g class="rise" {d(.4)}>' + panel(x, y, w, h, 10)
    b += (f'<text x="{x + 16}" y="{y + 22}" font-size="13.5" font-weight="800">Chai-o-meter</text>'
          f'<text x="{x + 16}" y="{y + 37}" font-size="9.5" class="muted">cups my last 7 days of code took</text>')
    kx, ky, kw, kh = x + 22, y + 80, 74, 84  # the kulhad
    shape = f'M{kx},{ky} h{kw} l-10,{kh} h{-(kw - 20)} z'
    b += (f'<defs><clipPath id="kulhad"><path d="{shape}"/></clipPath></defs>'
          f'<path d="{shape}" fill="#5a2a14"/>'
          f'<g clip-path="url(#kulhad)"><rect x="{kx}" y="{ky + kh * (1 - level) + 4:.1f}" width="{kw}" height="{kh}" '
          f'fill="#c68642" class="growy" {d(.8)}/>'
          f'<rect x="{kx}" y="{ky + kh * (1 - level) + 4:.1f}" width="{kw}" height="3" fill="#e0b080" class="growy" {d(.8)}/></g>'
          f'<path d="{shape}" stroke="#b5562b" stroke-width="2.5"/>'
          f'<ellipse cx="{kx + kw / 2}" cy="{ky}" rx="{kw / 2}" ry="5" fill="#3a1d0c" stroke="#b5562b" stroke-width="2"/>'
          f'<path d="M{kx + 6},{ky + 16} h{kw - 12}" stroke="#d9480f" stroke-opacity=".6" stroke-width="2"/>')
    b += "".join(f'<path d="M{kx + 22 + k * 15},{ky - 8} q-6,-9 0,-16 q6,-8 0,-16" stroke="#ffffff" stroke-opacity=".6" '
                 f'stroke-width="2" stroke-linecap="round" class="smoke" style="animation-delay:{k * 1.1:.1f}s"/>' for k in range(3))
    tx = x + 112
    b += (f'<text x="{tx}" y="{y + 92}" font-size="30" font-weight="800" fill="url(#og)">{cups}</text>'
          f'<text x="{tx}" y="{y + 108}" font-size="10" fill="#c9d1d9">cup{"s" if cups != 1 else ""} of chai ☕</text>'
          f'<text x="{tx}" y="{y + 130}" font-size="10.5" font-weight="700" fill="{AMBER}">{label}</text>'
          f'<text x="{tx}" y="{y + 146}" font-size="9" class="muted">{week} contribution{"s" if week != 1 else ""}</text>'
          f'<text x="{tx}" y="{y + 159}" font-size="9" class="muted">{late} after 10 PM</text>'
          f'<text x="{x + w / 2}" y="{y + h - 12}" text-anchor="middle" font-size="8.5" class="dim">'
          f'1 cup per 2 contributions, +1 per late-night commit</text>')
    b += "</g>"

    # ---- commit mood ring
    x, w = 598, 228
    cutoff = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()[:10]
    sample = [c for c in commits if c["date"][:10] >= cutoff and c.get("message")] or \
             [c for c in commits if c.get("message")][:40]
    moods = Counter(m for m in (_mood_of(c["message"]) for c in sample) if m is not None)
    b += f'<g class="rise" {d(.5)}>' + panel(x, y, w, h, 10)
    b += (f'<text x="{x + 16}" y="{y + 22}" font-size="13.5" font-weight="800">Commit Mood Ring</text>'
          f'<text x="{x + 16}" y="{y + 37}" font-size="9.5" class="muted">read from my last {len(sample)} commit messages</text>')
    rcx, rcy = x + 54, y + 108
    if moods:
        total = sum(moods.values())
        top = moods.most_common()
        mood, emoji, color, _ = MOODS[top[0][0]]
        b += (f'<circle cx="{rcx}" cy="{rcy}" r="34" fill="{color}" fill-opacity=".18" filter="url(#softglow)" class="glowpulse"/>'
              + _donut(rcx, rcy, 36, [(cnt / total, MOODS[i][2]) for i, cnt in top]) +
              f'<circle cx="{rcx}" cy="{rcy}" r="21" fill="{color}" fill-opacity=".22" stroke="{color}" filter="url(#glow)"/>'
              f'<text x="{rcx}" y="{rcy + 7}" text-anchor="middle" font-size="20">{emoji}</text>')
        b += (f'<text x="{x + 16}" y="{y + 176}" font-size="12.5" font-weight="800" fill="{color}">{mood} week</text>'
              f'<text x="{x + 16}" y="{y + 191}" font-size="9" class="muted">{round(100 * top[0][1] / total)}% of my commits</text>')
        for i, (mi, cnt) in enumerate(top[:4]):
            yy = y + 78 + i * 18
            m_name, m_emoji, m_color, _ = MOODS[mi]
            b += (dot(x + 108, yy - 3.5, 3, m_color, "") +
                  f'<text x="{x + 116}" y="{yy}" font-size="9" fill="#c9d1d9">{m_emoji} {esc(m_name)}</text>'
                  f'<text x="{x + w - 12}" y="{yy}" text-anchor="end" font-size="9" font-weight="700" fill="{m_color}">'
                  f'{round(100 * cnt / total)}%</text>')
    else:
        b += (f'<circle cx="{rcx}" cy="{rcy}" r="36" stroke="#1d2633" stroke-width="12"/>'
              f'<text x="{x + w / 2}" y="{y + 180}" text-anchor="middle" font-size="10" class="muted">No commit messages yet</text>')
    b += "</g>"
    b += synced(826, H - 8)
    return svg(W, H, b, WEATHER_CSS, title="Desi Dev Corner")


# ------------------------------------------------------ rajdhani express

TRAIN_CSS = (
    "@keyframes arrive{from{transform:translateX(-880px)}to{transform:translateX(0)}}"
    ".arrive{animation:arrive 3.2s cubic-bezier(.2,.7,.25,1) both}"
    "@keyframes passby{from{transform:translateX(0)}to{transform:translateX(-60px)}}"
    ".passby{animation:passby 1.2s linear infinite}"
    "@keyframes rock{0%,100%{transform:translateY(0)}50%{transform:translateY(-.8px)}}"
    ".rock{animation:rock .5s ease-in-out infinite}"
)
RED, CREAM = "#b3261e", "#f3e9d2"


def _wheels(x0, w, y) -> str:
    return "".join(f'<g class="spin" style="animation-duration:.7s"><circle cx="{cx}" cy="{y}" r="5" fill="#1d2633" stroke="#8b949e" '
                   f'stroke-width="1.2"/><path d="M{cx - 4},{y}h8M{cx},{y - 4}v8" stroke="#8b949e" stroke-width=".9"/></g>'
                   for cx in (x0 + 12, x0 + 24, x0 + w - 24, x0 + w - 12))


def rajdhani(repos: dict, n: int | None = None) -> str:
    """My repos as the coaches of a train: the most recently pushed one rides right behind the engine."""
    W, H = 850, 190
    b = frame(W, H)
    b += heading(24, 20, n, "Rajdhani Express", "Every coach is one of my repos · the freshest push rides behind the engine")
    coaches = sorted(repos["repos"], key=lambda r: r["pushed_at"] or "", reverse=True)[:7]
    rail = 156
    # scenery rushing past: poles and sleepers
    b += ('<g class="passby">' + "".join(f'<rect x="{x}" y="{rail + 3}" width="12" height="4" rx="1" fill="#2b1d12"/>'
                                         for x in range(0, W + 60, 20)) + "</g>")
    b += (f'<rect x="1" y="{rail}" width="{W - 2}" height="2.5" fill="#8b949e"/>'
          f'<rect x="1" y="{rail + 8}" width="{W - 2}" height="2" fill="#56606c"/>')
    b += ('<g class="passby" style="animation-duration:2.4s">' +
          "".join(f'<path d="M{x},{rail - 92}v{92 - 4}M{x - 6},{rail - 88}h12" stroke="#2b3646" stroke-width="2"/>'
                  for x in range(30, W + 60, 120)) + "</g>")

    train = ""
    ex = 734  # the engine, facing right
    train += (f'<path d="M{ex},{rail - 52} h62 q30,0 30,30 v12 h-92z" fill="{RED}" stroke="#7a1712"/>'
              f'<rect x="{ex}" y="{rail - 32}" width="92" height="7" fill="{CREAM}"/>'
              f'<rect x="{ex + 8}" y="{rail - 46}" width="22" height="12" rx="2" fill="#a5d6ff" fill-opacity=".85"/>'
              f'<path d="M{ex + 64},{rail - 48} h4 q20,2 22,20 h-26z" fill="#a5d6ff" fill-opacity=".85"/>'
              f'<circle cx="{ex + 89}" cy="{rail - 16}" r="3" fill="#fff3c4" filter="url(#glow)" class="pulse"/>'
              f'<rect x="{ex + 40}" y="{rail - 62}" width="9" height="10" fill="#46200b"/>'
              f'<text x="{ex + 46}" y="{rail - 15}" text-anchor="middle" font-size="7" font-weight="800" fill="{CREAM}">'
              f'{esc(trunc(config.GITHUB_USERNAME.upper(), 12))}</text>' + _wheels(ex, 92, rail - 5))
    train += "".join(f'<circle cx="{ex + 44}" cy="{rail - 66}" r="{3 + k}" fill="#c9d1d9" fill-opacity=".5" class="smoke" '
                     f'style="animation-delay:{k * .8:.1f}s"/>' for k in range(4))
    for i, r in enumerate(coaches):
        cw = 92
        cx = ex - 6 - (i + 1) * (cw + 6)
        if cx < 8:
            break
        top = rail - 50
        win = "".join(f'<rect x="{cx + 8 + k * 14}" y="{top + 8}" width="9" height="8" rx="1.5" fill="#a5d6ff" fill-opacity=".75"/>'
                      for k in range(6))
        train += (f'<g><title>{esc(r["name"])}{" — " + esc(r["description"]) if r["description"] else ""}</title>'
                  f'<rect x="{cx + cw}" y="{rail - 32}" width="6" height="4" fill="#56606c"/>'
                  f'<rect x="{cx}" y="{top}" width="{cw}" height="40" rx="4" fill="{RED}" stroke="#7a1712"/>'
                  f'<rect x="{cx + 2}" y="{top - 4}" width="{cw - 4}" height="5" rx="2" fill="#5c1410"/>'
                  f'{win}<rect x="{cx}" y="{top + 20}" width="{cw}" height="3" fill="{r["color"]}"/>'
                  f'<rect x="{cx}" y="{top + 24}" width="{cw}" height="13" fill="{CREAM}"/>'
                  f'<text x="{cx + cw / 2}" y="{top + 33.5}" text-anchor="middle" font-size="7.5" font-weight="800" '
                  f'fill="#5c1410">{esc(trunc(r["name"], 17))}</text>'
                  f'<text x="{cx + 4}" y="{top - 7}" font-size="7" font-weight="700" fill="{AMBER}">C{i + 1}</text>'
                  f'<text x="{cx + cw - 4}" y="{top - 7}" text-anchor="end" font-size="7" class="muted">'
                  f'{"★ " + compact(r["stars"]) + " · " if r["stars"] else ""}{esc(r["language"] or "—")}</text>'
                  + _wheels(cx, cw, rail - 5) + "</g>")
    b += f'<g class="arrive"><g class="rock">{train}</g></g>'
    newest = coaches[0]["name"] if coaches else ""
    b += (f'<text x="24" y="{H - 10}" font-size="9.5" class="dim mono fade" {d(3)}>'
          f'{"C1 " + esc(trunc(newest, 30)) + " was pushed most recently · " if newest else ""}'
          f'{len(repos["repos"])} coaches in the yard</text>')
    b += synced(826, H - 10)
    return svg(W, H, b, TRAIN_CSS + WEATHER_CSS, title="Rajdhani Express")


# ------------------------------------------------------------ report card

DAILY_GOAL = 3  # contributions a day that earn full marks for output
GRADES = [(90, "A+", GREEN), (80, "A", GREEN), (70, "B+", CYAN), (60, "B", BLUE), (50, "C", AMBER), (35, "D", ORANGE),
          (0, "F", "#ff7b72")]
REMARKS = {"A+": "Shabash! Class topper 🏆", "A": "Bahut badhiya, keep it up", "B+": "Accha hai, thoda aur push karo",
           "B": "Theek hai, consistency badhao", "C": "Mehnat ki zaroorat hai", "D": "Parents ko bulao 😅",
           "F": "Kal se pakka padhai? 📚"}


def _grade(score: float) -> tuple[str, str]:
    return next((g, color) for limit, g, color in GRADES if score >= limit)


def _streak(days: list[dict]) -> int:
    best = run = 0
    for day in days:
        run = run + 1 if day["count"] else 0
        best = max(best, run)
    return best


def _term(days: list[dict], streak_target: int) -> dict:
    """Marks for one term: attendance (days I coded), output (vs DAILY_GOAL a day) and longest streak."""
    n = max(len(days), 1)
    total, active, streak = sum(day["count"] for day in days), sum(1 for day in days if day["count"]), _streak(days)
    marks = {"attendance": 100 * active / n, "output": min(100.0, 100 * total / n / DAILY_GOAL),
             "streak": min(100.0, 100 * streak / max(min(streak_target, n), 1))}
    overall = .4 * marks["attendance"] + .35 * marks["output"] + .25 * marks["streak"]
    return {"total": total, "active": active, "n": len(days), "streak": streak, "marks": marks, "overall": overall}


def report_card(user: dict, calendar: dict, n: int | None = None) -> str:
    """Weekly, monthly and yearly grades from my contribution calendar, like a school report card."""
    W, H = 850, 300
    b = frame(W, H)
    days = _days(calendar)
    today = days[-1]["date"] if days else _ist().strftime("%Y-%m-%d")
    y0, mo = int(today[:4]), int(today[5:7])
    session = f"{y0}–{(y0 + 1) % 100:02d}" if mo >= 4 else f"{y0 - 1}–{y0 % 100:02d}"
    b += heading(24, 20, n, "Report Card", f"GitHub Public School, Noida · Session {session} · graded live from my contributions")
    b += (f'<text x="826" y="34" text-anchor="end" font-size="10" class="muted">Roll no.</text>'
          f'<text x="826" y="50" text-anchor="end" font-size="12" font-weight="800" class="mono" fill="{AMBER}">'
          f'@{esc(user["login"])}</text>')

    def short(iso: str) -> str:
        return datetime.strptime(iso, "%Y-%m-%d").strftime("%d %b").lstrip("0")

    weeks = calendar["weeks"]
    week, last_week = (weeks[-1] if weeks else []), (weeks[-2] if len(weeks) > 1 else [])
    month = [day for day in days if day["date"][:7] == today[:7]]
    prev_key = f"{y0 - (mo == 1)}-{12 if mo == 1 else mo - 1:02d}"
    # last month up to the same date, so a half-done month isn't compared with a whole one
    last_month = [day for day in days if day["date"][:7] == prev_key and day["date"][8:] <= today[8:]]
    year = [day for day in days if day["date"][:4] == today[:4]]
    by_month = Counter()
    for day in year:
        by_month[day["date"][5:7]] += day["count"]
    best = max(by_month, key=by_month.get) if by_month else ""

    def versus(now: int, then: int, what: str) -> tuple[str, str]:
        arrow = "▲" if now > then else "▼" if now < then else "="
        return f"{arrow} {abs(now - then)} vs {what}", GREEN if now >= then else "#ff7b72"

    terms = []
    if week:
        t = _term(week, 7)
        terms.append(("WEEKLY", f"{short(week[0]['date'])} – {short(today)}", t,
                      versus(t["total"], sum(day["count"] for day in last_week), "last week")))
    if month:
        t = _term(month, 14)
        prev = datetime.strptime(prev_key, "%Y-%m").strftime("%b")
        terms.append(("MONTHLY", f"{datetime.strptime(today, '%Y-%m-%d'):%B %Y}", t,
                      versus(t["total"], sum(day["count"] for day in last_month), f"{prev} (same days)")))
    if year:
        t = _term(year, 30)
        top = (f"Best month: {datetime.strptime(best, '%m'):%b} · {by_month[best]}" if by_month[best] else "No contributions yet",
               AMBER)
        terms.append(("YEARLY", f"1 Jan – {short(today)} {today[:4]}", t, top))

    for i, (title, span, t, (note, note_color)) in enumerate(terms):
        x, y, w, h = 24 + i * 274, 66, 254, 200
        grade, color = _grade(t["overall"])
        b += f'<g class="rise" {d(.3 + i * .12)}>' + panel(x, y, w, h, 10)
        b += (f'<text x="{x + 16}" y="{y + 24}" font-size="12.5" font-weight="800" letter-spacing="1.5" fill="{AMBER}">{title}</text>'
              f'<text x="{x + 16}" y="{y + 40}" font-size="9.5" class="muted">{esc(span)}</text>')
        # the teacher's rubber stamp
        sx, sy = x + w - 36, y + 34
        b += (f'<g class="pop" {d(1 + i * .2)}><g transform="rotate(-12 {sx} {sy})">'
              f'<circle cx="{sx}" cy="{sy}" r="23" fill="{color}" fill-opacity=".1" stroke="{color}" stroke-width="2"/>'
              f'<circle cx="{sx}" cy="{sy}" r="18.5" stroke="{color}" stroke-opacity=".5" stroke-dasharray="2 2"/>'
              f'<text x="{sx}" y="{sy + 7.5}" text-anchor="middle" font-size="21" font-weight="900" fill="{color}" '
              f'filter="url(#glow)">{grade}</text></g></g>')
        rows = [("Attendance", f'{t["active"]}/{t["n"]} days', t["marks"]["attendance"]),
                ("Contributions", f'{t["total"]} · {t["total"] / max(t["n"], 1):.1f}/day', t["marks"]["output"]),
                ("Longest streak", f'{t["streak"]} day{"s" if t["streak"] != 1 else ""}', t["marks"]["streak"])]
        for k, (subject, value, score) in enumerate(rows):
            ry = y + 74 + k * 30
            g, gc = _grade(score)
            b += (f'<text x="{x + 16}" y="{ry}" font-size="10.5" font-weight="600" fill="#c9d1d9">{subject}</text>'
                  f'<text x="{x + w - 44}" y="{ry}" text-anchor="end" font-size="9.5" class="muted mono">{esc(value)}</text>'
                  f'<text x="{x + w - 16}" y="{ry}" text-anchor="end" font-size="11" font-weight="800" fill="{gc}">{g}</text>'
                  f'<rect x="{x + 16}" y="{ry + 7}" width="{w - 32}" height="4" rx="2" fill="#1d2633"/>'
                  f'<rect x="{x + 16}" y="{ry + 7}" width="{(w - 32) * score / 100:.1f}" height="4" rx="2" fill="{gc}" '
                  f'class="grow" {d(1.2 + i * .2 + k * .1)}/>')
        b += (f'<line x1="{x + 16}" y1="{y + 158}" x2="{x + w - 16}" y2="{y + 158}" stroke="{BORDER}" stroke-dasharray="3 3"/>'
              f'<text x="{x + 16}" y="{y + 174}" font-size="10" font-weight="700" fill="{note_color}">{esc(note)}</text>'
              f'<text x="{x + 16}" y="{y + 190}" font-size="10" font-style="italic" fill="#c9d1d9">'
              f'“{esc(REMARKS[grade])}”</text></g>')

    b += (f'<text x="24" y="{H - 12}" font-size="9.5" class="dim mono fade" {d(2)}>Class teacher: Octocat Ma\'am ✍ · '
          f'attendance 40% · output 35% (goal {DAILY_GOAL}/day) · streak 25%</text>')
    b += synced(826, H - 12)
    return svg(W, H, b, title="Report Card")


# ------------------------------------------------------- cricket scorecard

DAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]


def _shot(runs: int) -> tuple[str, str]:
    """(label, colour) for an over: a day without code is a wicket."""
    if runs == 0:
        return "W", "#ff5e5e"
    if runs >= 6:
        return str(runs), GREEN
    if runs >= 4:
        return str(runs), BLUE
    return str(runs), "#c9d1d9"


def cricket(calendar: dict, commits: list[dict], n: int | None = None) -> str:
    """This week as a 7-over chase: each day is an over, contributions are runs, a day off is a wicket,
    and last week's total is the target."""
    W, H = 850, 270
    b = frame(W, H)
    b += heading(24, 20, n, "Commit Premier League", "This week chases last week · one over a day, contributions are runs")
    weeks = calendar["weeks"]
    week, last = (weeks[-1] if weeks else []), (weeks[-2] if len(weeks) > 1 else [])
    runs = [day["count"] for day in week]
    total, overs, wickets = sum(runs), len(runs), sum(1 for r in runs if r == 0)
    target = sum(day["count"] for day in last) + 1
    last_w = sum(1 for day in last if day["count"] == 0)

    # TV scoreboard
    x, y, w, h = 24, 66, 520, 180
    b += f'<g class="rise" {d(.2)}>' + panel(x, y, w, h, 10, fill="#0a0f18")
    b += (f'<rect x="{x}" y="{y}" width="132" height="26" rx="10" fill="url(#og)"/>'
          f'<rect x="{x + 100}" y="{y}" width="32" height="26" fill="url(#og)"/>'
          f'<text x="{x + 14}" y="{y + 17.5}" font-size="11" font-weight="900" fill="#1a0d02" letter-spacing="1">THIS WEEK XI</text>'
          f'<text x="{x + w - 14}" y="{y + 18}" text-anchor="end" font-size="10" class="muted">'
          f'Target <tspan fill="{AMBER}" font-weight="800">{target}</tspan> · Last week {target - 1}/{last_w} (7 ov)</text>')
    b += (f'<text x="{x + 16}" y="{y + 70}" font-size="40" font-weight="900" fill="{TEXT}" filter="url(#glow)">'
          f'{total}/{wickets}</text>'
          f'<text x="{x + 30 + len(f"{total}/{wickets}") * 23}" y="{y + 70}" font-size="13" class="muted">({overs} ov)</text>')
    crr = total / max(overs, 1)
    left = 7 - overs
    if total >= target:
        status, color = (f"Target chased with {left} over{'s' if left != 1 else ''} to spare! 🏆" if left else
                         f"Won by {total - target + 1} runs! 🏆"), GREEN
    elif left == 0:
        status, color = f"Lost by {target - 1 - total} runs · next week, revenge 💪", "#ff7b72"
    else:
        need = target - total
        status, color = f"Need {need} run{'s' if need != 1 else ''} from {left} over{'s' if left != 1 else ''} · RRR {need / left:.1f}", AMBER
    b += (f'<text x="{x + w - 16}" y="{y + 52}" text-anchor="end" font-size="10" class="muted">CRR</text>'
          f'<text x="{x + w - 16}" y="{y + 70}" text-anchor="end" font-size="18" font-weight="800" fill="{CYAN}">{crr:.1f}</text>'
          f'<text x="{x + 16}" y="{y + 96}" font-size="11.5" font-weight="700" fill="{color}">{esc(status)}</text>')
    # over by over
    for i in range(7):
        cx, cy = x + 40 + i * 70, y + 136
        if i < overs:
            label, c = _shot(runs[i])
            b += (f'<g class="pop" {d(.6 + i * .12)}><circle cx="{cx}" cy="{cy}" r="17" fill="{c}" fill-opacity=".14" stroke="{c}"/>'
                  f'<text x="{cx}" y="{cy + 5}" text-anchor="middle" font-size="14" font-weight="900" fill="{c}">{label}</text></g>')
        else:
            b += f'<circle cx="{cx}" cy="{cy}" r="17" stroke="{BORDER}" stroke-dasharray="3 3"/>'
        b += (f'<text x="{cx}" y="{cy + 32}" text-anchor="middle" font-size="9" '
              f'class="{"muted" if i < overs else "dim"}">{DAYS[i]}</text>')
    b += "</g>"

    # the ground: a ball bowled down the pitch, again and again
    gx, gy = 556, 66
    b += f'<g class="rise" {d(.35)}>' + panel(gx, gy, 270, 92, 10, fill="#0b1a10", stroke="#1f4d2b")
    b += (f'<ellipse cx="{gx + 135}" cy="{gy + 46}" rx="118" ry="38" fill="#14532d" stroke="#ffffff" stroke-opacity=".35" '
          f'stroke-dasharray="4 4"/><rect x="{gx + 95}" y="{gy + 38}" width="80" height="16" rx="2" fill="#c8a96a"/>'
          + "".join(f'<rect x="{gx + sx}" y="{gy + 38}" width="1.6" height="16" fill="#ffffff"/>' for sx in (99, 101.5, 104, 166, 168.5, 171))
          + f'<circle cx="{gx + 170}" cy="{gy + 46}" r="3" fill="#ff3b30" class="bowl"/></g>')
    # match facts
    day_runs = [(r, i) for i, r in enumerate(runs)]
    best = max(day_runs) if day_runs else (0, 0)
    start = week[0]["date"] if week else ""
    mom = Counter(c["repo"] for c in commits if c["date"][:10] >= start).most_common(1)
    partner = run_ = 0
    for r in runs:
        run_ = run_ + 1 if r else 0
        partner = max(partner, run_)
    facts = [("Player of the Match", f"{trunc(mom[0][0], 20)} · {mom[0][1]}" if mom else "—", AMBER),
             ("Best over", f"{DAYS[best[1]]} · {best[0]} runs" if best[0] else "—", GREEN),
             ("Top partnership", f"{partner} day{'s' if partner != 1 else ''} in a row", CYAN)]
    for i, (k, v, c) in enumerate(facts):
        yy = gy + 112 + i * 22
        b += (f'<g class="fade" {d(.9 + i * .15)}><text x="{gx + 4}" y="{yy}" font-size="10" class="muted">{k}</text>'
              f'<text x="{gx + 270}" y="{yy}" text-anchor="end" font-size="10.5" font-weight="700" fill="{c}">{esc(v)}</text></g>')
    # commentary
    if best[0] >= 10:
        line = f"Kya shot hai! {DAYS[best[1]]} ko {best[0]} runs ka toofani over 🔥"
    elif wickets >= 3:
        line = f"{wickets} wicket gir chuke hain, coach worried hai 😬"
    elif total >= target:
        line = "Crowd on its feet, chase complete! 🎉"
    else:
        line = "Steady batting, singles le rahe hain 🏏"
    b += (f'<text x="24" y="{H - 10}" font-size="9.5" class="dim mono fade" {d(2)}>🎙 {esc(line)}</text>'
          + synced(826, H - 10))
    css = ("@keyframes bowl{0%{transform:translateX(0);opacity:0}10%{opacity:1}70%{transform:translateX(-64px);opacity:1}"
           "100%{transform:translateX(-64px);opacity:0}}.bowl{animation:bowl 2.4s ease-in infinite}")
    return svg(W, H, b, css, title="Commit Premier League")


# --------------------------------------------------------- delhi metro map

# Delhi Metro line colours, given to my languages by how many repos use each
METRO_LINES = [("Blue", "#1e66c9"), ("Yellow", "#f5c400"), ("Magenta", "#c2187b"), ("Red", "#e2231a")]
GREY_LINE = ("Grey", "#9aa3ad")


def _route(x1, y1, x2, y2) -> str:
    """Metro-map segment: straight, a 45° bend in the middle, straight again."""
    dy = y2 - y1
    if not dy:
        return f" L{x2:.1f},{y2:.1f}"
    flat = max(0.0, (x2 - x1 - abs(dy)) / 2)
    return f" L{x1 + flat:.1f},{y1:.1f} L{x2 - flat:.1f},{y2:.1f} L{x2:.1f},{y2:.1f}"


def metro(repos: dict, tech: dict, n: int | None = None) -> str:
    """My repos as a Delhi Metro map: one line per language, stations in the order I created them,
    every line starting from home in Noida. A repo that uses another line's language is an interchange."""
    W, H = 850, 380
    b = frame(W, H)
    b += heading(24, 20, n, "Delhi Metro: Repo Lines", "One line per language, a station for every repo in the order I made them")
    rs = sorted(repos["repos"], key=lambda r: r["created_at"] or "")
    if not rs:
        return svg(W, H, b, title="Delhi Metro")
    langs = [lang for lang, _ in repos["languages"]][:len(METRO_LINES)]
    lines = [(lang, *METRO_LINES[i]) for i, lang in enumerate(langs)]
    if any(r["language"] not in langs for r in rs):
        lines.append(("Other", *GREY_LINE))
    names = [lang for lang, _, _ in lines]
    home = lambda r: r["language"] if r["language"] in langs else "Other"
    ys = {lang: 134 + i * (150 / max(len(lines) - 1, 1)) for i, lang in enumerate(names)}
    x0, x1 = 150, 800
    step = (x1 - x0) / max(len(rs) - 1, 1)
    pos = {r["name"]: (x0 + i * step, ys[home(r)]) for i, r in enumerate(rs)}
    hub = (46, 209)
    tokens = tech.get("repos", {})

    stops, paths = {}, {}
    for lang, _, color in lines:
        own = [r for r in rs if home(r) == lang]
        extra = [r for r in rs if home(r) != lang and lang != "Other" and lang.lower() in tokens.get(r["name"], set())]
        stops[lang] = sorted(own + extra, key=lambda r: r["created_at"] or "")
        y = ys[lang]
        p = f"M{hub[0]},{hub[1]} L{hub[0] + abs(y - hub[1]) + 30:.1f},{y:.1f}" if stops[lang] else ""
        px, py = hub[0] + abs(y - hub[1]) + 30, y
        for r in stops[lang]:
            sx, sy = pos[r["name"]]
            p += _route(px, py, sx, sy)
            px, py = sx, sy
        paths[lang] = p
    interchange = {r["name"] for r in rs if sum(r in stops[lang] for lang in names) > 1}

    for i, (lang, line, color) in enumerate(lines):
        if paths[lang]:
            b += (f'<path d="{paths[lang]}" stroke="{color}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round" '
                  f'class="draw" style="animation-delay:{.2 + i * .15:.2f}s"/>')
    # the newest line gets a train running on it
    newest = rs[-1]
    nl = home(newest)
    b += (f'<g><rect x="-9" y="-4" width="18" height="8" rx="3" fill="#ffffff" stroke="#0d1117"/>'
          f'<animateMotion dur="9s" repeatCount="indefinite" rotate="auto" path="{paths[nl]}"/></g>')
    for i, r in enumerate(rs):
        sx, sy = pos[r["name"]]
        color = next(c for lang, _, c in lines if lang == home(r))
        big = r["name"] in interchange
        ring = (f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="7" fill="#ffffff" stroke="#0d1117" stroke-width="2.5"/>' if big else
                f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="4.5" fill="#ffffff" stroke="{color}" stroke-width="2.5"/>')
        if r is newest:
            ring += f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="9" stroke="{AMBER}" stroke-width="1.5" class="pulse"/>'
        b += (f'<g class="pop" {d(.8 + i * .05)}><title>{esc(r["name"])} · {esc(r["language"] or "no main language")}'
              f' · opened {esc((r["created_at"] or "")[:10])}</title>{ring}'
              f'<text x="{sx + 5:.1f}" y="{sy - 9:.1f}" transform="rotate(-35 {sx + 5:.1f} {sy - 9:.1f})" font-size="8" '
              f'font-weight="600" fill="#c9d1d9" stroke="#0d121b" stroke-width="3" paint-order="stroke">'
              f'{esc(trunc(r["name"], 16))}</text></g>')
    b += (f'<circle cx="{hub[0]}" cy="{hub[1]}" r="11" fill="#ffffff" stroke="#0d1117" stroke-width="3"/>'
          f'<text x="{hub[0]}" y="{hub[1] + 4}" text-anchor="middle" font-size="10">🏠</text>'
          f'<text x="{hub[0]}" y="{hub[1] + 26}" text-anchor="middle" font-size="8.5" font-weight="700" fill="{AMBER}">Noida</text>'
          f'<text x="{hub[0]}" y="{hub[1] + 36}" text-anchor="middle" font-size="7.5" class="muted">Sec 46</text>')

    # legend + platform display board
    x = 24
    for lang, line, color in lines:
        label = f"{line} · {'Other languages' if lang == 'Other' else lang} · {len(stops[lang])}"
        b += (f'<rect x="{x}" y="324" width="16" height="6" rx="3" fill="{color}"/>'
              f'<text x="{x + 22}" y="330" font-size="9.5" fill="#c9d1d9">{esc(label)}</text>')
        x += len(label) * 5.4 + 40
    board = f"Agla station: {newest['name']} · Darwaze baayi taraf khulenge"
    b += (f'<rect x="24" y="342" width="560" height="22" rx="4" fill="#000000" stroke="#2b3646"/>'
          f'<g clip-path="url(#board)"><text x="590" y="357" font-size="11" font-weight="700" class="mono marquee" '
          f'fill="#ff9f1c">🚇 {esc(board)}</text></g>')
    b += synced(826, 357)
    css = ("@keyframes draw{to{stroke-dashoffset:0}}.draw{stroke-dasharray:2400;stroke-dashoffset:2400;"
           "animation:draw 2.4s ease forwards}"
           "@keyframes marquee{from{transform:translateX(0)}to{transform:translateX(-1250px)}}"
           ".marquee{animation:marquee 20s linear infinite}")
    defs = '<clipPath id="board"><rect x="28" y="342" width="552" height="22"/></clipPath>'
    return svg(W, H, b, css, defs, title="Delhi Metro: Repo Lines")


# ----------------------------------------------------------- dainik commit

PAPER, INK, RULE, PRESS_RED = "#f4ecd8", "#1d1a16", "#8a7f6a", "#a3221a"
SERIF = "Georgia, 'Times New Roman', serif"
CARTOONS = ["Works on my machine!", "Bas ek last commit…", "Chai pilao, bug bhagao", "git push --force? Na beta na",
            "Merge conflict ne din bana diya", "Prod mein test karna mana hai", "Semicolon kahan gaya?!"]


def dainik_commit(user: dict, calendar: dict, commits: list[dict], events: list[dict], repos: dict,
                  weather: dict | None, n: int | None = None) -> str:
    """Today's front page of 'Dainik Commit', the newspaper of my GitHub, written from the live data."""
    W, H = 850, 370
    now = _ist()
    days = _days(calendar)
    today, yday = (days[-1]["count"] if days else 0), (days[-2]["count"] if len(days) > 1 else 0)
    week = sum(day["count"] for day in (calendar["weeks"][-1] if calendar["weeks"] else []))
    first = (user.get("name") or user["login"]).split()[0]
    rs = repos["repos"]
    newest = max(rs, key=lambda r: r["created_at"] or "") if rs else None
    fresh = newest and (datetime.now(timezone.utc) - datetime.fromisoformat(newest["created_at"].replace("Z", "+00:00"))).days < 3
    latest = commits[0] if commits else None

    if fresh:
        head = f"Nayi repo '{newest['name']}' launch! Tech jagat mein halchal"
    elif today >= 10:
        head = f"{first} ka dhamaka: aaj {today} contributions!"
    elif today and latest:
        head = f"{latest['repo']} pe kaam zor-shor se jaari, aaj {today} contributions"
    elif yday:
        head = f"Kal {yday} contributions ke baad aaj abhi tak shanti"
    else:
        head = "Coding mein chhutti! Sootron ke mutabik chai break lamba chala"
    sub = f"Is hafte {week} contributions · saal bhar mein {calendar['total']} · {len(rs)} repos"

    b = (f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="10" fill="{PAPER}" stroke="{RULE}"/>'
         f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="10" fill="url(#paper)" opacity=".5"/>')
    # masthead
    b += (f'<text x="{W / 2}" y="50" text-anchor="middle" font-size="38" font-weight="900" fill="{INK}" '
          f'font-family="\'Noto Serif Devanagari\', Mangal, {SERIF}" class="fade">दैनिक कमिट</text>'
          f'<rect x="24" y="16" width="128" height="40" fill="none" stroke="{INK}"/>'
          f'<text x="88" y="32" text-anchor="middle" font-size="9" font-weight="700" fill="{INK}" font-family="{SERIF}">NOIDA EDITION</text>'
          f'<text x="88" y="47" text-anchor="middle" font-size="8.5" fill="{INK}" font-family="{SERIF}">GitHub ka apna akhbaar</text>')
    w_ = weather or {}
    wx = f"{w_['temp']}°C, {w_['words']}" if w_ else "Mausam vibhag offline"
    aqi = f"AQI {w_['aqi']}" if w_.get("aqi") is not None else ""
    b += (f'<rect x="698" y="16" width="128" height="40" fill="none" stroke="{INK}"/>'
          f'<text x="762" y="32" text-anchor="middle" font-size="9" font-weight="700" fill="{INK}" font-family="{SERIF}">MAUSAM</text>'
          f'<text x="762" y="47" text-anchor="middle" font-size="8.5" fill="{INK}" font-family="{SERIF}">'
          f'{esc(wx)}{" · " + aqi if aqi else ""}</text>')
    joined = datetime.fromisoformat(user["created_at"].replace("Z", "+00:00"))
    vol = (datetime.now(timezone.utc) - joined).days
    b += (f'<line x1="24" y1="66" x2="826" y2="66" stroke="{INK}" stroke-width="2"/>'
          f'<line x1="24" y1="70" x2="826" y2="70" stroke="{INK}" stroke-width=".6"/>'
          f'<text x="{W / 2}" y="82" text-anchor="middle" font-size="9" fill="{INK}" font-family="{SERIF}" letter-spacing=".5">'
          f'Ank {vol} · {now:%A, %d %B %Y} · Keemat: 1 commit ☕</text>'
          f'<line x1="24" y1="89" x2="826" y2="89" stroke="{INK}" stroke-width=".6"/>')
    # headline
    for i, line in enumerate(wrap(head, 58, 2)):
        b += (f'<text x="{W / 2}" y="{120 + i * 28}" text-anchor="middle" font-size="25" font-weight="900" fill="{INK}" '
              f'font-family="{SERIF}" class="rise" {d(.2 + i * .1)}>{esc(line)}</text>')
    hy = 120 + (len(wrap(head, 58, 2)) - 1) * 28
    b += (f'<text x="{W / 2}" y="{hy + 22}" text-anchor="middle" font-size="12" font-style="italic" fill="{PRESS_RED}" '
          f'font-family="{SERIF}" class="fade" {d(.5)}>{esc(sub)}</text>')
    top = hy + 38
    b += f'<line x1="24" y1="{top}" x2="826" y2="{top}" stroke="{INK}" stroke-width=".6"/>'

    # column 1: the lead story
    story = (f"NOIDA, {now:%d %B}: Sootron ke mutabik {first} ne aaj {today} aur kal {yday} contributions kiye. "
             + (f"Sabse taaza commit \"{latest['message']}\" {latest['repo']} repo mein darj hua. " if latest else "")
             + (f"Taaza repo '{newest['name']}' ({newest['language'] or 'multi-lang'}) ne bhi dhyan kheencha. " if newest else "")
             + f"Is hafte ka score {week} tak pahunch gaya hai, aur jaankaar kehte hain ki silsila jaari rahega.")
    b += (f'<text x="24" y="{top + 18}" font-size="11" font-weight="800" fill="{PRESS_RED}" font-family="{SERIF}" '
          f'letter-spacing="1">MUKHYA SAMACHAR</text>')
    for i, line in enumerate(wrap(story, 54, 9)):
        b += (f'<text x="24" y="{top + 36 + i * 14}" font-size="10.5" fill="{INK}" font-family="{SERIF}" class="fade" '
              f'{d(.6 + i * .05)}>{esc(line)}</text>')
    b += f'<line x1="330" y1="{top + 8}" x2="330" y2="{H - 30}" stroke="{RULE}" stroke-width=".8"/>'

    # column 2: latest events
    b += (f'<text x="346" y="{top + 18}" font-size="11" font-weight="800" fill="{PRESS_RED}" font-family="{SERIF}" '
          f'letter-spacing="1">TAAZA KHABREIN</text>')
    for i, e in enumerate(events[:5]):
        when = datetime.fromisoformat(e["at"].replace("Z", "+00:00")) + timedelta(hours=5, minutes=30)
        b += (f'<g class="fade" {d(.8 + i * .1)}><text x="346" y="{top + 38 + i * 30}" font-size="10.5" font-weight="700" '
              f'fill="{INK}" font-family="{SERIF}">■ {esc(trunc(e["text"], 40))}</text>'
              f'<text x="356" y="{top + 51 + i * 30}" font-size="9" font-style="italic" fill="{RULE}" font-family="{SERIF}">'
              f'{when:%d %b, %I:%M %p}</text></g>')
    b += f'<line x1="600" y1="{top + 8}" x2="600" y2="{H - 30}" stroke="{RULE}" stroke-width=".8"/>'

    # column 3: share bazaar + cartoon
    stars = sum(r["stars"] for r in rs)
    b += (f'<text x="616" y="{top + 18}" font-size="11" font-weight="800" fill="{PRESS_RED}" font-family="{SERIF}" '
          f'letter-spacing="1">SHARE BAZAAR</text>')
    for i, (k, v) in enumerate((("Stars ★", stars), ("Followers", user["followers"]), ("Repos", len(rs)))):
        yy = top + 36 + i * 15
        b += (f'<text x="616" y="{yy}" font-size="10" fill="{INK}" font-family="{SERIF}">{k}</text>'
              f'<text x="826" y="{yy}" text-anchor="end" font-size="10" font-weight="700" fill="#1f7a3a" font-family="{SERIF}">'
              f'{compact(v)}</text>')
    seed = int(hashlib.md5(f"{now:%Y-%m-%d}".encode()).hexdigest(), 16)
    joke = CARTOONS[seed % len(CARTOONS)]
    cx, cy = 650, top + 112
    b += (f'<rect x="616" y="{top + 82}" width="210" height="{H - 32 - top - 82}" fill="none" stroke="{INK}" stroke-width=".8"/>'
          f'<text x="622" y="{top + 94}" font-size="8" font-style="italic" fill="{RULE}" font-family="{SERIF}">Aaj ka cartoon</text>'
          # a stick-figure coder at a laptop
          f'<g stroke="{INK}" stroke-width="1.6" stroke-linecap="round" fill="none">'
          f'<circle cx="{cx}" cy="{cy}" r="7"/><path d="M{cx},{cy + 7} v18 M{cx},{cy + 12} l12,6 M{cx},{cy + 25} l-6,12 '
          f'M{cx},{cy + 25} l6,12"/></g>'
          f'<path d="M{cx + 10},{cy + 22} h18 l-4,-12 h-14 z" fill="{INK}"/>'
          f'<text x="{cx + 2}" y="{cy - 12}" font-size="9">☕</text>'
          f'<path d="M{cx + 30},{cy - 14} h134 a6,6 0 0 1 6,6 v18 a6,6 0 0 1 -6,6 h-124 l-10,8 v-8 a6,6 0 0 1 -6,-6 v-18 '
          f'a6,6 0 0 1 6,-6 z" fill="#ffffff" stroke="{INK}"/>'
          f'<text x="{cx + 100}" y="{cy + 1}" text-anchor="middle" font-size="8.5" font-style="italic" fill="{INK}" '
          f'font-family="{SERIF}">{esc(joke)}</text>')

    b += (f'<line x1="24" y1="{H - 26}" x2="826" y2="{H - 26}" stroke="{INK}" stroke-width=".6"/>'
          f'<text x="24" y="{H - 11}" font-size="8.5" font-style="italic" fill="{RULE}" font-family="{SERIF}">'
          f'Har ghante naya edition · chhapa {now:%d %b %Y, %H:%M} IST · sampadak: @{esc(user["login"])}</text>')
    defs = ('<pattern id="paper" width="6" height="6" patternUnits="userSpaceOnUse">'
            f'<circle cx="1" cy="1" r=".5" fill="{RULE}" fill-opacity=".25"/></pattern>')
    return svg(W, H, b, defs=defs, title="Dainik Commit", light=False)
