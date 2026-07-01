from bluealliance import TBACollector, __version__
print(__version__)  # 0.1.0

c = TBACollector("sM5ErSVKUaTgLEUBDI1AzLjPkzepXkXlsGg7XiyiyRyuG5ceGhYbXe2jSDMEZie1")
team = c.team("frc7563")
print(team.nickname, team.city)