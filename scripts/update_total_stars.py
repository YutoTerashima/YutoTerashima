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
    label = "total stars"
    value = compact(total)
    width = 216
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="36" role="img" aria-label="{label}: {value}">
  <title>{label}: {value}</title>
  <linearGradient id="s" x2="0" y2="100%">
    <stop offset="0" stop-color="#f8fafc" stop-opacity=".12"/>
    <stop offset="1" stop-color="#020617" stop-opacity=".12"/>
  </linearGradient>
  <clipPath id="r"><rect width="{width}" height="36" rx="9" fill="#fff"/></clipPath>
  <g clip-path="url(#r)">
    <rect width="112" height="36" fill="#0f172a"/>
    <rect x="112" width="{width - 112}" height="36" fill="#f59e0b"/>
    <rect width="{width}" height="36" fill="url(#s)"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="Segoe UI, Arial, sans-serif" font-size="13" font-weight="700">
    <text x="56" y="23">★ {label}</text>
    <text x="{112 + (width - 112) / 2:.0f}" y="23">{value}</text>
  </g>
  <text x="{width - 8}" y="32" fill="#fff7ed" text-anchor="end" font-family="Segoe UI, Arial, sans-serif" font-size="8">{repo_count} repos</text>
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
