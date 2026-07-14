"""Builds the standings HTML page from an AggregateResult. No filesystem access."""

import html

CAMERA_SVG = """<svg class="flourish" width="34" height="34" viewBox="0 0 24 24" fill="none"
  xmlns="http://www.w3.org/2000/svg">
  <path d="M4 8h3l1.5-2h7L17 8h3a1 1 0 0 1 1 1v10a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V9a1 1 0 0 1 1-1z"
    stroke="#fff" stroke-width="1.5" stroke-linejoin="round"/>
  <circle cx="12" cy="14" r="3.5" stroke="#fff" stroke-width="1.5"/>
</svg>"""

RANK_LABELS = {0: "1st place", 1: "2nd place", 2: "3rd place"}


def _team_heading(members):
    if len(members) <= 1:
        return ", ".join(members)
    return ", ".join(members[:-1]) + " & " + members[-1]


def _member_rows(team, roster_max_count):
    rows = []
    sorted_members = sorted(team.members, key=lambda m: team.counts[m], reverse=True)
    for member in sorted_members:
        count = team.counts[member]
        pct = 0 if roster_max_count == 0 else round((count / roster_max_count) * 100)
        pct = max(pct, 4) if count > 0 else 0
        rows.append(
            f'<div class="member-row">'
            f'<span class="name">{html.escape(member)}</span>'
            f'<span class="meter"><span style="width:{pct}%"></span></span>'
            f'<span class="count">{count}</span>'
            f"</div>"
        )
    return "\n".join(rows)


def _team_card(rank, team, roster_max_count):
    rank_class = f" rank-{rank + 1}" if rank < 3 else ""
    badge = f'<div class="rank-badge">{RANK_LABELS[rank]}</div>' if rank in RANK_LABELS else ""
    heading = _team_heading(team.members)
    return f"""
<div class="team-card{rank_class}">
  {CAMERA_SVG}
  {badge}
  <h2>{html.escape(heading)}</h2>
  <div class="total">{team.total} <span>photo{'s' if team.total != 1 else ''}</span></div>
  <details>
    <summary>Member breakdown</summary>
    {_member_rows(team, roster_max_count)}
  </details>
</div>"""


def _unmatched_section(unmatched):
    if not unmatched:
        return ""
    items = []
    for photo in unmatched:
        guess = html.escape(photo.unmatched_guess or "?")
        dept = html.escape(photo.department)
        items.append(
            f"<li><code>{html.escape(photo.filename)}</code> "
            f"&mdash; best guess: <strong>{guess}</strong>, department: {dept}, date: {photo.date}</li>"
        )
    return f"""
<details class="unmatched-panel">
  <summary>Unmatched files &mdash; needs review ({len(unmatched)})</summary>
  <ul>
    {''.join(items)}
  </ul>
</details>"""


def render(aggregate_result, generated_at_str):
    roster_max_count = max(
        (max(team.counts.values(), default=0) for team in aggregate_result.teams), default=0
    )
    cards = "\n".join(
        _team_card(rank, team, roster_max_count)
        for rank, team in enumerate(aggregate_result.teams)
    )
    unmatched_html = _unmatched_section(aggregate_result.unmatched)

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Session 2 Photo Standings</title>
<link rel="stylesheet" href="style.css">
</head>
<body>
<header class="hero">
  <h1>Session 2 Photo Standings</h1>
  <p>{aggregate_result.total_after_dedup} submissions counted so far &middot; {len(aggregate_result.teams)} teams</p>
</header>
<main>
  <div class="leaderboard">
    {cards}
  </div>
  {unmatched_html}
  <footer>Last updated: {html.escape(generated_at_str)}</footer>
</main>
</body>
</html>
"""
