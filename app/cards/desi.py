"""Desi cards: Tech Thali, Desi Dev Corner (rashifal, chai-o-meter, commit mood ring) and the
Rajdhani Express of my repos."""

from __future__ import annotations

import hashlib
import math
from collections import Counter
from datetime import datetime, timedelta, timezone

from .. import config
from ..github import lang_color
from .theme import (AMBER, BLUE, BORDER, CYAN, GREEN, ORANGE, WEATHER_CSS, compact, d, dot, esc, frame, heading,
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
