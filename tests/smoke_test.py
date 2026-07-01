# smoke_test.py
from bluealliance import TBACollector

c = TBACollector("YOUR_API_KEY")

# status da TBA
status = c.status()
print("temporada atual:", status.current_season)
assert not status.is_datafeed_down, "TBA datafeed está fora"

# time
team = c.team("frc7563")
assert team.team_number == 7563
print("time:", team.nickname, "-", team.city)

# evento simples
events = c.events_simple(2025)
assert len(events) > 0
print(f"{len(events)} eventos em 2025")

# evento do megazord
bundle = c.event_bundle("2025brba")
print("evento:", bundle.event.name)
print("times:", len(bundle.teams))
print("partidas:", len(bundle.matches))

# score breakdown 2025
for match, bd in c.event_matches_2025("2025brba"):
    if bd and match.comp_level.value == "qm":
        print(f"{match.key}: red={bd.red.totalPoints} blue={bd.blue.totalPoints}")
        break

print("smoke test OK")