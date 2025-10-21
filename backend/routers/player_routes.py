from icecream import ic

from pony.orm import db_session

from datetime import datetime, timedelta
from dateutil import parser

from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder

from nhlpy import NHLClient

from db_connection import init_db, db
from db_models.entities import Team, Player, PlayerTeamSeason
from db_helpers import create_db_helper


db = init_db(create_tables=True)

db_helper = create_db_helper(db)

nhl_client = NHLClient()

player_router = APIRouter()

current_season = datetime.now().year

if datetime.now().month >= 1 and datetime.now().month <= 4:
    current_season = str(current_season - 1) + str(current_season)
else:
    current_season = str(current_season) + str(current_season + 1)


@player_router.get("/players_by_team_id/{id}")
async def get_players_by_team_id(id: int, season: str = current_season):
    """
    Gets basic player information about all players on a given team.

    Parameters:
        id: The ID of the team to retrieve a list of players for.
        season: The season string for the season from which to get roster data for.
            (default: the current season)

    Returns:
        A list of players on the given team and a dictionary of thier basic information.
    """
    update_flag = False
    team = db.get_by_id(Team, id)
    try:
        team = team.abbr
    except Exception as e:
        return {"error": "Team not found."}
    ic(id)
    players = db_helper.get_team_roster(30, season)

    if len(players) != 0:
        need_to_update = datetime.now() - timedelta(hours=4)
        for player in players:
            last_updated_time = player["last_updated"]
            if need_to_update >= last_updated_time:
                ic("We need to update")
                update_flag = True

    if len(players) == 0 or update_flag:
        players = nhl_client.players.players_by_team(team, season)
        for position in players:
            for player in players[position]:
                try:
                    birth_province_state = player["birthStateProvince"]["default"]
                except Exception as e:
                    birth_province_state = None
                new_player = db.insert_one(
                    Player,
                    data={
                        "id": player["id"],
                        "first_name": player["firstName"]["default"],
                        "last_name": player["lastName"]["default"],
                        "birth_date": player["birthDate"],
                        "birth_city": player["birthCity"]["default"],
                        "birth_country": player["birthCountry"],
                        "birth_province_state": birth_province_state,
                        "position": player["positionCode"],
                        "shoots_catches": player["shootsCatches"],
                        "height_in_centimeters": player["heightInCentimeters"],
                        "height_in_inches": player["heightInInches"],
                        "weight_in_kilograms": player["weightInKilograms"],
                        "weight_in_pounds": player["weightInPounds"],
                        "headshot": player["headshot"],
                        "sweater_number": player["sweaterNumber"],
                        "last_updated": datetime.now(),
                    },
                )

                team = db.get_by_id(Team, id)
                season_data = {
                    "player": new_player,
                    "team": team,
                    "season": season,
                    "sweater_number": player["sweaterNumber"],
                }
                pts_dict = db_helper.insert_player_team_season(
                    new_player.id, team.id, season_data
                )
        players = db_helper.get_team_roster(id, season)

    players = jsonable_encoder(players)
    return {"roster": players, "count": len(players)}
