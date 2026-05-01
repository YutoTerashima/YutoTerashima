from __future__ import annotations

import json
import os
import urllib.request
from pathlib import Path


USERNAME = "YutoTerashima"
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "widgets" / "total_stars.svg"


def github_json(url: str, token: str | None) -> list[dict]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "YutoTerashima-profile-star-counter",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_public_repos(token: str | None) -> list[dict]:
    repos: list[dict] = []
    page = 1
    while True:
        url = f"https://api.github.com/users/{USERNAME}/repos?per_page=100&page={page}&type=owner&sort=updated"
        batch = github_json(url, token)
        if not batch:
            break
        repos.extend(batch)
        page += 1
    return repos


def compact(n: int) -> str:
    if n >= 1000:
        return f"{n / 1000:.1f}k"
    return str(n)


def render(total: int, repo_count: int) -> str:
    label = "portfolio stars"
    value = compact(total)
    width = 720
    height = 118
    bar_width = min(560, 90 + total * 18)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{label}: {value}">
  <title>{label}: {value}</title>
  <defs>
  <linearGradient id="bg" x1="0" x2="1" y1="0" y2="1">
    <stop offset="0" stop-color="#0f172a"/>
    <stop offset=".55" stop-color="#111827"/>
    <stop offset="1" stop-color="#020617"/>
  </linearGradient>
  <linearGradient id="gold" x1="0" x2="1">
    <stop offset="0" stop-color="#f97316"/>
    <stop offset=".55" stop-color="#facc15"/>
    <stop offset="1" stop-color="#fde68a"/>
  </linearGradient>
  <filter id="glow" x="-20%" y="-60%" width="140%" height="220%">
    <feGaussianBlur stdDeviation="5" result="blur"/>
    <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  </defs>
  <rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="18" fill="url(#bg)" stroke="#334155" stroke-width="2"/>
  <circle cx="630" cy="22" r="78" fill="#f59e0b" opacity=".08"/>
  <text x="32" y="38" fill="#e2e8f0" font-family="Segoe UI, Arial, sans-serif" font-size="15" font-weight="700" letter-spacing=".8">PORTFOLIO SIGNAL</text>
  <text x="32" y="76" fill="#ffffff" font-family="Segoe UI, Arial, sans-serif" font-size="38" font-weight="800">★ {value}</text>
  <text x="150" y="73" fill="#fef3c7" font-family="Segoe UI, Arial, sans-serif" font-size="18" font-weight="700">total GitHub stars</text>
  <rect x="32" y="91" width="560" height="10" rx="5" fill="#1e293b"/>
  <rect x="32" y="91" width="{bar_width}" height="10" rx="5" fill="url(#gold)" filter="url(#glow)"/>
  <text x="612" y="101" fill="#cbd5e1" font-family="Segoe UI, Arial, sans-serif" font-size="12">{repo_count} public repos</text>
  <text x="676" y="37" fill="#facc15" text-anchor="middle" font-family="Segoe UI, Arial, sans-serif" font-size="30">★</text>
</svg>
"""


def main() -> None:
    token = os.environ.get("GITHUB_TOKEN")
    repos = fetch_public_repos(token)
    owned_non_forks = [repo for repo in repos if not repo.get("fork")]
    total = sum(int(repo.get("stargazers_count", 0)) for repo in owned_non_forks)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render(total, len(owned_non_forks)), encoding="utf-8")
    print(f"total_stars={total} repos={len(owned_non_forks)}")


if __name__ == "__main__":
    main()
