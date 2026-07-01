'''
bluealliance
============
Python client for The Blue Alliance API v3.

Quick start::

    from bluealliance import TBACollector

    c = TBACollector("YOUR_TBA_KEY")
    team  = c.team("frc7563")
    print(team.nickname, team.city)

    bundle = c.event_bundle("2025spbra")
    for match, bd in c.event_matches_2025("2025spbra"):
        if bd:
            print(bd.red.autoCoralPoints, bd.blue.totalPoints)

Low-level access (raw HTTP client)::

    from bluealliance import TBAClient

    client = TBAClient("YOUR_TBA_KEY")
    raw = client.get_event_matches("2025spbra")   # returns list[dict]

Pydantic models are importable directly::

    from bluealliance.schemas import Team, Match, Event, ScoreBreakdown2025
'''

__version__ = "0.1.0"

from bluealliance.client import TBAClient
from bluealliance.collector import EventBundle, TBACollector, TeamSeasonSummary
from bluealliance.schemas import (
    # enums
    AllianceColor,
    AutoLine2025,
    CompLevel,
    DoubleElimRound,
    EndGameRobot2025,
    EventType,
    PlayoffType,
    WebcastStatus,
    # shared
    APIStatus,
    Award,
    AwardRecipient,
    District,
    DistrictAdvancement,
    WLTRecord,
    Webcast,
    # team
    Team,
    TeamHistory,
    TeamRobot,
    TeamSimple,
    # event
    Event,
    EventDistrictPoints,
    EventOPRs,
    EventRanking,
    EventSimple,
    # match
    Match,
    MatchAlliance,
    MatchSimple,
    MatchVideo,
    # score breakdown 2025
    ReefRow2025,
    ReefSection2025,
    ScoreBreakdown2025,
    ScoreBreakdown2025Alliance,
    parse_score_breakdown_2025,
    # alliances / status
    EliminationAlliance,
    TeamEventStatus,
    # districts / regional
    DistrictRanking,
    RegionalAdvancement,
    RegionalRanking,
    # insights
    LeaderboardInsight,
    NotablesInsight,
    # zebra
    Zebra,
)

__all__ = [
    "__version__",
    # clients
    "TBAClient",
    "TBACollector",
    # bundles
    "EventBundle",
    "TeamSeasonSummary",
    # enums
    "AllianceColor",
    "AutoLine2025",
    "CompLevel",
    "DoubleElimRound",
    "EndGameRobot2025",
    "EventType",
    "PlayoffType",
    "WebcastStatus",
    # models
    "APIStatus",
    "Award",
    "AwardRecipient",
    "District",
    "DistrictAdvancement",
    "DistrictRanking",
    "EliminationAlliance",
    "Event",
    "EventDistrictPoints",
    "EventOPRs",
    "EventRanking",
    "EventSimple",
    "LeaderboardInsight",
    "Match",
    "MatchAlliance",
    "MatchSimple",
    "MatchVideo",
    "NotablesInsight",
    "ReefRow2025",
    "ReefSection2025",
    "RegionalAdvancement",
    "RegionalRanking",
    "ScoreBreakdown2025",
    "ScoreBreakdown2025Alliance",
    "Team",
    "TeamEventStatus",
    "TeamHistory",
    "TeamRobot",
    "TeamSimple",
    "Webcast",
    "WLTRecord",
    "Zebra",
    # helpers
    "parse_score_breakdown_2025",
]
