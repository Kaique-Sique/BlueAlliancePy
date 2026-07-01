'''
TBA Collector
=============
Typed data collection layer built on top of TBAClient + tba_schemas.
Every method fetches from TBA and returns validated Pydantic objects --
never raw dicts.

Usage:
    from tba_collector import TBACollector

    c = TBACollector()

    # single team
    team  = c.team("frc7563")
    print(team.nickname, team.city)

    # all teams in an event, already typed
    teams = c.event_teams("2025spbra")
    for t in teams:
        print(t.team_number, t.nickname)

    # match with 2025 score breakdown already parsed
    match, bd = c.match_2025("2025spbra_qm1")
    if bd:
        print(bd.red.autoCoralPoints, bd.blue.totalPoints)

    # full event bundle in one call
    bundle = c.event_bundle("2025spbra")
    print(bundle.event.name)
    print(bundle.rankings.rankings[0].team_key)
'''

from __future__ import annotations
from dataclasses import dataclass, field

from tba_client import TBAClient
from tba_schemas import (
    APIStatus,
    Award,
    District,
    DistrictAdvancement,
    DistrictRanking,
    EliminationAlliance,
    Event,
    EventDistrictPoints,
    EventOPRs,
    EventRanking,
    EventSimple,
    InsightV2Leaderboard,
    InsightV2Streak,
    InsightV2Timeseries,
    LeaderboardInsight,
    Match,
    MatchSimple,
    MediaBase,
    NotablesInsight,
    RegionalAdvancement,
    RegionalRanking,
    ScoreBreakdown2025,
    SearchIndex,
    Team,
    TeamEventStatus,
    TeamHistory,
    TeamRobot,
    TeamSimple,
    WLTRecord,
    Zebra,
    parse_score_breakdown_2025,
)


# =============================================================================
# EVENT BUNDLE
# =============================================================================

@dataclass
class EventBundle:
    '''All data for a single event, collected in one call via event_bundle().'''

    event:    Event
    teams:    list[Team]
    matches:  list[Match]
    rankings: EventRanking | None
    oprs:     EventOPRs | None
    alliances: list[EliminationAlliance] | None
    awards:   list[Award]


# =============================================================================
# TEAM SEASON SUMMARY
# =============================================================================

@dataclass
class TeamSeasonSummary:
    '''A team's full picture for one season: profile, events, matches and awards.'''

    team:    Team
    events:  list[Event]
    matches: list[Match]
    awards:  list[Award]
    robots:  list[TeamRobot]
    years_participated: list[int]


# =============================================================================
# COLLECTOR
# =============================================================================

class TBACollector:
    '''
    Thin typed wrapper over TBAClient.
    Every method returns Pydantic model instances, not raw dicts.
    '''

    def __init__(self):
        self._client = TBAClient()

    # -------------------------------------------------------------------------
    # TBA / STATUS
    # -------------------------------------------------------------------------

    def status(self) -> APIStatus:
        '''
        TBA API health and current season info. Good to call before a large
        batch sync to confirm the datafeed is up.
        '''
        return APIStatus.model_validate(self._client.get_status())

    def search_index(self) -> SearchIndex:
        '''Large search blob used by the TBA frontend (teams + event names).'''
        return SearchIndex.model_validate(self._client.get_search_index())

    # -------------------------------------------------------------------------
    # TEAMS -- paginated roster
    # -------------------------------------------------------------------------

    def all_teams_by_year(self, year: int) -> list[Team]:
        '''
        Returns every team that competed in a given season, automatically
        iterating through all 500-team pages until exhausted. Can be
        slow for a full year (~8000+ teams across ~20 pages) -- cache the
        result locally instead of calling this repeatedly.
        '''
        teams: list[Team] = []
        page = 0
        while True:
            page_data = self._client.get_teams_by_year(year, page)
            if not page_data:
                break
            teams.extend(Team.model_validate(t) for t in page_data)
            page += 1
        return teams

    def all_team_keys_by_year(self, year: int) -> list[str]:
        '''
        Returns every team key for a season without fetching full team objects.
        Much faster than all_teams_by_year when you only need keys.
        '''
        keys: list[str] = []
        page = 0
        while True:
            page_data = self._client.get_teams_by_year_keys(year, page)
            if not page_data:
                break
            keys.extend(page_data)
            page += 1
        return keys

    # -------------------------------------------------------------------------
    # SINGLE TEAM
    # -------------------------------------------------------------------------

    def team(self, team_key: str) -> Team:
        '''Full Team object for the given key (e.g. "frc7563").'''
        return Team.model_validate(self._client.get_team(team_key))

    def team_simple(self, team_key: str) -> TeamSimple:
        '''Lightweight team data (number, nickname, location only).'''
        return TeamSimple.model_validate(self._client.get_team_simple(team_key))

    def team_history(self, team_key: str) -> TeamHistory:
        '''Every event and award for the team across all seasons.'''
        return TeamHistory.model_validate(self._client.get_team_history(team_key))

    def team_robots(self, team_key: str) -> list[TeamRobot]:
        '''Year/robot-name pairs for every year the team named their robot.'''
        return [TeamRobot.model_validate(r) for r in self._client.get_team_robots(team_key)]

    def team_years_participated(self, team_key: str) -> list[int]:
        '''List of years the team competed in at least one event.'''
        return self._client.get_team_years_participated(team_key)

    def team_districts(self, team_key: str) -> list[District]:
        '''Districts the team has participated in, one entry per year.'''
        return [District.model_validate(d) for d in self._client.get_team_districts(team_key)]

    def team_awards(self, team_key: str, year: int | None = None) -> list[Award]:
        '''
        Awards won by a team. Pass year to restrict to a single season,
        or omit for all-time.
        '''
        raw = (
            self._client.get_team_awards_by_year(team_key, year)
            if year
            else self._client.get_team_awards(team_key)
        )
        return [Award.model_validate(a) for a in raw]

    def team_media(self, team_key: str, year: int) -> list[MediaBase]:
        '''
        Photos, videos, CAD models for a team in a specific year.
        Returns the common MediaBase shape (type, foreign_key, direct_url).
        '''
        raw = self._client.get_team_media_by_year(team_key, year)
        return [MediaBase.model_validate(m) for m in raw]

    def team_social_media(self, team_key: str) -> list[MediaBase]:
        '''Social media profiles for a team (Twitter, GitHub, Instagram...).'''
        return [MediaBase.model_validate(m) for m in self._client.get_team_social_media(team_key)]

    # -------------------------------------------------------------------------
    # TEAM -- events + matches
    # -------------------------------------------------------------------------

    def team_events(self, team_key: str, year: int | None = None) -> list[Event]:
        '''
        Events a team competed at. Pass year to restrict to one season,
        or omit for all time.
        '''
        raw = (
            self._client.get_team_events_by_year(team_key, year)
            if year
            else self._client.get_team_events(team_key)
        )
        return [Event.model_validate(e) for e in raw]

    def team_event_status(self, team_key: str, event_key: str) -> TeamEventStatus | None:
        '''
        Current rank, alliance and playoff status for the team at a specific
        event. Returns None when the event hasn't started yet.
        '''
        raw = self._client.get_team_event_status(team_key, event_key)
        return TeamEventStatus.model_validate(raw) if raw else None

    def team_event_awards(self, team_key: str, event_key: str) -> list[Award]:
        '''Awards the team won at a specific event.'''
        raw = self._client.get_team_event_awards(team_key, event_key)
        return [Award.model_validate(a) for a in raw]

    def team_matches(self, team_key: str, year: int) -> list[Match]:
        '''All matches for the team in a given season.'''
        raw = self._client.get_team_matches_by_year(team_key, year)
        return [Match.model_validate(m) for m in raw]

    def team_matches_simple(self, team_key: str, year: int) -> list[MatchSimple]:
        '''Lightweight match list for the team (no score_breakdown) in a season.'''
        raw = self._client.get_team_matches_by_year_simple(team_key, year)
        return [MatchSimple.model_validate(m) for m in raw]

    def team_event_matches(self, team_key: str, event_key: str) -> list[Match]:
        '''All matches for the team at a specific event.'''
        raw = self._client.get_team_event_matches(team_key, event_key)
        return [Match.model_validate(m) for m in raw]

    def team_season_summary(self, team_key: str, year: int) -> TeamSeasonSummary:
        '''
        Convenience collector: fetches team profile, events, matches, awards
        and robots for a full season in a single call.
        '''
        return TeamSeasonSummary(
            team=self.team(team_key),
            events=self.team_events(team_key, year),
            matches=self.team_matches(team_key, year),
            awards=self.team_awards(team_key, year),
            robots=self.team_robots(team_key),
            years_participated=self.team_years_participated(team_key),
        )

    # -------------------------------------------------------------------------
    # EVENTS -- listing
    # -------------------------------------------------------------------------

    def events(self, year: int) -> list[Event]:
        '''All events in a given season.'''
        return [Event.model_validate(e) for e in self._client.get_events_by_year(year)]

    def events_simple(self, year: int) -> list[EventSimple]:
        '''Lightweight event list for a season (key, name, dates, type).'''
        return [EventSimple.model_validate(e) for e in self._client.get_events_by_year_simple(year)]

    def event_keys(self, year: int) -> list[str]:
        '''Just the event keys for a season -- fastest way to discover events.'''
        return self._client.get_events_by_year_keys(year)

    # -------------------------------------------------------------------------
    # SINGLE EVENT
    # -------------------------------------------------------------------------

    def event(self, event_key: str) -> Event:
        '''Full event details (name, dates, venue, webcasts, district...).'''
        return Event.model_validate(self._client.get_event(event_key))

    def event_teams(self, event_key: str) -> list[Team]:
        '''All teams that competed at the event.'''
        return [Team.model_validate(t) for t in self._client.get_event_teams(event_key)]

    def event_teams_simple(self, event_key: str) -> list[TeamSimple]:
        '''Lightweight team list for the event.'''
        return [TeamSimple.model_validate(t) for t in self._client.get_event_teams_simple(event_key)]

    def event_team_keys(self, event_key: str) -> list[str]:
        '''Just the team keys for the event -- useful for quick lookups.'''
        return self._client.get_event_teams_keys(event_key)

    def event_matches(self, event_key: str) -> list[Match]:
        '''All matches for the event, including score_breakdown (stored as dict).'''
        return [Match.model_validate(m) for m in self._client.get_event_matches(event_key)]

    def event_matches_simple(self, event_key: str) -> list[MatchSimple]:
        '''Lightweight match list (no score_breakdown).'''
        return [MatchSimple.model_validate(m) for m in self._client.get_event_matches_simple(event_key)]

    def event_rankings(self, event_key: str) -> EventRanking | None:
        '''
        Full ranking table for the event. Returns None before any matches
        are played.
        '''
        raw = self._client.get_event_rankings(event_key)
        return EventRanking.model_validate(raw) if raw else None

    def event_oprs(self, event_key: str) -> EventOPRs | None:
        '''OPR, DPR and CCWM for every team at the event. None before quals.'''
        raw = self._client.get_event_oprs(event_key)
        return EventOPRs.model_validate(raw) if raw else None

    def event_coprs(self, event_key: str) -> dict[str, dict[str, float]] | None:
        '''
        Component OPRs keyed by component name and then by team key.
        Returns None if not yet computed.
        '''
        return self._client.get_event_coprs(event_key)

    def event_alliances(self, event_key: str) -> list[EliminationAlliance] | None:
        '''
        Playoff alliance selections for the event. None before alliance
        selection ceremony.
        '''
        raw = self._client.get_event_alliances(event_key)
        if raw is None:
            return None
        return [EliminationAlliance.model_validate(a) for a in raw]

    def event_awards(self, event_key: str) -> list[Award]:
        '''All awards (with recipients) from the event.'''
        return [Award.model_validate(a) for a in self._client.get_event_awards(event_key)]

    def event_teams_statuses(self, event_key: str) -> dict[str, TeamEventStatus | None]:
        '''
        Map of team_key -> TeamEventStatus for every team at the event.
        Replaces N individual team_event_status calls during elimination rounds.
        '''
        raw: dict = self._client.get_event_teams_statuses(event_key)
        return {
            key: TeamEventStatus.model_validate(val) if val else None
            for key, val in raw.items()
        }

    def event_district_points(self, event_key: str) -> EventDistrictPoints | None:
        '''District points earned per team at the event.'''
        raw = self._client.get_event_district_points(event_key)
        return EventDistrictPoints.model_validate(raw) if raw else None

    def event_media(self, event_key: str) -> list[MediaBase]:
        '''Media objects (photos/videos) for all teams at the event.'''
        return [MediaBase.model_validate(m) for m in self._client.get_event_team_media(event_key)]

    def event_bundle(self, event_key: str) -> EventBundle:
        '''
        Convenience collector: fetches all core event data in one call --
        event details, teams, matches, rankings, OPRs, alliances and awards.
        Ideal for populating the database for a newly-discovered event.
        '''
        return EventBundle(
            event=self.event(event_key),
            teams=self.event_teams(event_key),
            matches=self.event_matches(event_key),
            rankings=self.event_rankings(event_key),
            oprs=self.event_oprs(event_key),
            alliances=self.event_alliances(event_key),
            awards=self.event_awards(event_key),
        )

    # -------------------------------------------------------------------------
    # SINGLE MATCH
    # -------------------------------------------------------------------------

    def match(self, match_key: str) -> Match:
        '''
        Full match object. score_breakdown is a raw dict -- use match_2025()
        if you need the 2025 breakdown parsed into typed fields.
        '''
        return Match.model_validate(self._client.get_match(match_key))

    def match_simple(self, match_key: str) -> MatchSimple:
        '''Lightweight match (alliances, score, times -- no breakdown).'''
        return MatchSimple.model_validate(self._client.get_match_simple(match_key))

    def match_2025(self, match_key: str) -> tuple[Match, ScoreBreakdown2025 | None]:
        '''
        Returns the match AND its score_breakdown already parsed into the
        2025 Reefscape schema. The tuple makes it easy to destructure:

            match, bd = c.match_2025("2025spbra_qm12")
            if bd:
                print(bd.red.autoCoralPoints, bd.blue.endGameBargePoints)
        '''
        m = self.match(match_key)
        return m, parse_score_breakdown_2025(m.score_breakdown)

    def event_matches_2025(self, event_key: str) -> list[tuple[Match, ScoreBreakdown2025 | None]]:
        '''
        All matches for an event with their 2025 breakdowns pre-parsed.
        Useful for bulk analysis without calling match_2025 in a loop.

            for match, bd in c.event_matches_2025("2025spbra"):
                if bd:
                    total_coral = bd.red.autoCoralCount + bd.red.teleopCoralCount
        '''
        matches = self.event_matches(event_key)
        return [(m, parse_score_breakdown_2025(m.score_breakdown)) for m in matches]

    def match_zebra(self, match_key: str) -> Zebra:
        '''
        Zebra MotionWorks positional data (x, y per robot per frame).
        Only available at events with Zebra hardware installed.
        '''
        return Zebra.model_validate(self._client.get_match_zebra(match_key))

    # -------------------------------------------------------------------------
    # DISTRICTS
    # -------------------------------------------------------------------------

    def districts(self, year: int) -> list[District]:
        '''All districts active in a given season.'''
        return [District.model_validate(d) for d in self._client.get_districts_by_year(year)]

    def district_events(self, district_key: str) -> list[Event]:
        '''All events in a district (e.g. "2025fim").'''
        return [Event.model_validate(e) for e in self._client.get_district_events(district_key)]

    def district_teams(self, district_key: str) -> list[Team]:
        '''All teams that competed in events in a district.'''
        return [Team.model_validate(t) for t in self._client.get_district_teams(district_key)]

    def district_rankings(self, district_key: str) -> list[DistrictRanking] | None:
        '''Team rankings within a district. None before the season starts.'''
        raw = self._client.get_district_rankings(district_key)
        if raw is None:
            return None
        return [DistrictRanking.model_validate(r) for r in raw]

    def district_awards(self, district_key: str) -> list[Award]:
        '''All awards given across all events in a district.'''
        return [Award.model_validate(a) for a in self._client.get_district_awards(district_key)]

    def district_advancement(self, district_key: str) -> dict[str, DistrictAdvancement] | None:
        '''
        Map of team_key -> DistrictAdvancement (dcmp: bool, cmp: bool).
        Tells you which teams qualified for DCMP and CMP.
        '''
        raw = self._client.get_district_advancement(district_key)
        if raw is None:
            return None
        return {key: DistrictAdvancement.model_validate(val) for key, val in raw.items()}

    # -------------------------------------------------------------------------
    # REGIONAL ADVANCEMENT (2025+)
    # -------------------------------------------------------------------------

    def regional_advancement(self, year: int) -> dict[str, RegionalAdvancement] | None:
        '''
        For regional teams (non-district), maps team_key -> RegionalAdvancement
        with CMP qualification status. Available from 2025 onwards.
        '''
        raw = self._client.get_regional_advancement(year)
        if raw is None:
            return None
        return {key: RegionalAdvancement.model_validate(val) for key, val in raw.items()}

    def regional_rankings(self, year: int) -> list[RegionalRanking] | None:
        '''Regional pool rankings for CMP qualification.'''
        raw = self._client.get_regional_rankings(year)
        if raw is None:
            return None
        return [RegionalRanking.model_validate(r) for r in raw]

    # -------------------------------------------------------------------------
    # INSIGHTS
    # -------------------------------------------------------------------------

    def leaderboards(self, year: int) -> list[LeaderboardInsight]:
        '''
        Global leaderboard insights for a season (blue banners, win streaks,
        highest scores...). Use year=0 for all-time records.
        '''
        raw = self._client.get_insights_leaderboards_year(year)
        return [LeaderboardInsight.model_validate(i) for i in raw]

    def notables(self, year: int) -> list[NotablesInsight]:
        '''
        Notable achievements for a season (e.g. "undefeated in quals").
        Use year=0 for all-time.
        '''
        raw = self._client.get_insights_notables_year(year)
        return [NotablesInsight.model_validate(i) for i in raw]

    def insights_v2(
        self, year: int, category: str | None = None
    ) -> list[InsightV2Leaderboard | InsightV2Streak | InsightV2Timeseries]:
        '''
        Structured InsightV2 objects (leaderboard / streak / timeseries).
        Pass category="leaderboard", "streak", or "timeseries" to filter.
        Use year=0 for all-time.
        '''
        from tba_schemas import InsightV2Leaderboard, InsightV2Streak, InsightV2Timeseries

        _map = {
            "leaderboard": InsightV2Leaderboard,
            "streak":      InsightV2Streak,
            "timeseries":  InsightV2Timeseries,
        }

        raw = (
            self._client.get_insights_v2_year_category(year, category)
            if category
            else self._client.get_insights_v2_year(year)
        )

        results = []
        for item in raw:
            cat = item.get("category")
            model = _map.get(cat)
            if model:
                results.append(model.model_validate(item))
        return results