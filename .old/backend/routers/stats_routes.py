from icecream import ic

from datetime import datetime, timedelta

from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder

from nhlpy import NHLClient

from pony.orm import TransactionIntegrityError

from db_connection import init_db, db
from db_models.entities import Team, Player, PlayerTeamSeason, Stat
from db_helpers import create_db_helper

db = init_db(create_tables=True)

db_helper = create_db_helper(db)

nhl_client = NHLClient()

stat_router = APIRouter()

current_season = datetime.now().year

if datetime.now().month >= 1 and datetime.now().month <= 4:
    current_season = str(current_season - 1) + str(current_season)
else:
    current_season = str(current_season) + str(current_season + 1)


@stat_router.get("/season_stats_by_player_id")
async def get_season_stats_by_player_id(id: int, season: str = current_season):
    """
    Gets a players seasonal statistics for a given season.

    Parameters:
        id: The players ID.
        season: The season string.

    Returns:
        A list of game by game statistics for the given player during the given season.
    """

    # player = db.get_by_id(Player, id)

    # if not player:
    #     return {"error": "Player not found"}

    # player = db_helper.get_player_with_teams(player.id)
    # return jsonable_encoder(player)

    career_data = nhl_client.stats.player_career_stats(player_id=id)

    player_info = {
        "id": career_data.get("playerId"),
        "birth_city": career_data.get("birthCity", {}).get("default"),
        "birth_country": career_data.get("birthCountry"),
        "birth_province_state": career_data.get("birthStateProvince", {}).get(
            "default"
        ),
        "first_name": career_data.get("firstName").get("default"),
        "last_name": career_data.get("lastName").get("default"),
        "headshot": career_data.get("headshot"),
        "height_in_centimeters": career_data.get("heightInCentimeters"),
        "height_in_inches": career_data.get("heightInInches"),
        "position": career_data.get("position"),
        "shoots_catches": career_data.get("shootsCatches"),
        "sweater_number": career_data.get("sweaterNumber"),
        "weight_in_kilograms": career_data.get("weightInKilograms"),
        "weight_in_pounds": career_data.get("weightInPounds"),
    }

    team_history = []

    if "seasonTotals" in career_data:
        for season in career_data["seasonTotals"]:
            ic(season)
            team_entry = {
                "season": season.get("season"),
                "team_name": season.get("teamName", {}).get("default"),
                "team_common_name": season.get("teamCommonName", {}).get("default"),
                "team_abbr": season.get("teamAbbrev", {}),
                "league": season.get("leagueAbbrev"),
                "sequence": season.get("sequence"),
            }
            team_history.append(team_entry)

    return {"player_info": player_info, "team_info": team_history}
