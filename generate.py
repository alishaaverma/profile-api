"""Render every profile card to static SVG files.

Used by the GitHub Actions workflow (.github/workflows/profile-cards.yml), so the
profile README can show the cards without a publicly deployed API.

    python generate.py --out dist [--readme ../alishaaverma/README.md]

--readme rewrites the featured-project links between the
<!-- PROJECTS:START --> / <!-- PROJECTS:END --> markers so each card links to
the repo it currently shows.
"""

from __future__ import annotations

import argparse
import asyncio
import re
from pathlib import Path

from app import config
from app import github as gh
from app.cards import engineering as eng
from app.cards import live
from app.cards import profile as prof
from app.cards.theme import set_festival_dates

BUTTONS = {
    "button-view-my-work": ("View My Work", "github", True),
    "button-github": ("GitHub", "", False),
    "button-linkedin": ("LinkedIn", "", False),
    "button-email": ("Email", "", False),
    "button-resume": ("Resume", "", False),
}


async def render(login: str) -> tuple[dict[str, str], list[dict]]:
    user, repos, events, stats, cal, tech, festivals = await asyncio.gather(
        gh.get_user(login), gh.get_repos(login), gh.get_events(login), gh.get_stats(login), gh.get_calendar(login),
        gh.get_tech(login), gh.get_festival_dates())
    set_festival_dates(festivals)
    top = gh.featured(repos["repos"], 4)
    building = await gh.get_now_building(login, repos)

    # Section numbers follow the order of the cards in the profile README.
    cards = {
        "hero": prof.hero(user),
        "city": live.contribution_city(user, cal),
        "about": prof.about(user, 2),
        "tech-stack": prof.tech_stack(tech, 3),
        "smart-contracts": live.smart_contract_lab(user, repos, tech, 4),
        "what-i-build": prof.what_i_build(5),
        "featured-projects": prof.section_heading("Featured Projects",
                                                   {"newest": "My latest public repositories, live from GitHub",
                                                    "updated": "My most recently updated repositories, live from GitHub"}
                                                   .get(config.FEATURED_SORT, "Live from my GitHub repositories"), 6),
        "now-building": live.now_building(building, 7),
        "architecture": eng.architecture(tech, 8),
        "timeline": live.timeline_opensource(user, repos, stats, cal, 9),
        "analytics": live.analytics_exploring(user, stats, cal, 11),
        "activity": live.activity_terminal(user, repos, events, 13),
        "playground": live.playground(repos, f"https://api.github.com/users/{login}/repos", 15),
        "cloud": eng.cloud_deploy(tech, 16),
        "achievements": eng.achievements(user, repos, stats, cal, 17),
        "collaborate": prof.collaborate(user, 18),
    }
    for i in range(4):
        cards[f"project-{i}"] = live.project_card(top[i] if i < len(top) else None, i, login)
    for name, (label, icon, primary) in BUTTONS.items():
        cards[name] = prof.button(label, icon, primary)
    return cards, top


def update_readme(path: Path, login: str, top: list[dict]) -> bool:
    """Point each featured-project card at the repo it shows. Returns True if changed."""
    text = path.read_text()
    m = re.search(r"(<!-- PROJECTS:START -->\n)(.*?)(<!-- PROJECTS:END -->)", text, re.S)
    if not m:
        return False
    body = m.group(2)
    for i in range(4):
        url = top[i]["url"] if i < len(top) else f"https://github.com/{login}?tab=repositories"
        body = re.sub(rf'<a href="[^"]*">(<img src="[^"]*project-{i}\.svg)', rf'<a href="{url}">\1', body)
    new = text[:m.start(2)] + body + text[m.end(2):]
    if new != text:
        path.write_text(new)
        return True
    return False


async def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="dist")
    ap.add_argument("--readme")
    args = ap.parse_args()

    login = config.GITHUB_USERNAME
    cards, top = await render(login)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for name, body in cards.items():
        (out / f"{name}.svg").write_text(body)
    print(f"Rendered {len(cards)} cards for @{login} into {out}/")

    if args.readme:
        changed = update_readme(Path(args.readme), login, top)
        print("README project links", "updated" if changed else "unchanged")


if __name__ == "__main__":
    asyncio.run(main())
