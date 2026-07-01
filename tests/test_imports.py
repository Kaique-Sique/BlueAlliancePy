'''Basic import and instantiation tests -- no network required.'''

def test_package_imports():
    from bluealliance import TBAClient, TBACollector
    from bluealliance import Team, Match, Event, ScoreBreakdown2025
    from bluealliance import AllianceColor, CompLevel, EventType
    assert TBAClient is not None
    assert TBACollector is not None


def test_client_instantiation():
    from bluealliance import TBAClient
    c = TBAClient("dummy_key")
    assert c is not None


def test_collector_instantiation():
    from bluealliance import TBACollector
    c = TBACollector("dummy_key")
    assert c is not None


def test_schema_model_validate():
    from bluealliance import Team
    team = Team.model_validate({
        "key": "frc7563",
        "team_number": 7563,
        "nickname": "Megazord",
        "name": "FRC Team 7563",
        "city": "Jundiai",
        "state_prov": "SP",
        "country": "Brazil",
        "rookie_year": 2019,
        "motto": None,
        "school_name": None,
        "address": None,
        "postal_code": None,
        "website": None,
        "gmaps_place_id": None,
        "gmaps_url": None,
        "lat": None,
        "lng": None,
        "location_name": None,
    })
    assert team.team_number == 7563
    assert team.nickname == "Megazord"
    assert team.city == "Jundiai"


def test_score_breakdown_2025():
    from bluealliance import parse_score_breakdown_2025

    alliance = {
        "autoLineRobot1": "Yes", "autoLineRobot2": "No", "autoLineRobot3": "Yes",
        "autoMobilityPoints": 6, "autoCoralCount": 3, "autoCoralPoints": 15,
        "autoReef": {
            "topRow": {f"node{c}": False for c in "ABCDEFGHIJKL"},
            "midRow": {f"node{c}": False for c in "ABCDEFGHIJKL"},
            "botRow": {f"node{c}": False for c in "ABCDEFGHIJKL"},
            "trough": 3,
        },
        "autoPoints": 21,
        "teleopCoralCount": 12, "teleopCoralPoints": 48,
        "teleopReef": {
            "topRow": {f"node{c}": False for c in "ABCDEFGHIJKL"},
            "midRow": {f"node{c}": False for c in "ABCDEFGHIJKL"},
            "botRow": {f"node{c}": False for c in "ABCDEFGHIJKL"},
            "trough": 12,
        },
        "teleopPoints": 48,
        "netAlgaeCount": 2, "wallAlgaeCount": 1, "algaePoints": 9,
        "endGameRobot1": "DeepCage", "endGameRobot2": "ShallowCage", "endGameRobot3": "None",
        "endGameBargePoints": 17,
        "rp": 2, "foulCount": 0, "techFoulCount": 0, "foulPoints": 0,
        "g206Penalty": False, "g410Penalty": False, "g418Penalty": False, "g428Penalty": False,
        "totalPoints": 95,
    }
    bd = parse_score_breakdown_2025({"red": alliance, "blue": alliance})
    assert bd is not None
    assert bd.red.totalPoints == 95
    assert bd.red.endGameRobot1.value == "DeepCage"
    assert bd.blue.autoMobilityPoints == 6


def test_parse_none_breakdown():
    from bluealliance import parse_score_breakdown_2025
    assert parse_score_breakdown_2025(None) is None
