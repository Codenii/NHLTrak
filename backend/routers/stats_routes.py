from icecream import ic
from datetime import datetime

from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder

from nhlpy import NHLClient

from db_connection import init_db, db
from config import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME

from helpers import get_stats_by_player

nhl_client = NHLClient()

db = init_db(DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)

current_season = datetime.now().year

if datetime.now().month >= 1 and datetime.now().month <= 4:
    current_season = str(current_season) + str(current_season - 1)
else:
    current_season = str(current_season) + str(current_season + 1)

stats_router = APIRouter()


@stats_router.get("/season_by_id/{id}")
async def get_season_stats_by_id(id: str, season: str = current_season):
    """
    Gets statistics for the given player for the given season.

    Parameters:
    id (str): The ID of the player to gather stats for.
    season (str): The season to gather stats for.
                  Defaults to the current season.

    Returns:
    list: List of all players stats for the given season in json format.
    """

    stats_sql_query = (
        f"SELECT * FROM stats WHERE stats.player = {id} AND stats.season = '{season}';"
    )

    stats_data = get_stats_by_player(stats_sql_query, season, id)

    return stats_data


@stats_router.get("/season_by_name/{name}")
async def get_season_stats_by_name(
    first_name: str, last_name: str, season: str = current_season
):
    """
    Gets statistics for the given player for the given season.

    Parameters:
    first_name (str): The first name of the player to retrieve stats for.
    last_name (str): The last name of the player to retrieve stats for.
    season (str): The season string to gather stats for.
                  Defaults to the current season.

    Returns:
    list: List of game stats for the season provided for the given player in json format.
    """
    player_sql_query = f"SELECT players.id FROM players WHERE players.first_name = '{first_name}' AND players.last_name = '{last_name}';"

    player = db.execute_query(player_sql_query).fetchall()[0]
    player = player[0]
    stats_sql_query = f"SELECT * FROM stats WHERE stats.player = {player} AND stats.season = '{season}';"

    stats_data = get_stats_by_player(stats_sql_query, season, player)

    return stats_data
