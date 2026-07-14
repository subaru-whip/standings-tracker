"""ParsedPhoto list -> dedupe -> per-person/team tallies + unmatched list.

No filename-parsing or filesystem knowledge lives here — this module only
works on already-parsed ParsedPhoto objects.
"""

from dataclasses import dataclass, field

from parser import ParsedPhoto
from roster import Roster


@dataclass
class TeamResult:
    members: list
    counts: dict
    total: int


@dataclass
class AggregateResult:
    teams: list                # list[TeamResult], sorted by total descending
    unmatched: list             # list[ParsedPhoto], deduped
    total_scanned: int
    total_after_dedup: int
    total_matched: int
    total_unmatched: int


def aggregate(photos: list, roster: Roster) -> AggregateResult:
    seen = {}
    for photo in photos:
        seen.setdefault(photo.dedup_key, photo)
    deduped = list(seen.values())

    person_counts = {name: 0 for name in roster.person_to_team}
    unmatched = []

    for photo in deduped:
        if photo.person is not None:
            person_counts[photo.person] += 1
        else:
            unmatched.append(photo)

    teams = []
    for members in roster.teams:
        counts = {name: person_counts[name] for name in members}
        teams.append(TeamResult(members=members, counts=counts, total=sum(counts.values())))
    teams.sort(key=lambda t: t.total, reverse=True)

    unmatched.sort(key=lambda p: p.filename.lower())

    return AggregateResult(
        teams=teams,
        unmatched=unmatched,
        total_scanned=len(photos),
        total_after_dedup=len(deduped),
        total_matched=len(deduped) - len(unmatched),
        total_unmatched=len(unmatched),
    )
