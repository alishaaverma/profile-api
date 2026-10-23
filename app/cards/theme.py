"""Shared SVG design system: colours, base CSS animations, primitives."""

from __future__ import annotations

import html
import math
import textwrap
from datetime import datetime, timedelta, timezone

BG = "#070a10"
CARD = "#0d121b"
CARD2 = "#111823"
BORDER = "#1f2a38"
ORANGE = "#ff8c42"
ORANGE_DEEP = "#ff6a00"
AMBER = "#ffb067"
TEXT = "#e6edf3"
MUTED = "#8b949e"
DIM = "#56606c"
GREEN = "#3fb950"
BLUE = "#58a6ff"
CYAN = "#39c5cf"
ETH = "#8c8cff"  # Solidity / Web3 accent

FONT = "'Segoe UI', Ubuntu, 'Helvetica Neue', Arial, sans-serif"
MONO = "'JetBrains Mono', 'Fira Code', Consolas, 'Courier New', monospace"

BASE_CSS = f"""
text{{font-family:{FONT}}}
text:not([fill]){{fill:{TEXT}}}
.mono{{font-family:{MONO};white-space:pre}}
.type{{clip-path:inset(0 100% 0 0);animation:type .7s steps(14,end) forwards}}
.muted{{fill:{MUTED}}}
.dim{{fill:{DIM}}}
.orange{{fill:{ORANGE}}}
.fade{{opacity:0;animation:fade .9s ease forwards}}
.rise{{opacity:0;animation:rise .8s cubic-bezier(.2,.8,.2,1) forwards}}
.pop{{opacity:0;transform-box:fill-box;transform-origin:center;animation:pop .6s cubic-bezier(.3,1.5,.5,1) forwards}}
.grow{{transform-box:fill-box;transform-origin:left center;transform:scaleX(0);animation:grow 1.4s cubic-bezier(.2,.8,.2,1) forwards}}
.growy{{transform-box:fill-box;transform-origin:center bottom;transform:scaleY(0);animation:growy 1.2s cubic-bezier(.2,.8,.2,1) forwards}}
.pulse{{animation:pulse 2.2s ease-in-out infinite}}
.blink{{animation:blink 1s step-end infinite}}
.float{{transform-box:fill-box;animation:float 4s ease-in-out infinite}}
.flow{{stroke-dasharray:6 7;animation:flow 1.1s linear infinite}}
.glowpulse{{animation:glowpulse 3s ease-in-out infinite}}
.spin{{transform-box:fill-box;transform-origin:center;animation:spin 24s linear infinite}}
.twinkle{{animation:twinkle 3s ease-in-out infinite}}
@keyframes fade{{to{{opacity:1}}}}
@keyframes type{{to{{clip-path:inset(0 0 0 0)}}}}
@keyframes rise{{from{{opacity:0;transform:translateY(10px)}}to{{opacity:1;transform:translateY(0)}}}}
@keyframes pop{{from{{opacity:0;transform:scale(.6)}}to{{opacity:1;transform:scale(1)}}}}
@keyframes grow{{to{{transform:scaleX(1)}}}}
@keyframes growy{{to{{transform:scaleY(1)}}}}
@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.35}}}}
@keyframes blink{{50%{{opacity:0}}}}
@keyframes float{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-4px)}}}}
@keyframes flow{{to{{stroke-dashoffset:-13}}}}
@keyframes glowpulse{{0%,100%{{opacity:.55}}50%{{opacity:1}}}}
@keyframes spin{{to{{transform:rotate(360deg)}}}}
@keyframes twinkle{{0%,100%{{opacity:.2}}50%{{opacity:1}}}}
"""

# Light mode: when the viewer's browser/OS prefers light, the dark surfaces swap to
# GitHub's light palette. Terminals and the code editor (.mono text) stay dark on purpose;
# give mono text that sits on a card surface the "ink" class so it is recoloured too.
LIGHT_SURFACES = {
    "#0b1018": "#ffffff", "#070a10": "#f6f8fa", "#111823": "#f6f8fa", "#0d121b": "#ffffff",
    BORDER: "#d0d7de", "#161b22": "#ebedf0", "#141c28": "#dde3e9", "#0a0f17": "#e7ecf1",
    "#1d2633": "#d8dee4", "#161d29": "#d8dee4", "#243042": "#c9d1d9", "#2b3646": "#bfc8d2",
    "#0b111a": "#e6eaef", "#1a1109": "#fff1e6", "#1d1712": "#f1e6dc", "#2a1a0c": "#f1e6dc",
}
LIGHT_TEXT = {
    TEXT: "#1f2328", "#c9d1d9": "#424a53", AMBER: "#bc4c00", ORANGE: "#d9480f",
    "#8c8cff": "#5b5bd6", "#c9cbff": "#4b4bc4", "#a5d6ff": "#0969da",
}
LIGHT_CSS = "@media (prefers-color-scheme: light){" + "".join(
    f'[fill="{k}"]{{fill:{v}}}[stroke="{k}"]{{stroke:{v}}}[stop-color="{k}"]{{stop-color:{v}}}'
    for k, v in LIGHT_SURFACES.items()) + "".join(
    f'text:not(.mono)[fill="{k}"],text.ink[fill="{k}"],text:not(.mono) tspan[fill="{k}"],text.ink tspan[fill="{k}"]'
    f'{{fill:{v}}}' for k, v in LIGHT_TEXT.items()) + (
    "text:not([fill]):not(.mono),text.ink:not([fill]){fill:#1f2328}"
    # svg-prefixed so they outrank the base text:not([fill]) rule
    "svg text.muted,svg tspan.muted{fill:#57606a}svg text.dim,svg tspan.dim{fill:#6e7781}pattern path{stroke:#000}}")

BASE_DEFS = f"""
<linearGradient id="cardg" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="{CARD2}"/><stop offset="1" stop-color="{CARD}"/>
</linearGradient>
<linearGradient id="og" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{ORANGE_DEEP}"/><stop offset="1" stop-color="{AMBER}"/>
</linearGradient>
<linearGradient id="bgg" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#0b1018"/><stop offset="1" stop-color="{BG}"/>
</linearGradient>
<radialGradient id="emberg" cx=".5" cy="1" r=".9">
  <stop offset="0" stop-color="{ORANGE_DEEP}" stop-opacity=".16"/><stop offset="1" stop-color="{ORANGE_DEEP}" stop-opacity="0"/>
</radialGradient>
<filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
  <feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
</filter>
<filter id="softglow" x="-50%" y="-50%" width="200%" height="200%">
  <feGaussianBlur stdDeviation="6"/>
</filter>
<pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse">
  <path d="M24 0H0V24" fill="none" stroke="#ffffff" stroke-opacity=".035"/>
</pattern>
"""


def esc(s) -> str:
    return html.escape(str(s), quote=True)


def trunc(s: str, n: int) -> str:
    s = s or ""
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


def wrap(s: str, width: int, max_lines: int = 99) -> list[str]:
    lines = textwrap.wrap(s or "", width)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = trunc(lines[-1] + " …", width)
    return lines


def compact(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M".replace(".0M", "M")
    if n >= 1000:
        return f"{n / 1000:.1f}k".replace(".0k", "k")
    return str(n)


def ist_now() -> str:
    return (datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)).strftime("%d %b %Y, %H:%M IST")


# ------------------------------------------------------------ day / night

# Cards re-render every hour, so the sky follows the time of day in India.
# phase: (sky top, horizon glow, glow opacity, chance a window is lit, sun/moon colour)
SKIES = {
    "dawn": ("#1b2140", "#ff9a5a", .30, .15, "#ffb067"),
    "day": ("#0e2440", "#4a8fd8", .30, .05, "#ffd76a"),
    "dusk": ("#1c1030", "#ff5e3a", .36, .28, "#ff8c42"),
    "night": ("#04060c", "#24407a", .32, .42, "#e8ecf5"),
}


def sky_phase() -> str:
    h = (datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)).hour
    if 5 <= h < 8:
        return "dawn"
    if 8 <= h < 17:
        return "day"
    if 17 <= h < 20:
        return "dusk"
    return "night"


def phase_label(phase: str, location: str = "") -> str:
    word = {"dawn": "sunrise", "day": "daytime", "dusk": "sunset", "night": "night"}[phase]
    return f"{word} in {location.split(',')[0]}" if location else word


def sky(x, y, w, h, phase: str, rx: int = 14) -> str:
    """Gradient wash from a clear top to a phase-coloured horizon at the bottom."""
    top, horizon, op, _, _ = SKIES[phase]
    gid = f"sky{x}-{y}-{w}"
    return (f'<defs><linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{top}" stop-opacity=".0"/>'
            f'<stop offset="1" stop-color="{horizon}" stop-opacity="{op}"/></linearGradient></defs>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="url(#{gid})"/>')


def celestial(cx, cy, phase: str, r: float = 18) -> str:
    """Sun by day, low orange sun at dawn/dusk, moon at night."""
    color = SKIES[phase][4]
    out = f'<circle cx="{cx}" cy="{cy}" r="{r * 2.2:.0f}" fill="{color}" fill-opacity=".14" filter="url(#softglow)" class="glowpulse"/>'
    if phase == "night":
        out += (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{color}" filter="url(#glow)"/>'
                f'<circle cx="{cx - r * .3:.1f}" cy="{cy - r * .2:.1f}" r="{r * .22:.1f}" fill="#c3cad8"/>'
                f'<circle cx="{cx + r * .35:.1f}" cy="{cy + r * .3:.1f}" r="{r * .15:.1f}" fill="#c3cad8"/>'
                f'<circle cx="{cx + r * .1:.1f}" cy="{cy - r * .5:.1f}" r="{r * .1:.1f}" fill="#c3cad8"/>')
        return out
    if phase == "day":
        rays = "".join(f'<path d="M{cx},{cy - r * 1.35:.1f}v{-r * .45:.1f}" stroke="{color}" stroke-width="2" '
                       f'stroke-linecap="round" transform="rotate({a} {cx} {cy})"/>' for a in range(0, 360, 45))
        out += f'<g class="spin">{rays}</g>'
    return out + f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{color}" filter="url(#glow)"/>'


# ------------------------------------------------------------- festivals

# name: (greeting, window colours, chance a window is lit)
FESTIVALS = {
    "diwali": ("Happy Diwali", [AMBER, "#ffd76a", ORANGE], .85),
    "holi": ("Happy Holi", ["#ff4fa3", "#3fd0ff", "#ffe14d", "#5be36a", "#b36bff"], .45),
    "newyear": ("Happy New Year", ["#ffd76a", "#c9d1ff", AMBER], .55),
    "independence": ("Happy Independence Day", ["#FF9933", "#ffffff", "#138808"], .5),
    "republic": ("Happy Republic Day", ["#FF9933", "#ffffff", "#138808"], .5),
    "birthday": ("It's my birthday!", ["#ff8fd1", "#ffd76a", "#8fd3ff"], .5),
    "christmas": ("Merry Christmas", ["#ff4d4d", "#3fb950", "#ffd76a"], .6),
    "halloween": ("Happy Halloween", [ORANGE, "#b36bff", "#7CFC00"], .35),
    "sankranti": ("Happy Makar Sankranti", ["#ffd76a", "#ff4fa3", "#3fd0ff", ORANGE], .3),
    "eid": ("Eid Mubarak", ["#ffd76a", "#3fb950", "#ffffff"], .55),
    "navratri": ("Happy Navratri", ["#ff4d4d", "#FF9933", "#ffd76a", "#3fb950", "#3fd0ff", "#b36bff", "#ff4fa3",
                                    "#ffffff", "#8c8cff"], .5),
    "dussehra": ("Happy Dussehra", [ORANGE, "#ffd76a", "#ff4d4d"], .5),
    "ganesh": ("Ganpati Bappa Morya", ["#FF9933", "#ffd76a", ORANGE], .5),
    "janmashtami": ("Happy Janmashtami", ["#3fd0ff", "#3fb950", "#ffd76a"], .45),
    "rakhi": ("Happy Raksha Bandhan", ["#ff4fa3", "#ffd76a", ORANGE], .45),
    "onam": ("Happy Onam", ["#ffd76a", ORANGE, "#ff4d4d", "#ffffff"], .45),
    "gurpurab": ("Happy Gurpurab", [AMBER, "#ffd76a"], .8),
    "chhath": ("Happy Chhath Puja", [ORANGE, "#ffd76a"], .5),
}
# these add a row of lamps / pumpkins at street level
GROUND_FESTIVALS = {"diwali", "halloween", "gurpurab", "chhath"}


# {'YYYY-MM-DD': festival} from the live holiday calendar (github.get_festival_dates);
# filled before rendering with set_festival_dates().
FESTIVAL_DATES: dict[str, str] = {}


def set_festival_dates(dates: dict[str, str]) -> None:
    FESTIVAL_DATES.clear()
    FESTIVAL_DATES.update(dates)


def festival_today() -> str | None:
    """Which festival theme is on today in India, if any."""
    from .. import config

    today = (datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)).date()
    md = today.strftime("%m-%d")
    if config.BIRTHDAY and md == config.BIRTHDAY:
        return "birthday"
    if today.isoformat() in FESTIVAL_DATES:
        return FESTIVAL_DATES[today.isoformat()]
    # fixed dates, so these still show if the calendar can't be reached
    if md in ("12-31", "01-01"):
        return "newyear"
    if md in ("12-24", "12-25"):
        return "christmas"
    if md in ("10-30", "10-31"):
        return "halloween"
    if md in ("01-13", "01-14", "01-15"):  # Lohri, Makar Sankranti, Pongal
        return "sankranti"
    if md == "08-15":
        return "independence"
    if md == "01-26":
        return "republic"
    return None


FESTIVAL_CSS = (
    "@keyframes burst{0%{transform:scale(.1);opacity:0}12%{opacity:1}70%{opacity:.8}100%{transform:scale(1);opacity:0}}"
    ".burst{transform-box:fill-box;transform-origin:center;opacity:0;animation:burst 2.8s ease-out infinite}"
    "@keyframes drift{from{transform:translateY(0)}to{transform:translateY(-260px)}}"
    ".drift{animation:drift 12s linear infinite}"
    "@keyframes flicker{0%,100%{transform:scaleY(1);opacity:1}50%{transform:scaleY(.8);opacity:.75}}"
    ".flicker{transform-box:fill-box;transform-origin:center bottom;animation:flicker .9s ease-in-out infinite}"
    "@keyframes fall{from{transform:translateY(-40px)}to{transform:translateY(260px)}}"
    ".fall{animation:fall 9s linear infinite}"
    "@keyframes fly{from{transform:translateX(-120px)}to{transform:translateX(560px)}}"
    ".fly{animation:fly 14s linear infinite}"
    "@keyframes sway{0%,100%{transform:rotate(-6deg)}50%{transform:rotate(6deg)}}"
    ".sway{transform-box:fill-box;transform-origin:center top;animation:sway 3s ease-in-out infinite}"
)


def festival_sky(name: str, x, y, w, h, seed: int = 9) -> str:
    """Sky decoration for a festival inside the box (x, y, w, h)."""
    import random

    rnd = random.Random(seed)
    colors = FESTIVALS[name][1]
    out = ""
    if name in ("newyear", "diwali", "dussehra"):  # fireworks
        for i in range(3 if name == "diwali" else 6):
            cx, cy, r = x + rnd.random() * w, y + rnd.random() * h * .6, 16 + rnd.random() * 14
            c = rnd.choice(colors)
            rays = "".join(f'<path d="M{cx:.0f},{cy:.0f}l{r * math.cos(a * math.pi / 6):.1f},{r * math.sin(a * math.pi / 6):.1f}" '
                           f'stroke="{c}" stroke-width="1.6" stroke-linecap="round"/>' for a in range(12))
            out += f'<g class="burst" filter="url(#glow)" style="animation-delay:{i * .55:.2f}s">{rays}</g>'
    if name in ("diwali", "gurpurab"):  # floating sky lanterns
        for i in range(5):
            lx, ly = x + rnd.random() * w, y + h * .5 + rnd.random() * h * .5
            out += (f'<g class="drift" style="animation-delay:{-rnd.random() * 12:.1f}s;animation-duration:{14 + rnd.random() * 8:.0f}s">'
                    f'<path d="M{lx - 5:.0f},{ly:.0f}h10l-2,12h-6z" fill="{ORANGE}" fill-opacity=".85" filter="url(#glow)"/>'
                    f'<circle cx="{lx:.0f}" cy="{ly + 9:.0f}" r="2" fill="#fff3c4"/></g>')
    if name == "holi":  # colour splashes
        for _ in range(9):
            out += (f'<circle cx="{x + rnd.random() * w:.0f}" cy="{y + rnd.random() * h:.0f}" r="{12 + rnd.random() * 22:.0f}" '
                    f'fill="{rnd.choice(colors)}" fill-opacity=".22" filter="url(#softglow)" class="glowpulse" '
                    f'style="animation-delay:{rnd.random() * 3:.1f}s"/>')
    if name in ("independence", "republic"):  # tricolour bunting
        n = int(w // 18)
        for i in range(n):
            bx = x + i * 18
            sag = 10 * math.sin(math.pi * i / max(1, n - 1))
            out += (f'<polygon points="{bx},{y + sag:.1f} {bx + 14},{y + sag:.1f} {bx + 7},{y + sag + 14:.1f}" '
                    f'fill="{colors[i % 3]}" fill-opacity=".85" class="pop" style="animation-delay:{i * .03:.2f}s"/>')
    if name == "ganesh":  # marigold garlands
        for row, (sag_h, y0) in enumerate(((16, y), (10, y + 4))):
            n = int(w // 9)
            for i in range(n):
                fx = x + i * 9
                fy = y0 + sag_h * math.sin(math.pi * i / max(1, n - 1))
                out += f'<circle cx="{fx:.0f}" cy="{fy:.1f}" r="3.6" fill="{colors[(i + row) % 2]}" fill-opacity=".95"/>'
        for i in range(5):  # hanging strands
            fx = x + w * (i + .5) / 5
            out += "".join(f'<circle cx="{fx:.0f}" cy="{y + 20 + k * 7}" r="3" fill="{colors[k % 2]}"/>' for k in range(4))
    if name == "navratri":  # garba lights and crossing dandiya sticks
        for _ in range(26):
            out += (f'<circle cx="{x + rnd.random() * w:.0f}" cy="{y + rnd.random() * h:.0f}" r="{1.5 + rnd.random() * 2:.1f}" '
                    f'fill="{rnd.choice(colors)}" class="twinkle" filter="url(#glow)" style="animation-delay:{rnd.random() * 3:.1f}s"/>')
        for i in range(4):
            dx, dy = x + w * (i + .5) / 4, y + h * .35 + (i % 2) * 18
            c1, c2 = colors[(2 * i) % len(colors)], colors[(2 * i + 3) % len(colors)]
            out += (f'<g class="sway" style="animation-delay:{i * .5:.1f}s">'
                    f'<path d="M{dx - 12:.0f},{dy - 12:.0f}L{dx + 12:.0f},{dy + 12:.0f}" stroke="{c1}" stroke-width="3" stroke-linecap="round"/>'
                    f'<path d="M{dx + 12:.0f},{dy - 12:.0f}L{dx - 12:.0f},{dy + 12:.0f}" stroke="{c2}" stroke-width="3" stroke-linecap="round"/></g>')
    if name == "janmashtami":  # dahi handi on a rope, and peacock feathers
        hx = x + w * .45
        out += (f'<path d="M{x:.0f},{y}Q{hx:.0f},{y + 30} {x + w:.0f},{y}" stroke="#c9a66b" stroke-width="1.5"/>'
                f'<g class="sway"><path d="M{hx:.0f},{y + 15}v12" stroke="#c9a66b" stroke-width="1.5"/>'
                f'<ellipse cx="{hx:.0f}" cy="{y + 42}" rx="16" ry="14" fill="#b5541c" stroke="#ffd76a"/>'
                f'<rect x="{hx - 9:.0f}" y="{y + 26}" width="18" height="5" rx="2" fill="#7c2d12" stroke="#ffd76a"/>'
                f'<path d="M{hx - 14:.0f},{y + 42}h28" stroke="#ffd76a" stroke-dasharray="3 3"/>'
                f'<ellipse cx="{hx:.0f}" cy="{y + 27}" rx="9" ry="3" fill="#ffffff" fill-opacity=".9"/></g>')
        for i in range(3):
            px, py = x + w * (.12 + i * .3), y + h * .55
            out += (f'<g class="sway" style="animation-delay:{i * .7:.1f}s"><path d="M{px:.0f},{py + 30:.0f}Q{px - 4:.0f},{py + 10:.0f} {px:.0f},{py:.0f}" stroke="#3fb950" stroke-width="1.4"/>'
                    f'<ellipse cx="{px:.0f}" cy="{py - 4:.0f}" rx="7" ry="10" fill="#3fb950" fill-opacity=".8"/>'
                    f'<ellipse cx="{px:.0f}" cy="{py - 4:.0f}" rx="4" ry="5.5" fill="#3fd0ff"/>'
                    f'<circle cx="{px:.0f}" cy="{py - 4:.0f}" r="2.2" fill="#1a2a6c"/></g>')
    if name == "rakhi":  # floating rakhis
        for i in range(5):
            rx_, ry_ = x + w * (i + .5) / 5, y + 20 + rnd.random() * h * .5
            c = colors[i % len(colors)]
            out += (f'<g class="sway" style="animation-delay:{i * .5:.1f}s">'
                    f'<path d="M{rx_ - 26:.0f},{ry_:.0f}q13,6 26,0t26,0" stroke="{c}" stroke-width="2"/>'
                    + "".join(f'<circle cx="{rx_ + 7 * math.cos(a * math.pi / 4):.1f}" cy="{ry_ + 7 * math.sin(a * math.pi / 4):.1f}" r="3.4" fill="{c}"/>'
                              for a in range(8)) +
                    f'<circle cx="{rx_:.0f}" cy="{ry_:.0f}" r="5" fill="#ffd76a" filter="url(#glow)"/></g>')
    if name == "onam":  # pookalam (flower carpet) spinning slowly
        px, py = x + w * .3, y + h * .45
        out += f'<g class="spin" style="animation-duration:40s">'
        for ring, (r, c) in enumerate(((34, "#ff4d4d"), (27, ORANGE), (20, "#ffd76a"), (13, "#ffffff"), (7, "#3fb950"))):
            out += f'<circle cx="{px:.0f}" cy="{py:.0f}" r="{r}" fill="{c}" fill-opacity=".85"/>'
            if ring < 3:
                out += "".join(f'<circle cx="{px + (r - 3) * math.cos(a * math.pi / 8):.1f}" cy="{py + (r - 3) * math.sin(a * math.pi / 8):.1f}" '
                               f'r="2.2" fill="#ffffff" fill-opacity=".7"/>' for a in range(16))
        out += "</g>"
    if name == "chhath":  # offering to the setting sun, reflected in water
        sx, sy = x + w * .22, y + h * .8
        out += (f'<circle cx="{sx:.0f}" cy="{sy:.0f}" r="26" fill="{ORANGE}" fill-opacity=".9" filter="url(#glow)" class="glowpulse"/>'
                + "".join(f'<path d="M{sx - 30 + k * 4:.0f},{sy + 30 + k * 6:.0f}h{60 - k * 8}" stroke="{ORANGE}" stroke-opacity="{.6 - k * .12:.2f}" '
                          f'stroke-width="2" stroke-linecap="round"/>' for k in range(4)))
    if name == "christmas":  # snowfall
        for _ in range(45):
            out += (f'<circle cx="{x + rnd.random() * w:.0f}" cy="{y + rnd.random() * h * .3:.0f}" r="{.8 + rnd.random() * 1.6:.1f}" '
                    f'fill="#ffffff" fill-opacity=".85" class="fall" '
                    f'style="animation-delay:{-rnd.random() * 9:.1f}s;animation-duration:{7 + rnd.random() * 6:.1f}s"/>')
    if name == "halloween":  # bats crossing the sky
        for i in range(5):
            bx, by = x + rnd.random() * w * .3, y + rnd.random() * h * .7
            out += (f'<g class="fly" style="animation-delay:{-rnd.random() * 14:.1f}s;animation-duration:{10 + rnd.random() * 8:.0f}s">'
                    f'<path d="M{bx:.0f},{by:.0f}q5,-7 10,-1q3,-4 6,0q3,-4 6,0q5,-6 10,1q-6,-1 -9,5q-3,-3 -7,0q-4,-3 -7,0q-3,-6 -9,-5z" '
                    f'fill="#1b1028" stroke="#b36bff" stroke-width=".6"/></g>')
    if name == "sankranti":  # kites on swaying strings
        for i in range(6):
            kx, ky, c = x + rnd.random() * w, y + rnd.random() * h * .6, rnd.choice(colors)
            out += (f'<g class="sway" style="animation-delay:{-rnd.random() * 3:.1f}s">'
                    f'<polygon points="{kx:.0f},{ky - 10:.0f} {kx + 8:.0f},{ky:.0f} {kx:.0f},{ky + 12:.0f} {kx - 8:.0f},{ky:.0f}" '
                    f'fill="{c}" fill-opacity=".9"/>'
                    f'<path d="M{kx:.0f},{ky - 10:.0f}V{ky + 12:.0f}M{kx - 8:.0f},{ky:.0f}H{kx + 8:.0f}" stroke="#fff" stroke-opacity=".5" stroke-width=".6"/>'
                    f'<path d="M{kx:.0f},{ky + 12:.0f}q-6,14 4,24t-2,26" stroke="#c9d1d9" stroke-opacity=".45"/></g>')
    if name == "eid":  # crescent, star and hanging lanterns
        cx, cy = x + w * .85, y + 22
        out += (f'<g filter="url(#glow)"><circle cx="{cx:.0f}" cy="{cy:.0f}" r="16" fill="#ffd76a"/>'
                f'<circle cx="{cx + 7:.0f}" cy="{cy - 4:.0f}" r="14" fill="#0b1018"/>'
                f'<path d="M{cx + 16:.0f},{cy - 8:.0f}l2,5 5,.5 -4,3 1.5,5 -4.5,-3 -4.5,3 1.5,-5 -4,-3 5,-.5z" fill="#ffd76a"/></g>')
        for i in range(6):
            lx = x + 20 + i * (w * .7 / 6)
            drop = 18 + (i % 3) * 14
            out += (f'<g class="sway" style="animation-delay:{i * .4:.1f}s"><path d="M{lx:.0f},{y}v{drop}" stroke="#ffd76a" stroke-opacity=".5"/>'
                    f'<path d="M{lx - 5:.0f},{y + drop + 3}h10l-2,12h-6z" fill="#ffd76a" fill-opacity=".85" filter="url(#glow)"/>'
                    f'<path d="M{lx:.0f},{y + drop}l-5,3h10z" fill="#c2410c"/></g>')
    if name == "birthday":  # balloons
        for i in range(7):
            bx, by = x + rnd.random() * w, y + h * .6 + rnd.random() * h * .4
            c = rnd.choice(colors)
            out += (f'<g class="drift" style="animation-delay:{-rnd.random() * 12:.1f}s;animation-duration:{10 + rnd.random() * 6:.0f}s">'
                    f'<path d="M{bx:.0f},{by + 12:.0f}q4,10 -2,22" stroke="#c9d1d9" stroke-opacity=".5"/>'
                    f'<ellipse cx="{bx:.0f}" cy="{by:.0f}" rx="8" ry="11" fill="{c}" fill-opacity=".9"/>'
                    f'<ellipse cx="{bx - 3:.0f}" cy="{by - 4:.0f}" rx="2" ry="3" fill="#fff" fill-opacity=".5"/></g>')
    return out


def festival_ground(name: str, x, y, w, n: int = 12) -> str:
    """Street-level row at height y: flickering diyas on Diwali, jack-o'-lanterns on Halloween."""
    out = ""
    step = w / n
    for i in range(n):
        cx = x + step * (i + .5)
        if name in ("diwali", "gurpurab", "chhath"):
            out += (f'<path d="M{cx - 7:.1f},{y + 4} q7,9 14,0z" fill="#c2410c" stroke="{AMBER}" stroke-width=".8"/>'
                    f'<ellipse cx="{cx:.1f}" cy="{y - 1}" rx="2.6" ry="5" fill="#ffd76a" filter="url(#glow)" class="flicker" '
                    f'style="animation-delay:{i * .13 % .9:.2f}s"/>')
        elif name == "halloween" and i % 2 == 0:
            out += (f'<ellipse cx="{cx:.1f}" cy="{y + 3}" rx="8" ry="6.5" fill="{ORANGE_DEEP}" stroke="#7c2d12"/>'
                    f'<path d="M{cx:.1f},{y - 3.5}v-3" stroke="#3fb950" stroke-width="1.6"/>'
                    f'<g class="flicker" style="animation-delay:{i * .17 % .9:.2f}s" filter="url(#glow)">'
                    f'<path d="M{cx - 4.5:.1f},{y + 1}l1.5,-2.5 1.5,2.5z M{cx + 1.5:.1f},{y + 1}l1.5,-2.5 1.5,2.5z" fill="#ffd76a"/>'
                    f'<path d="M{cx - 4:.1f},{y + 4}q4,3 8,0q-2,1 -4,1t-4,-1z" fill="#ffd76a"/></g>')
    return out


def stars(x, y, w, h, n: int = 30, seed: int = 5) -> str:
    import random

    rnd = random.Random(seed)
    return "".join(
        f'<circle cx="{x + rnd.random() * w:.0f}" cy="{y + rnd.random() * h:.0f}" r="{.6 + rnd.random() * .9:.1f}" '
        f'fill="#dfe8ff" class="twinkle" style="animation-delay:{rnd.random() * 3:.1f}s"/>'
        for _ in range(n))


def d(sec: float) -> str:
    """inline animation-delay style"""
    return f'style="animation-delay:{sec:.2f}s"'


def svg(width: int, height: int, body: str, css: str = "", defs: str = "", title: str = "") -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" fill="none" role="img" aria-label="{esc(title)}">'
        f"<title>{esc(title)}</title>"
        f"<style>{BASE_CSS}{css}{LIGHT_CSS}</style><defs>{BASE_DEFS}{defs}</defs>{body}</svg>"
    )


def frame(w: int, h: int, rx: int = 14, ember: bool = True) -> str:
    """Outer card background with grid texture and warm glow."""
    out = (
        f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="{rx}" fill="url(#bgg)" stroke="{BORDER}"/>'
        f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="{rx}" fill="url(#grid)"/>'
    )
    if ember:
        out += f'<rect x="1" y="{h * .45:.0f}" width="{w - 2}" height="{h * .55 - 1:.0f}" rx="{rx}" fill="url(#emberg)"/>'
    return out


def panel(x, y, w, h, rx=10, stroke=BORDER, fill="url(#cardg)", extra="") -> str:
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" {extra}/>'


def badge_num(x, y, num: int, size: int = 30) -> str:
    return (
        f'<rect x="{x}" y="{y}" width="{size}" height="{size}" rx="7" fill="#1a1109" stroke="{ORANGE}" filter="url(#glow)"/>'
        f'<text x="{x + size / 2}" y="{y + size / 2 + 5}" text-anchor="middle" font-size="14" font-weight="700" class="orange">{num:02d}</text>'
    )


def count_badge(cx, cy, n: int, r: float = 7.5) -> str:
    """Small orange bubble with a repo count; empty when n is 0."""
    if not n:
        return ""
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{ORANGE}" stroke="#0d1117" stroke-width="1.5"/>'
            f'<text x="{cx}" y="{cy + r * .42:.1f}" text-anchor="middle" font-size="{r * (1.07 if n < 10 else .9):.1f}" '
            f'font-weight="800" fill="#1a0d02">{min(n, 99)}</text>')


def heading(x, y, num: int | None, title: str, subtitle: str = "", delay: float = 0) -> str:
    """Section heading used at the top of each card."""
    out = f'<g class="rise" {d(delay)}>'
    tx = x
    if num is not None:
        out += badge_num(x, y, num)
        tx = x + 42
    out += f'<text x="{tx}" y="{y + 21}" font-size="19" font-weight="700">{esc(title)}</text>'
    if subtitle:
        out += f'<text x="{tx}" y="{y + 38}" font-size="11" class="muted">{esc(subtitle)}</text>'
    return out + "</g>"


def dot(x, y, r=4, color=ORANGE, cls="pulse") -> str:
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color}" class="{cls}" filter="url(#glow)"/>'


def bullet_list(x, y, items: list[str], gap=22, size=11.5, delay=0.3) -> str:
    out = ""
    for i, it in enumerate(items):
        yy = y + i * gap
        out += (
            f'<g class="rise" {d(delay + i * 0.1)}>'
            f'<circle cx="{x + 6}" cy="{yy - 4}" r="5.5" stroke="{ORANGE}" stroke-opacity=".6"/>'
            f'<circle cx="{x + 6}" cy="{yy - 4}" r="2.4" fill="{ORANGE}"/>'
            f'<text x="{x + 18}" y="{yy}" font-size="{size}" fill="#c9d1d9">{esc(it)}</text></g>'
        )
    return out


def flow_line(path: str, color=ORANGE, dots: int = 2, dur: float = 2.4, width=1.6) -> str:
    """Dashed animated connector with glowing packets travelling along it."""
    out = (
        f'<path d="{path}" stroke="{color}" stroke-opacity=".25" stroke-width="{width + 2}" fill="none"/>'
        f'<path d="{path}" stroke="{color}" stroke-width="{width}" fill="none" class="flow"/>'
    )
    for i in range(dots):
        out += (
            f'<circle r="3.2" fill="{AMBER}" filter="url(#glow)">'
            f'<animateMotion dur="{dur}s" begin="{i * dur / dots:.2f}s" repeatCount="indefinite" path="{path}"/></circle>'
        )
    return out


def skyline(x0: int, base: int, width: int, seed: int = 7, opacity: float = 0.9, max_h: int = 90,
            lit: float = 0.22, colors: list[str] | None = None) -> str:
    """Procedural city silhouette with twinkling windows; `lit` is the chance a window is on
    and `colors` (e.g. a festival palette) replaces the usual orange/blue lights."""
    import random

    rnd = random.Random(seed)
    out = f'<g opacity="{opacity}">'
    x = x0
    while x < x0 + width:
        bw = rnd.randint(16, 38)
        bh = rnd.randint(25, max_h)
        out += f'<rect x="{x}" y="{base - bh}" width="{bw}" height="{bh}" fill="#0a0f17" stroke="#141c28"/>'
        for wy in range(base - bh + 6, base - 6, 9):
            for wx in range(x + 4, x + bw - 4, 7):
                if rnd.random() < lit:
                    col = rnd.choice(colors) if colors else ORANGE if rnd.random() < 0.75 else "#7fb4ff"
                    out += (
                        f'<rect x="{wx}" y="{wy}" width="3" height="4" fill="{col}" class="twinkle" '
                        f'style="animation-delay:{rnd.random() * 3:.2f}s;animation-duration:{2 + rnd.random() * 4:.1f}s"/>'
                    )
        x += bw + rnd.randint(1, 4)
    return out + "</g>"


def cube(cx, cy, s=20, top="#ff9d57", left="#c2410c", right="#7c2d12", stroke=AMBER) -> str:
    """Isometric glowing cube icon."""
    h = s * 0.58
    return (
        f'<g filter="url(#glow)">'
        f'<polygon points="{cx},{cy - s} {cx + s},{cy - s + h} {cx},{cy - s + 2 * h} {cx - s},{cy - s + h}" fill="{top}" fill-opacity=".9" stroke="{stroke}" stroke-width=".8"/>'
        f'<polygon points="{cx - s},{cy - s + h} {cx},{cy - s + 2 * h} {cx},{cy + h} {cx - s},{cy}" fill="{left}" fill-opacity=".85" stroke="{stroke}" stroke-width=".8"/>'
        f'<polygon points="{cx + s},{cy - s + h} {cx},{cy - s + 2 * h} {cx},{cy + h} {cx + s},{cy}" fill="{right}" fill-opacity=".9" stroke="{stroke}" stroke-width=".8"/>'
        f"</g>"
    )


def synced(x, y, right=True) -> str:
    """'live · <time>' stamp proving the card was rendered from fresh data.
    x is the right edge when right=True, else the left edge."""
    label = f"live · {ist_now()}"
    width = len(label) * 5.75 + 12
    x0 = x - width if right else x
    return (
        f'<g class="fade" {d(1.2)}><circle cx="{x0 + 3}" cy="{y - 3.5}" r="3" fill="{GREEN}" class="pulse"/>'
        f'<text x="{x0 + 12}" y="{y}" font-size="9.5" class="dim mono">{esc(label)}</text></g>'
    )
