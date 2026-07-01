'''
TBA API v3 - Pydantic Schemas
==============================
Response models for every type returned by the TBA API v3 endpoints.
Based on OpenAPI spec 3.15.0.

Usage with tba_client.py:
    from tba_client import TBAClient
    from tba_schemas import Team, Match, Event, EventRanking

    client = TBAClient()

    raw = client.get_team("frc7563")
    team = Team.model_validate(raw)
    print(team.nickname, team.city)

    raw_matches = client.get_event_matches("2025spbra")
    matches = [Match.model_validate(m) for m in raw_matches]

    raw_ranking = client.get_event_rankings("2025spbra")
    ranking = EventRanking.model_validate(raw_ranking)
'''

from __future__ import annotations
from enum import IntEnum, StrEnum
from typing import Annotated, Any, Literal
from pydantic import BaseModel, Field


# =============================================================================
# ENUMS
# =============================================================================

class AllianceColor(StrEnum):
    RED      = "red"
    BLUE     = "blue"
    NO_WINNER = ""


class CompLevel(StrEnum):
    QM = "qm"   # qualification
    EF = "ef"   # eighths-final
    QF = "qf"   # quarter-final
    SF = "sf"   # semi-final
    F  = "f"    # final


class WebcastStatus(StrEnum):
    UNKNOWN = "unknown"
    ONLINE  = "online"
    OFFLINE = "offline"


class EventType(IntEnum):
    REGIONAL            = 0
    DISTRICT            = 1
    DISTRICT_CMP        = 2
    CMP_DIVISION        = 3
    CMP_FINALS          = 4
    DISTRICT_CMP_DIV    = 5
    FOC                 = 6
    REMOTE              = 7
    OFFSEASON           = 99
    PRESEASON           = 100
    UNLABELED           = -1


class PlayoffType(IntEnum):
    BRACKET_16_TEAM          = 1
    BRACKET_8_TEAM           = 0
    BRACKET_4_TEAM           = 2
    BRACKET_2_TEAM           = 9
    AVG_SCORE_8_TEAM         = 3
    ROUND_ROBIN_6_TEAM       = 4
    LEGACY_DOUBLE_ELIM_8     = 5
    DOUBLE_ELIM_8_TEAM       = 10
    DOUBLE_ELIM_4_TEAM       = 11
    BO5_FINALS               = 6
    BO3_FINALS               = 7
    CUSTOM                   = 8


class DoubleElimRound(StrEnum):
    FINALS   = "Finals"
    ROUND_1  = "Round 1"
    ROUND_2  = "Round 2"
    ROUND_3  = "Round 3"
    ROUND_4  = "Round 4"
    ROUND_5  = "Round 5"


class EndGameRobot2025(StrEnum):
    DEEP_CAGE   = "DeepCage"
    NONE        = "None"
    PARKED      = "Parked"
    SHALLOW_CAGE = "ShallowCage"


class AutoLine2025(StrEnum):
    NO  = "No"
    YES = "Yes"


# =============================================================================
# SHARED / PRIMITIVE MODELS
# =============================================================================

class WLTRecord(BaseModel):
    wins:   int
    losses: int
    ties:   int


class Webcast(BaseModel):
    type:         str
    channel:      str
    date:         str | None = None
    file:         str | None = None
    status:       WebcastStatus | None = None
    stream_title: str | None = None
    viewer_count: int | None = None


class AppVersion(BaseModel):
    min_app_version:    int
    latest_app_version: int


class APIStatus(BaseModel):
    current_season:   int
    max_season:       int
    is_datafeed_down: bool
    down_events:      list[str]
    ios:              AppVersion
    android:          AppVersion
    max_team_page:    int


# =============================================================================
# DISTRICT
# =============================================================================

class DistrictAdvancementCounts(BaseModel):
    dcmp: int
    cmp:  int


class District(BaseModel):
    abbreviation:              str
    display_name:              str
    key:                       str
    year:                      int
    official_advancement_counts: DistrictAdvancementCounts


# =============================================================================
# AWARD
# =============================================================================

class AwardRecipient(BaseModel):
    team_key: str | None = None
    awardee:  str | None = None


class Award(BaseModel):
    name:           str
    award_type:     int
    event_key:      str
    recipient_list: list[AwardRecipient]
    year:           int


# =============================================================================
# TEAM
# =============================================================================

class TeamSimple(BaseModel):
    key:        str
    team_number: int
    nickname:   str
    name:       str
    city:       str | None = None
    state_prov: str | None = None
    country:    str | None = None


class Team(BaseModel):
    key:         str
    team_number: int
    nickname:    str
    name:        str
    school_name: str | None = None
    city:        str | None = None
    state_prov:  str | None = None
    country:     str | None = None
    address:     str | None = None
    postal_code: str | None = None
    website:     str | None = None
    rookie_year: int | None = None
    motto:       str | None = None

    # deprecated -- will return null per spec v3.11
    gmaps_place_id: str | None = None
    gmaps_url:      str | None = None
    lat:            float | None = None
    lng:            float | None = None
    location_name:  str | None = None


class TeamRobot(BaseModel):
    year:       int
    robot_name: str
    key:        str
    team_key:   str


# =============================================================================
# MEDIA
# =============================================================================

class MediaBase(BaseModel):
    type:        str
    foreign_key: str
    team_keys:   list[str]
    preferred:   bool | None = None
    direct_url:  str | None = None
    view_url:    str | None = None


class MediaNoDetails(MediaBase):
    details: dict[str, Any] | None = None


class MediaAvatar(MediaBase):
    type:    Literal["avatar"]
    details: dict[str, str] | None = None  # {"base64Image": "..."}


class MediaCdPhotoThread(MediaBase):
    type:    Literal["cdphotothread"]
    details: dict[str, str] | None = None  # {"image_partial": "..."}


class MediaCdThread(MediaBase):
    type:    Literal["cd-thread"]
    details: dict[str, Any] | None = None  # {"thread_title": "...", "image_url": ...}


class MediaGrabCad(MediaBase):
    type:    Literal["grabcad"]
    details: dict[str, Any] | None = None  # {"model_name", "model_image", ...}


class MediaOnshape(MediaBase):
    type:    Literal["onshape"]
    details: dict[str, Any] | None = None


# Union covering all media types -- use model_validate on the raw dict
Media = (
    MediaAvatar
    | MediaCdPhotoThread
    | MediaCdThread
    | MediaGrabCad
    | MediaOnshape
    | MediaNoDetails
)


# =============================================================================
# EVENT
# =============================================================================

class EventSimple(BaseModel):
    key:               str
    name:              str
    event_code:        str
    event_type:        EventType
    district:          District | None = None
    city:              str | None = None
    state_prov:        str | None = None
    country:           str | None = None
    start_date:        str
    end_date:          str
    year:              int


class Event(BaseModel):
    key:                str
    name:               str
    event_code:         str
    event_type:         EventType
    district:           District | None = None
    city:               str | None = None
    state_prov:         str | None = None
    country:            str | None = None
    start_date:         str
    end_date:           str
    year:               int
    short_name:         str | None = None
    event_type_string:  str
    week:               int | None = None
    address:            str | None = None
    postal_code:        str | None = None
    timezone:           str | None = None
    website:            str | None = None
    first_event_id:     str | None = None
    first_event_code:   str | None = None
    webcasts:           list[Webcast] = Field(default_factory=list)
    division_keys:      list[str] = Field(default_factory=list)
    parent_event_key:   str | None = None
    playoff_type:       PlayoffType | None = None
    playoff_type_string: str | None = None
    remap_teams:        dict[str, str] | None = None

    # deprecated per spec v3.11 -- returns null
    gmaps_place_id: str | None = None
    gmaps_url:      str | None = None
    lat:            float | None = None
    lng:            float | None = None
    location_name:  str | None = None


# =============================================================================
# MATCH
# =============================================================================

class MatchAlliance(BaseModel):
    score:              int
    team_keys:          list[str]
    surrogate_team_keys: list[str] = Field(default_factory=list)
    dq_team_keys:       list[str] = Field(default_factory=list)


class MatchAlliances(BaseModel):
    red:  MatchAlliance
    blue: MatchAlliance


class MatchVideo(BaseModel):
    type: str  # 'youtube' | 'tba'
    key:  str


class Match(BaseModel):
    key:              str
    comp_level:       CompLevel
    set_number:       int
    match_number:     int
    alliances:        MatchAlliances
    winning_alliance: AllianceColor
    event_key:        str
    time:             int | None = None
    actual_time:      int | None = None
    predicted_time:   int | None = None
    post_result_time: int | None = None
    score_breakdown:  dict[str, Any] | None = None  # year-specific, stored as JSONB
    videos:           list[MatchVideo] = Field(default_factory=list)


class MatchSimple(BaseModel):
    key:              str
    comp_level:       CompLevel
    set_number:       int
    match_number:     int
    alliances:        MatchAlliances
    winning_alliance: AllianceColor
    event_key:        str
    time:             int | None = None
    predicted_time:   int | None = None
    actual_time:      int | None = None


# =============================================================================
# SCORE BREAKDOWN 2025 (Reefscape)
# =============================================================================

class ReefRow2025(BaseModel):
    nodeA: bool
    nodeB: bool
    nodeC: bool
    nodeD: bool
    nodeE: bool
    nodeF: bool
    nodeG: bool
    nodeH: bool
    nodeI: bool
    nodeJ: bool
    nodeK: bool
    nodeL: bool


class ReefSection2025(BaseModel):
    topRow: ReefRow2025
    midRow: ReefRow2025
    botRow: ReefRow2025
    trough: int
    tba_botRowCount: int | None = None
    tba_midRowCount: int | None = None
    tba_topRowCount: int | None = None


class ScoreBreakdown2025Alliance(BaseModel):
    # Auto
    autoLineRobot1:       AutoLine2025
    autoLineRobot2:       AutoLine2025
    autoLineRobot3:       AutoLine2025
    autoMobilityPoints:   int
    autoCoralCount:       int
    autoCoralPoints:      int
    autoReef:             ReefSection2025
    autoPoints:           int

    # Teleop
    teleopCoralCount:  int
    teleopCoralPoints: int
    teleopReef:        ReefSection2025
    teleopPoints:      int

    # Algae
    netAlgaeCount:  int
    wallAlgaeCount: int
    algaePoints:    int

    # Endgame
    endGameRobot1:      EndGameRobot2025
    endGameRobot2:      EndGameRobot2025
    endGameRobot3:      EndGameRobot2025
    endGameBargePoints: int

    # Ranking / bonus flags
    rp:                     int
    autoBonusAchieved:      bool | None = None
    bargeBonusAchieved:     bool | None = None
    coralBonusAchieved:     bool | None = None
    coopertitionCriteriaMet: bool | None = None

    # Fouls / penalties
    foulCount:    int
    techFoulCount: int
    foulPoints:   int
    g206Penalty:  bool
    g410Penalty:  bool
    g418Penalty:  bool
    g428Penalty:  bool

    adjustPoints: int | None = None
    totalPoints:  int


class ScoreBreakdown2025(BaseModel):
    red:  ScoreBreakdown2025Alliance
    blue: ScoreBreakdown2025Alliance


# =============================================================================
# EVENT RANKINGS & STATS
# =============================================================================

class RankingSortOrderInfo(BaseModel):
    name:      str
    precision: int


class RankingEntry(BaseModel):
    team_key:       str
    rank:           int
    matches_played: int
    qual_average:   float | None = None
    sort_orders:    list[float] | None = None
    extra_stats:    list[float] = Field(default_factory=list)
    record:         WLTRecord | None = None
    dq:             int


class EventRanking(BaseModel):
    rankings:        list[RankingEntry]
    sort_order_info: list[RankingSortOrderInfo] | None = None
    extra_stats_info: list[RankingSortOrderInfo] = Field(default_factory=list)


class EventOPRs(BaseModel):
    oprs:  dict[str, float] = Field(default_factory=dict)  # team_key -> OPR
    dprs:  dict[str, float] = Field(default_factory=dict)  # team_key -> DPR
    ccwms: dict[str, float] = Field(default_factory=dict)  # team_key -> CCWM


# Component OPRs: outer key = component name, inner key = team_key
EventCOPRs = dict[str, dict[str, float]]


class DistrictPointEntry(BaseModel):
    total:           int
    qual_points:     int
    elim_points:     int
    alliance_points: int
    award_points:    int


class EventDistrictPoints(BaseModel):
    points:     dict[str, DistrictPointEntry]   # team_key -> points
    tiebreakers: dict[str, Any] | None = None


# =============================================================================
# ELIMINATION ALLIANCES
# =============================================================================

class AllianceBackup(BaseModel):
    out: str  # team key replaced
    in_: str = Field(alias="in")  # backup called in

    model_config = {"populate_by_name": True}


class AllianceStatus(BaseModel):
    playoff_average:              float | None = None
    playoff_type:                 PlayoffType | None = None
    level:                        CompLevel
    record:                       WLTRecord | None = None
    current_level_record:         WLTRecord | None = None
    status:                       str  # 'won' | 'eliminated' | 'playing'
    advanced_to_round_robin_finals: bool | None = None
    double_elim_round:            DoubleElimRound | None = None
    round_robin_rank:             int | None = None


class EliminationAlliance(BaseModel):
    name:    str | None = None
    backup:  AllianceBackup | None = None
    declines: list[str] = Field(default_factory=list)
    picks:   list[str]
    status:  AllianceStatus | None = None


# =============================================================================
# TEAM EVENT STATUS
# =============================================================================

class TeamEventStatusAlliance(BaseModel):
    name:   str | None = None
    number: int
    pick:   int
    backup: dict[str, str] | None = None


class TeamEventStatusPlayoff(BaseModel):
    level:                CompLevel | None = None
    current_level_record: WLTRecord | None = None
    record:               WLTRecord | None = None
    status:               str | None = None
    playoff_average:      float | None = None


class TeamEventStatusRankingEntry(BaseModel):
    team_key:       str
    rank:           int | None = None
    matches_played: int | None = None
    qual_average:   float | None = None
    sort_orders:    list[float] | None = None
    record:         WLTRecord | None = None
    dq:             int | None = None


class TeamEventStatusRank(BaseModel):
    num_teams:      int | None = None
    ranking:        TeamEventStatusRankingEntry | None = None
    sort_order_info: list[RankingSortOrderInfo] | None = None
    status:         str | None = None


class TeamEventStatus(BaseModel):
    qual:               TeamEventStatusRank | None = None
    alliance:           TeamEventStatusAlliance | None = None
    playoff:            TeamEventStatusPlayoff | None = None
    alliance_status_str: str | None = None
    playoff_status_str: str | None = None
    overall_status_str: str | None = None
    next_match_key:     str | None = None
    last_match_key:     str | None = None
    pit_location:       str | None = None


# =============================================================================
# DISTRICT MODELS
# =============================================================================

class DistrictRankingEventPoints(BaseModel):
    event_key:       str
    district_cmp:    bool
    total:           int
    qual_points:     int
    elim_points:     int
    alliance_points: int
    award_points:    int


class DistrictRanking(BaseModel):
    team_key:     str
    rank:         int
    rookie_bonus: int
    point_total:  int
    event_points: list[DistrictRankingEventPoints]
    adjustments:  int | None = None
    other_bonus:  int | None = None


class DistrictAdvancement(BaseModel):
    dcmp: bool
    cmp:  bool


# =============================================================================
# REGIONAL ADVANCEMENT (2025+)
# =============================================================================

class RegionalAdvancement(BaseModel):
    cmp:                    bool
    cmp_status:             str  # NotInvited|PreQualified|EventQualified|PoolQualified|Declined
    qualifying_event:       str | None = None
    qualifying_award_name:  str | None = None
    qualifying_pool_week:   int | None = None


class RegionalRankingEventPoints(BaseModel):
    event_key:       str
    total:           int
    qual_points:     int
    elim_points:     int
    alliance_points: int
    award_points:    int


class RegionalRanking(BaseModel):
    team_key:          str
    rank:              int
    point_total:       int
    rookie_bonus:      int | None = None
    single_event_bonus: int | None = None
    event_points:      list[RegionalRankingEventPoints] = Field(default_factory=list)


# =============================================================================
# ZEBRA MOTIONWORKS
# =============================================================================

class ZebraTeam(BaseModel):
    team_key: str
    xs: list[float | None]
    ys: list[float | None]


class ZebraAlliances(BaseModel):
    red:  list[ZebraTeam] = Field(default_factory=list)
    blue: list[ZebraTeam] = Field(default_factory=list)


class Zebra(BaseModel):
    key:      str
    times:    list[float]
    alliances: ZebraAlliances


# =============================================================================
# INSIGHTS
# =============================================================================

class LeaderboardInsightRanking(BaseModel):
    value: float
    keys:  list[str]


class LeaderboardInsightData(BaseModel):
    rankings: list[LeaderboardInsightRanking]
    key_type: str  # 'team' | 'event' | 'match'


class LeaderboardInsight(BaseModel):
    name: str
    year: int
    data: LeaderboardInsightData


class NotablesInsightEntry(BaseModel):
    team_key: str
    context:  list[str]


class NotablesInsightData(BaseModel):
    entries: list[NotablesInsightEntry]


class NotablesInsight(BaseModel):
    name: str
    year: int
    data: NotablesInsightData


class InsightV2Leaderboard(BaseModel):
    name:                  str
    display_name:          str
    year:                  int
    category:              Literal["leaderboard"]
    district_abbreviation: str | None = None
    data:                  dict[str, Any]


class InsightV2Streak(BaseModel):
    name:                  str
    display_name:          str
    year:                  int
    category:              Literal["streak"]
    district_abbreviation: str | None = None
    data:                  dict[str, Any]


class InsightV2Timeseries(BaseModel):
    name:                  str
    display_name:          str
    year:                  int
    category:              Literal["timeseries"]
    district_abbreviation: str | None = None
    data:                  dict[str, Any]


InsightV2 = Annotated[
    InsightV2Leaderboard | InsightV2Streak | InsightV2Timeseries,
    Field(discriminator="category"),
]


# =============================================================================
# HISTORY
# =============================================================================

class TeamHistory(BaseModel):
    events: list[Event]
    awards: list[Award]


# =============================================================================
# SEARCH INDEX
# =============================================================================

class SearchIndexTeam(BaseModel):
    key:      str
    nickname: str


class SearchIndexEvent(BaseModel):
    key:  str
    name: str


class SearchIndex(BaseModel):
    teams:  list[SearchIndexTeam]
    events: list[SearchIndexEvent]


# =============================================================================
# HELPERS
# =============================================================================

def parse_score_breakdown_2025(raw: dict[str, Any] | None) -> ScoreBreakdown2025 | None:
    '''
    Parses the year-specific score_breakdown field from a Match object when
    the match is from the 2025 Reefscape season. Returns None if the raw
    breakdown is absent.

    Usage:
        match = Match.model_validate(raw_match)
        breakdown = parse_score_breakdown_2025(match.score_breakdown)
        if breakdown:
            print(breakdown.red.autoCoralPoints)
    '''
    if raw is None:
        return None
    return ScoreBreakdown2025.model_validate(raw)