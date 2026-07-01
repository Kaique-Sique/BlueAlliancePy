from bluealliance import TBACollector, __version__
print(__version__)  # 0.1.0

c = TBACollector("Your_api_key")
team = c.team("frc7563")
print(team.nickname, team.city)