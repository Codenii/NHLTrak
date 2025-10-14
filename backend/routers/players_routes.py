from icecream import ic
from datetime import datetime

from fastapi import APIRouter, Body, Request, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder

from nhlpy import NHLClient

from db_connection import init_db, db
from config import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME
from helpers import get_players_by_team


nhl_client = NHLClient()

db = init_db(DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)


current_season = datetime.now().year

if datetime.now().month >= 1 and datetime.now().month <= 4:
    current_season = str(current_season) + str(current_season - 1)
else:
    current_season = str(current_season) + str(current_season + 1)


players_router = APIRouter()

columns = [
    "birth_city",
    "birth_country",
    "birth_date",
    "birth_province_state",
    "first_name",
    "last_name",
    "headshot",
    "height_in_centimeters",
    "height_in_inches",
    "position",
    "shoots_catches",
    "sweater_number",
    "weight_in_kilograms",
    "weight_in_pounds",
    "last_updated",
    "current_team",
]


@players_router.get("/all_players_current_season")
async def get_all_players_current_season():
    return {
        "message": f"All players endpoint. {current_season} - {datetime.now().month}"
    }


@players_router.get("/all_players_past_seasons")
async def get_all_players_past_seasons(season: str):
    return {"message": f"All players endpoint for the {season} season"}


@players_router.get("/players_by_team_id/{id}")
async def get_players_by_team_id(id: int, season: str = current_season):
    """
    Gets basic information about all players on a given team.

    Parameters:
    id (int): The ID of the team to retrieve list of players for.
    season (str): The season for which to retrieve the roster for.
                  Defaults to the current season.

    Returns:
    list: List of players on the given team and thier basic informanion in json format.
    """
    player_sql_query = f"SELECT players.birth_city, players.birth_country, players.birth_date, players.birth_province_state, players.first_name, players.last_name, players.headshot, players.height_in_centimeters, players.height_in_inches, players.position, players.shoots_catches, players.sweater_number, players.weight_in_kilograms, players.weight_in_pounds, players.last_updated, teams.name FROM players INNER JOIN teams ON players.current_team = teams.id WHERE players.current_team = {id};"

    team_sql_query = (
        f"SELECT teams.id, teams.abbr, teams.name FROM teams WHERE teams.id = {id}"
    )

    player_data = get_players_by_team(team_sql_query, player_sql_query, season)

    return player_data


@players_router.get("/players_by_team_name/{name}")
async def get_players_by_team_name(name: str, season: str = current_season):
    """
    Gets basic information about all players on a given team.

    Parameters:
    name (str): The name, common name, or abbreviation of the team to retrieve list of players for.
    season (str): The season for which to retrieve the roster for.
                  Defaults to the current season.

    Returns:
    list: List of players on the given team and thier basic information in json format.
    """
    team_sql_query = f"SELECT teams.id, teams.abbr, teams.name FROM teams WHERE teams.name = '{name.title()}' OR teams.common_name = '{name.title()}' OR teams.abbr = '{name.upper()}';"
    team = db.execute_query(team_sql_query)
    team = team.fetchall()
    team = team[0]

    player_sql_query = f"SELECT players.birth_city, players.birth_country, players.birth_date, players.birth_province_state, players.first_name, players.last_name, players.headshot, players.height_in_centimeters, players.height_in_inches, players.position, players.shoots_catches, players.sweater_number, players.weight_in_kilograms, players.weight_in_pounds, players.last_updated, teams.name FROM players INNER JOIN teams ON players.current_team = teams.id WHERE players.current_team = {team[0]};"

    player_data = get_players_by_team(team_sql_query, player_sql_query, season)

    return player_data
