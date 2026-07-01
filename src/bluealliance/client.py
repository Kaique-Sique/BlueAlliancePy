'''
bluealliance.client
===================
Raw HTTP client for The Blue Alliance API v3.
Covers every endpoint in the OpenAPI 3.15.0 spec.
Returns plain dicts/lists -- no Pydantic parsing.
Use TBACollector for typed, schema-validated responses.

Example::

    from bluealliance import TBAClient

    client = TBAClient("YOUR_TBA_KEY")
    team = client.get_team("frc7563")
    matches = client.get_event_matches("2025arc")
'''

import requests


class TBAClient:

    def __init__(self, TBA_KEY: str, TBA_BASE_URL: str = "https://www.thebluealliance.com/api/v3"):
        self._session = requests.Session()
        self._session.headers.update({
            "X-TBA-Auth-Key": TBA_KEY,
            "Accept": "application/json",
        })

        self.TBA_BASE_URL = TBA_BASE_URL

    def _get(self, path: str, **params) -> dict | list | None:
        '''
        Performs a GET request against the TBA API and returns parsed JSON.
        Raises requests.HTTPError on non-2xx responses.

        :param path: Path appended to TBA_BASE_URL (e.g. "/event/2025arc/matches").
        :param params: Optional query parameters.
        :return: Parsed JSON response body.
        '''

        url = f"{self.TBA_BASE_URL}{path}"
        filtered = {k: v for k, v in params.items() if v is not None}
        response = self._session.get(url, params=filtered or None)
        response.raise_for_status()
        return response.json()


    # =========================================================
    # TBA
    # =========================================================

    def get_status(self) -> dict:
        '''Returns API status and TBA status information. GET /status'''
        return self._get("/status")

    def get_search_index(self) -> dict:
        '''Gets the large search index blob used on the TBA frontend. GET /search_index'''
        return self._get("/search_index")


    # =========================================================
    # TEAMS  (paginated -- /teams/{page_num})
    # =========================================================

    def get_teams(self, page_num: int) -> list:
        '''Gets a list of Team objects, paginated in groups of 500. GET /teams/{page_num}'''
        return self._get(f"/teams/{page_num}")

    def get_teams_simple(self, page_num: int) -> list:
        '''Short-form Team_Simple list, paginated. GET /teams/{page_num}/simple'''
        return self._get(f"/teams/{page_num}/simple")

    def get_teams_keys(self, page_num: int) -> list:
        '''Team key list, paginated. GET /teams/{page_num}/keys'''
        return self._get(f"/teams/{page_num}/keys")

    def get_teams_by_year(self, year: int, page_num: int) -> list:
        '''Teams that competed in a given year, paginated. GET /teams/{year}/{page_num}'''
        return self._get(f"/teams/{year}/{page_num}")

    def get_teams_by_year_simple(self, year: int, page_num: int) -> list:
        '''Short-form teams that competed in a given year, paginated. GET /teams/{year}/{page_num}/simple'''
        return self._get(f"/teams/{year}/{page_num}/simple")

    def get_teams_by_year_keys(self, year: int, page_num: int) -> list:
        '''Team keys for a given year, paginated. GET /teams/{year}/{page_num}/keys'''
        return self._get(f"/teams/{year}/{page_num}/keys")


    # =========================================================
    # TEAM  (single team)
    # =========================================================

    def get_team(self, team_key: str) -> dict:
        '''Gets a Team object. GET /team/{team_key}'''
        return self._get(f"/team/{team_key}")

    def get_team_simple(self, team_key: str) -> dict:
        '''Short-form Team_Simple object. GET /team/{team_key}/simple'''
        return self._get(f"/team/{team_key}/simple")

    def get_team_years_participated(self, team_key: str) -> list:
        '''Years the team competed in at least one event. GET /team/{team_key}/years_participated'''
        return self._get(f"/team/{team_key}/years_participated")

    def get_team_districts(self, team_key: str) -> list:
        '''Districts the team has participated in, by year. GET /team/{team_key}/districts'''
        return self._get(f"/team/{team_key}/districts")

    def get_team_robots(self, team_key: str) -> list:
        '''Year/robot-name pairs for every year the team named a robot. GET /team/{team_key}/robots'''
        return self._get(f"/team/{team_key}/robots")

    def get_team_history(self, team_key: str) -> dict:
        '''Full team history including events and awards. GET /team/{team_key}/history'''
        return self._get(f"/team/{team_key}/history")

    def get_team_social_media(self, team_key: str) -> list:
        '''Social media objects for the team. GET /team/{team_key}/social_media'''
        return self._get(f"/team/{team_key}/social_media")

    def get_team_awards(self, team_key: str) -> list:
        '''All awards the team has won (all time). GET /team/{team_key}/awards'''
        return self._get(f"/team/{team_key}/awards")

    def get_team_awards_by_year(self, team_key: str, year: int) -> list:
        '''Awards the team won in a specific year. GET /team/{team_key}/awards/{year}'''
        return self._get(f"/team/{team_key}/awards/{year}")

    def get_team_media_by_year(self, team_key: str, year: int) -> list:
        '''Media objects for the team in a given year. GET /team/{team_key}/media/{year}'''
        return self._get(f"/team/{team_key}/media/{year}")

    def get_team_media_by_tag(self, team_key: str, media_tag: str) -> list:
        '''Media for the team filtered by tag. GET /team/{team_key}/media/tag/{media_tag}'''
        return self._get(f"/team/{team_key}/media/tag/{media_tag}")

    def get_team_media_by_tag_year(self, team_key: str, media_tag: str, year: int) -> list:
        '''Media for the team filtered by tag and year. GET /team/{team_key}/media/tag/{media_tag}/{year}'''
        return self._get(f"/team/{team_key}/media/tag/{media_tag}/{year}")

    # Team events (all years)
    def get_team_events(self, team_key: str) -> list:
        '''All events this team has competed at (all time). GET /team/{team_key}/events'''
        return self._get(f"/team/{team_key}/events")

    def get_team_events_simple(self, team_key: str) -> list:
        '''Short-form events this team has competed at (all time). GET /team/{team_key}/events/simple'''
        return self._get(f"/team/{team_key}/events/simple")

    def get_team_events_keys(self, team_key: str) -> list:
        '''Event keys for all events this team has competed at. GET /team/{team_key}/events/keys'''
        return self._get(f"/team/{team_key}/events/keys")

    # Team events (by year)
    def get_team_events_by_year(self, team_key: str, year: int) -> list:
        '''Events this team competed at in a given year. GET /team/{team_key}/events/{year}'''
        return self._get(f"/team/{team_key}/events/{year}")

    def get_team_events_by_year_simple(self, team_key: str, year: int) -> list:
        '''Short-form events this team competed at in a given year. GET /team/{team_key}/events/{year}/simple'''
        return self._get(f"/team/{team_key}/events/{year}/simple")

    def get_team_events_by_year_keys(self, team_key: str, year: int) -> list:
        '''Event keys for events this team competed at in a given year. GET /team/{team_key}/events/{year}/keys'''
        return self._get(f"/team/{team_key}/events/{year}/keys")

    def get_team_events_statuses_by_year(self, team_key: str, year: int) -> dict:
        '''Key-value map of Team_Event_Status for each event in a given year. GET /team/{team_key}/events/{year}/statuses'''
        return self._get(f"/team/{team_key}/events/{year}/statuses")

    # Team matches
    def get_team_event_matches(self, team_key: str, event_key: str) -> list:
        '''Matches for the team at a specific event. GET /team/{team_key}/event/{event_key}/matches'''
        return self._get(f"/team/{team_key}/event/{event_key}/matches")

    def get_team_event_matches_simple(self, team_key: str, event_key: str) -> list:
        '''Short-form matches for the team at a specific event. GET /team/{team_key}/event/{event_key}/matches/simple'''
        return self._get(f"/team/{team_key}/event/{event_key}/matches/simple")

    def get_team_event_matches_keys(self, team_key: str, event_key: str) -> list:
        '''Match keys for the team at a specific event. GET /team/{team_key}/event/{event_key}/matches/keys'''
        return self._get(f"/team/{team_key}/event/{event_key}/matches/keys")

    def get_team_matches_by_year(self, team_key: str, year: int) -> list:
        '''All matches for the team in a given year. GET /team/{team_key}/matches/{year}'''
        return self._get(f"/team/{team_key}/matches/{year}")

    def get_team_matches_by_year_simple(self, team_key: str, year: int) -> list:
        '''Short-form matches for the team in a given year. GET /team/{team_key}/matches/{year}/simple'''
        return self._get(f"/team/{team_key}/matches/{year}/simple")

    def get_team_matches_by_year_keys(self, team_key: str, year: int) -> list:
        '''Match keys for the team in a given year. GET /team/{team_key}/matches/{year}/keys'''
        return self._get(f"/team/{team_key}/matches/{year}/keys")

    # Team event-specific
    def get_team_event_awards(self, team_key: str, event_key: str) -> list:
        '''Awards the team won at a specific event. GET /team/{team_key}/event/{event_key}/awards'''
        return self._get(f"/team/{team_key}/event/{event_key}/awards")

    def get_team_event_status(self, team_key: str, event_key: str) -> dict | None:
        '''Competition rank and status for the team at a specific event. GET /team/{team_key}/event/{event_key}/status'''
        return self._get(f"/team/{team_key}/event/{event_key}/status")


    # =========================================================
    # EVENTS  (by year)
    # =========================================================

    def get_events_by_year(self, year: int) -> list:
        '''All events in a given year. GET /events/{year}'''
        return self._get(f"/events/{year}")

    def get_events_by_year_simple(self, year: int) -> list:
        '''Short-form events in a given year. GET /events/{year}/simple'''
        return self._get(f"/events/{year}/simple")

    def get_events_by_year_keys(self, year: int) -> list:
        '''Event keys for a given year. GET /events/{year}/keys'''
        return self._get(f"/events/{year}/keys")


    # =========================================================
    # EVENT  (single event)
    # =========================================================

    def get_event(self, event_key: str) -> dict:
        '''Gets an Event object. GET /event/{event_key}'''
        return self._get(f"/event/{event_key}")

    def get_event_simple(self, event_key: str) -> dict:
        '''Short-form Event_Simple object. GET /event/{event_key}/simple'''
        return self._get(f"/event/{event_key}/simple")

    def get_event_alliances(self, event_key: str) -> list | None:
        '''Elimination alliances for the event. GET /event/{event_key}/alliances'''
        return self._get(f"/event/{event_key}/alliances")

    def get_event_awards(self, event_key: str) -> list:
        '''Awards from the event. GET /event/{event_key}/awards'''
        return self._get(f"/event/{event_key}/awards")

    def get_event_matches(self, event_key: str) -> list:
        '''All matches for the event. GET /event/{event_key}/matches'''
        return self._get(f"/event/{event_key}/matches")

    def get_event_matches_simple(self, event_key: str) -> list:
        '''Short-form matches for the event. GET /event/{event_key}/matches/simple'''
        return self._get(f"/event/{event_key}/matches/simple")

    def get_event_matches_keys(self, event_key: str) -> list:
        '''Match keys for the event. GET /event/{event_key}/matches/keys'''
        return self._get(f"/event/{event_key}/matches/keys")

    def get_event_match_timeseries(self, event_key: str) -> list:
        '''Match keys that have Zebra timeseries data at this event. GET /event/{event_key}/matches/timeseries'''
        return self._get(f"/event/{event_key}/matches/timeseries")

    def get_event_rankings(self, event_key: str) -> dict | None:
        '''Team rankings for the event. GET /event/{event_key}/rankings'''
        return self._get(f"/event/{event_key}/rankings")

    def get_event_oprs(self, event_key: str) -> dict | None:
        '''OPR, DPR, and CCWM for teams at the event. GET /event/{event_key}/oprs'''
        return self._get(f"/event/{event_key}/oprs")

    def get_event_coprs(self, event_key: str) -> dict | None:
        '''Component OPRs for teams at the event. GET /event/{event_key}/coprs'''
        return self._get(f"/event/{event_key}/coprs")

    def get_event_district_points(self, event_key: str) -> dict | None:
        '''District points for the event (always calculated, regardless of event type). GET /event/{event_key}/district_points'''
        return self._get(f"/event/{event_key}/district_points")

    def get_event_advancement_points(self, event_key: str) -> dict | None:
        '''District or regional CMP points, depending on event type. GET /event/{event_key}/advancement_points'''
        return self._get(f"/event/{event_key}/advancement_points")

    def get_event_regional_champs_pool_points(self, event_key: str) -> dict | None:
        '''For 2025+ Regional events, points toward the Championship qualification pool. GET /event/{event_key}/regional_champs_pool_points'''
        return self._get(f"/event/{event_key}/regional_champs_pool_points")

    def get_event_insights(self, event_key: str) -> dict | None:
        '''Year-specific event insights (qual and playoff). GET /event/{event_key}/insights'''
        return self._get(f"/event/{event_key}/insights")

    def get_event_predictions(self, event_key: str) -> dict | None:
        '''TBA-generated match predictions for the event. GET /event/{event_key}/predictions'''
        return self._get(f"/event/{event_key}/predictions")

    def get_event_teams(self, event_key: str) -> list:
        '''Team objects for all teams that competed at the event. GET /event/{event_key}/teams'''
        return self._get(f"/event/{event_key}/teams")

    def get_event_teams_simple(self, event_key: str) -> list:
        '''Short-form Team_Simple objects for the event. GET /event/{event_key}/teams/simple'''
        return self._get(f"/event/{event_key}/teams/simple")

    def get_event_teams_keys(self, event_key: str) -> list:
        '''Team keys for the event. GET /event/{event_key}/teams/keys'''
        return self._get(f"/event/{event_key}/teams/keys")

    def get_event_teams_statuses(self, event_key: str) -> dict:
        '''Key-value map of Team_Event_Status for all teams at the event. GET /event/{event_key}/teams/statuses'''
        return self._get(f"/event/{event_key}/teams/statuses")

    def get_event_team_media(self, event_key: str) -> list:
        '''Media objects for all teams at the event. GET /event/{event_key}/team_media'''
        return self._get(f"/event/{event_key}/team_media")


    # =========================================================
    # MATCH  (single match)
    # =========================================================

    def get_match(self, match_key: str) -> dict:
        '''Gets a full Match object. GET /match/{match_key}'''
        return self._get(f"/match/{match_key}")

    def get_match_simple(self, match_key: str) -> dict:
        '''Short-form Match_Simple object. GET /match/{match_key}/simple'''
        return self._get(f"/match/{match_key}/simple")

    def get_match_timeseries(self, match_key: str) -> list:
        '''Game-specific Zebra timeseries data for the match. GET /match/{match_key}/timeseries'''
        return self._get(f"/match/{match_key}/timeseries")

    def get_match_zebra(self, match_key: str) -> dict:
        '''Zebra MotionWorks positional data for the match. GET /match/{match_key}/zebra_motionworks'''
        return self._get(f"/match/{match_key}/zebra_motionworks")


    # =========================================================
    # DISTRICTS
    # =========================================================

    def get_districts_by_year(self, year: int) -> list:
        '''Districts and their keys for a given year. GET /districts/{year}'''
        return self._get(f"/districts/{year}")

    def get_district_events(self, district_key: str) -> list:
        '''Events in a given district. GET /district/{district_key}/events'''
        return self._get(f"/district/{district_key}/events")

    def get_district_events_simple(self, district_key: str) -> list:
        '''Short-form events in a given district. GET /district/{district_key}/events/simple'''
        return self._get(f"/district/{district_key}/events/simple")

    def get_district_events_keys(self, district_key: str) -> list:
        '''Event keys for a given district. GET /district/{district_key}/events/keys'''
        return self._get(f"/district/{district_key}/events/keys")

    def get_district_teams(self, district_key: str) -> list:
        '''Teams that competed in events in the given district. GET /district/{district_key}/teams'''
        return self._get(f"/district/{district_key}/teams")

    def get_district_teams_simple(self, district_key: str) -> list:
        '''Short-form teams for the given district. GET /district/{district_key}/teams/simple'''
        return self._get(f"/district/{district_key}/teams/simple")

    def get_district_teams_keys(self, district_key: str) -> list:
        '''Team keys for the given district. GET /district/{district_key}/teams/keys'''
        return self._get(f"/district/{district_key}/teams/keys")

    def get_district_rankings(self, district_key: str) -> list | None:
        '''Team district rankings for the given district. GET /district/{district_key}/rankings'''
        return self._get(f"/district/{district_key}/rankings")

    def get_district_awards(self, district_key: str) -> list:
        '''All awards in the given district. GET /district/{district_key}/awards'''
        return self._get(f"/district/{district_key}/awards")

    def get_district_advancement(self, district_key: str) -> dict | None:
        '''Advancement information per team in a district. GET /district/{district_key}/advancement'''
        return self._get(f"/district/{district_key}/advancement")

    def get_district_history(self, district_abbreviation: str) -> list:
        '''District objects across all years for a given district abbreviation. GET /district/{district_abbreviation}/history'''
        return self._get(f"/district/{district_abbreviation}/history")

    def get_district_dcmp_history(self, district_abbreviation: str) -> list:
        '''DCMP events and awards for a given district abbreviation. GET /district/{district_abbreviation}/dcmp_history'''
        return self._get(f"/district/{district_abbreviation}/dcmp_history")

    def get_district_insights(self, district_abbreviation: str) -> dict:
        '''Insights for a given district. GET /district/{district_abbreviation}/insights'''
        return self._get(f"/district/{district_abbreviation}/insights")


    # =========================================================
    # INSIGHTS
    # =========================================================

    def get_insights_leaderboards_year(self, year: int) -> list:
        '''LeaderboardInsight objects for a year (year=0 for all-time). GET /insights/leaderboards/{year}'''
        return self._get(f"/insights/leaderboards/{year}")

    def get_insights_notables_year(self, year: int) -> list:
        '''NotablesInsight objects for a year (year=0 for all-time). GET /insights/notables/{year}'''
        return self._get(f"/insights/notables/{year}")

    def get_insights_v2_year(self, year: int) -> list:
        '''All InsightV2 objects for a year across all categories (year=0 for all-time). GET /insights/{year}'''
        return self._get(f"/insights/{year}")

    def get_insights_v2_year_category(self, year: int, category: str) -> list:
        '''InsightV2 objects for a year filtered by category (leaderboard/streak/timeseries). GET /insights/{year}/{category}'''
        return self._get(f"/insights/{year}/{category}")

    def get_insights_v2_year_district(self, year: int, district_abbreviation: str) -> list:
        '''InsightV2 objects for a year scoped to a district across all categories. GET /insights/{year}/district/{district_abbreviation}'''
        return self._get(f"/insights/{year}/district/{district_abbreviation}")

    def get_insights_v2_year_category_district(self, year: int, category: str, district_abbreviation: str) -> list:
        '''InsightV2 objects for a year, category, and district. GET /insights/{year}/{category}/district/{district_abbreviation}'''
        return self._get(f"/insights/{year}/{category}/district/{district_abbreviation}")


    # =========================================================
    # REGIONAL ADVANCEMENT
    # =========================================================

    def get_regional_advancement(self, year: int) -> dict | None:
        '''Per-team advancement information to the FIRST Championship. GET /regional_advancement/{year}'''
        return self._get(f"/regional_advancement/{year}")

    def get_regional_rankings(self, year: int) -> list | None:
        '''Team rankings in the regional pool for a specific year. GET /regional_advancement/{year}/rankings'''
        return self._get(f"/regional_advancement/{year}/rankings")