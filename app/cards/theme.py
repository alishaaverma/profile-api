"""Shared SVG design system: colours, base CSS animations, primitives."""

from __future__ import annotations

import html
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
        f"<style>{BASE_CSS}{css}</style><defs>{BASE_DEFS}{defs}</defs>{body}</svg>"
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
            lit: float = 0.22) -> str:
    """Procedural city silhouette with twinkling windows; `lit` is the chance a window is on."""
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
                    col = ORANGE if rnd.random() < 0.75 else "#7fb4ff"
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
