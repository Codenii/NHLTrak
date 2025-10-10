from nhlpy import NHLClient
from icecream import ic


client = NHLClient()

teams = client.teams.teams()

# players = client.players.players_by_team("OTT", "20252026")

# ic(players)

d_total_height = 0
d_total_len = 0
g_total_height = 0
g_total_len = 0
f_total_height = 0
f_total_len = 0
# for dman in players["defensemen"]:
#     # ic(dman["heightInInches"])
#     total_height += dman["heightInInches"]

# average_height = total_height / len(players["defensemen"])

# to_feet = int(average_height / 12)
# to_feet_inches = average_height % 12

# ic(f"{to_feet}' {to_feet_inches}\"")
for team in teams:
    players = client.players.players_by_team(team["abbr"], "20252026")
    d_total_len += len(players["defensemen"])
    f_total_len += len(players["forwards"])
    g_total_len += len(players["goalies"])
    for dman in players["defensemen"]:
        d_total_height += dman["heightInInches"]

    for forward in players["forwards"]:
        f_total_height += forward["heightInInches"]

    for goalie in players["goalies"]:
        g_total_height += goalie["heightInInches"]

d_average_height = round(d_total_height / d_total_len, 2)
f_average_height = round(f_total_height / f_total_len, 2)
g_average_height = round(g_total_height / g_total_len, 2)

d_to_feet = int(d_average_height / 12)
d_to_feet_inches = round(d_average_height % 12, 2)

f_to_feet = int(f_average_height / 12)
f_to_feet_inches = round(f_average_height % 12, 2)

g_to_feet = int(g_average_height / 12)
g_to_feet_inches = round(g_average_height % 12, 2)

print(f"Defensemen average height in inches: {d_average_height}")
print(f"Forward average height in inches: {f_average_height}")
print(f"Goalie average height in inches: {g_average_height}")

print(f"Defensemen average height in feet: {d_to_feet}' {d_to_feet_inches}\"")
print(f"Forward average height in feet: {f_to_feet}' {f_to_feet_inches}\"")
print(f"Goalie average height in feet: {g_to_feet}' {g_to_feet_inches}\"")
