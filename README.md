# BlueAlliancePy

Python client for [The Blue Alliance](https://www.thebluealliance.com) API v3.
Typed, schema-validated, zero boilerplate.

Built for FRC Team 7563 (Megazord) scouting infrastructure.

## Installation

```bash
pip install bluealliance
```

Or directly from the repository:

```bash
pip install git+https://github.com/Kaique-Sique/BlueAlliancePy.git
```

## Quick start

Get your API key at https://www.thebluealliance.com/account.

```python
from bluealliance import TBACollector

c = TBACollector("YOUR_TBA_KEY")

# team profile
team = c.team("frc7563")
print(team.nickname, team.city)  # Megazord, Jundiaí

# all teams at an event (typed, not raw dicts)
for team in c.event_teams("2025spbra"):
    print(team.team_number, team.nickname)

# live rankings
ranking = c.event_rankings("2025spbra")
if ranking:
    for entry in ranking.rankings[:5]:
        print(entry.rank, entry.team_key, entry.record)

# full event bundle in one call
bundle = c.event_bundle("2025spbra")
print(bundle.event.name)
print(f"{len(bundle.teams)} teams, {len(bundle.matches)} matches")

# 2025 Reefscape score breakdown already parsed
for match, bd in c.event_matches_2025("2025spbra"):
    if bd:
        coral = bd.red.autoCoralCount + bd.red.teleopCoralCount
        print(match.key, "red coral:", coral, "endgame:", bd.red.endGameRobot1)
```

## Three layers

| Layer | Import | What it does |
|---|---|---|
| `TBAClient` | `from bluealliance import TBAClient` | Raw HTTP — returns `dict`/`list`. One method per TBA endpoint (84 total). |
| `TBACollector` | `from bluealliance import TBACollector` | Typed — wraps every client method to return Pydantic models instead of dicts. Handles pagination automatically. |
| Schemas | `from bluealliance import Team, Match, Event` | Pydantic v2 models. Use `Model.model_validate(raw)` if you already have a dict. |

You can mix layers freely — `TBACollector` for most work, `TBAClient` when you need the raw payload for something not covered by the schemas.

## Low-level client

```python
from bluealliance import TBAClient

client = TBAClient("YOUR_TBA_KEY")

# returns raw dict/list -- no Pydantic parsing
raw = client.get_event_matches("2025spbra")
raw_team = client.get_team("frc7563")
```

## Pydantic models directly

```python
from bluealliance.schemas import Team, Match, ScoreBreakdown2025, parse_score_breakdown_2025

team = Team.model_validate(raw_dict)

match = Match.model_validate(raw_match_dict)
bd = parse_score_breakdown_2025(match.score_breakdown)
if bd:
    print(bd.red.totalPoints, bd.blue.endGameBargePoints)
```

## Available collector methods

### Status
- `c.status()` → `APIStatus`

### Teams
- `c.team(key)` → `Team`
- `c.team_simple(key)` → `TeamSimple`
- `c.team_history(key)` → `TeamHistory`
- `c.team_robots(key)` → `list[TeamRobot]`
- `c.team_awards(key, year?)` → `list[Award]`
- `c.team_media(key, year)` → `list[MediaBase]`
- `c.team_events(key, year?)` → `list[Event]`
- `c.team_matches(key, year)` → `list[Match]`
- `c.team_event_matches(key, event_key)` → `list[Match]`
- `c.team_event_status(key, event_key)` → `TeamEventStatus | None`
- `c.team_season_summary(key, year)` → `TeamSeasonSummary`
- `c.all_teams_by_year(year)` → `list[Team]` *(auto-paginates)*

### Events
- `c.events(year)` → `list[Event]`
- `c.event(key)` → `Event`
- `c.event_teams(key)` → `list[Team]`
- `c.event_matches(key)` → `list[Match]`
- `c.event_matches_2025(key)` → `list[tuple[Match, ScoreBreakdown2025 | None]]`
- `c.event_rankings(key)` → `EventRanking | None`
- `c.event_oprs(key)` → `EventOPRs | None`
- `c.event_alliances(key)` → `list[EliminationAlliance] | None`
- `c.event_awards(key)` → `list[Award]`
- `c.event_teams_statuses(key)` → `dict[str, TeamEventStatus | None]`
- `c.event_bundle(key)` → `EventBundle`

### Matches
- `c.match(key)` → `Match`
- `c.match_2025(key)` → `tuple[Match, ScoreBreakdown2025 | None]`
- `c.match_zebra(key)` → `Zebra`

### Districts
- `c.districts(year)` → `list[District]`
- `c.district_rankings(key)` → `list[DistrictRanking] | None`
- `c.district_advancement(key)` → `dict[str, DistrictAdvancement] | None`

### Regional (2025+)
- `c.regional_advancement(year)` → `dict[str, RegionalAdvancement] | None`
- `c.regional_rankings(year)` → `list[RegionalRanking] | None`

### Insights
- `c.leaderboards(year)` → `list[LeaderboardInsight]`
- `c.insights_v2(year, category?)` → `list[InsightV2...]`

## Requirements

- Python 3.11+
- `requests >= 2.32`
- `pydantic >= 2.7`
