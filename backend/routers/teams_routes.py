from icecream import ic

from fastapi import APIRouter, Body, Request, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder

from db_connection import init_db, db
from config import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME


columns = [
    "abbr",
    "common_name",
    "name",
    "logo",
    "conf_abbr",
    "conf_name",
    "div_abbr",
    "div_name",
]

db = init_db(DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)


teams_router = APIRouter()


@teams_router.get("/")
async def get_all_teams():
    """
    Gets all NHL teams basic information.

    Returns:
    list: List of all teams basic information in json format.
    """
    sql_query = "select teams.abbr, teams.common_name, teams.name, teams.logo, conferences.abbr, conferences.name, divisions.abbr, divisions.name from teams INNER JOIN conferences ON teams.conference = conferences.id INNER JOIN divisions ON teams.division = divisions.id;"
    teams = db.execute_query(sql_query)
    teams = teams.fetchall()

    team_data = [dict(zip(columns, row)) for row in teams]

    team_data = jsonable_encoder(team_data)

    return team_data


@teams_router.get("/id/{id}")
async def get_team_by_id(id: int):
    """
    Gets a single teams basic information when given a teams ID.

    Parameters:
    id (int): The ID of the team to gather information of.

    Returns:
    list: List of the teams basic information in json format.
    """
    sql_query = f"SELECT teams.abbr, teams.common_name, teams.name, teams.logo, conferences.abbr, conferences.name, divisions.abbr, divisions.name FROM teams INNER JOIN conferences ON teams.conference = conferences.id INNER JOIN divisions ON teams.division = divisions.id WHERE teams.id = {id};"

    team = db.execute_query(sql_query)
    team = team.fetchall()

    team_data = [dict(zip(columns, row)) for row in team]
    team_data = jsonable_encoder(team_data)

    return team_data


@teams_router.get("/name/{name}")
async def get_team_by_name(name: str):
    """
    Gets a single teams basic information when given a teams name, common name, or abbreviation.

    Parameters:
    name (str): The name, common name, or abbreviation of the team to gather information of.

    Returns:
    list: List of the teams basic information in json format.
    """
    sql_query = f"SELECT teams.abbr, teams.common_name, teams.name, teams.logo, conferences.abbr, conferences.name, divisions.abbr, divisions.name FROM teams INNER JOIN conferences ON teams.conference = conferences.id INNER JOIN divisions ON teams.division = divisions.id WHERE teams.name = '{name.title()}' OR teams.common_name = '{name.title()}' OR teams.abbr = '{name.upper()}';"

    team = db.execute_query(sql_query)
    team = team.fetchall()

    team_data = [dict(zip(columns, row)) for row in team]
    team_data = jsonable_encoder(team_data)

    return team_data


@teams_router.get("/division_id/{id}")
async def get_teams_by_division_id(id: int):
    """
    Gets the basic information of all teams in a given division.

    Parameters:
    id (int): The ID of the division to gather a list of teams from.

    Returns:
    list: List of the teams in the given division as well as thier basic information in json format.
    """
    sql_query = f"SELECT teams.abbr, teams.common_name, teams.name, teams.logo, conferences.abbr, conferences.name, divisions.abbr, divisions.name FROM teams INNER JOIN conferences ON teams.conference = conferences.id INNER JOIN divisions ON teams.division = divisions.id WHERE divisions.id = {id};"

    teams = db.execute_query(sql_query)
    teams = teams.fetchall()

    team_data = [dict(zip(columns, row)) for row in teams]
    team_data = jsonable_encoder(team_data)

    return team_data


@teams_router.get("/division_name/{name}")
async def get_teams_by_division_name(name: str):
    """
    Gets the basic information of all teams in the given division.

    Parameters:
    name (str): The name or abbreviation of the division to gather a list of teams from.

    Returns:
    list: List of the teams in the given division as well as thier basic information in json format.
    """
    sql_query = f"SELECT teams.abbr, teams.common_name, teams.name, teams.logo, conferences.abbr, conferences.name, divisions.abbr, divisions.name FROM teams INNER JOIN conferences ON teams.conference = conferences.id INNER JOIN divisions ON teams.division = divisions.id WHERE divisions.name = '{name.title()}' OR divisions.abbr = '{name.title()}';"

    teams = db.execute_query(sql_query)
    teams = teams.fetchall()

    team_data = [dict(zip(columns, row)) for row in teams]
    team_data = jsonable_encoder(team_data)

    return team_data


@teams_router.get("/conference_id/{id}")
async def get_teams_by_conference_id(id: int):
    """
    Gets the basic information of all teams in the given conference.

    Parameters:
    id (int): The ID of the conference to gather a list of teams from.

    Returns:
    list: List of the teams in the given conference as well as thier basic information in json format.
    """
    sql_query = f"SELECT teams.abbr, teams.common_name, teams.name, teams.logo, conferences.abbr, conferences.name, divisions.abbr, divisions.name FROM teams INNER JOIN conferences ON teams.conference = conferences.id INNER JOIN divisions ON teams.division = divisions.id WHERE conferences.id = {id};"

    teams = db.execute_query(sql_query)
    teams = teams.fetchall()

    team_data = [dict(zip(columns, row)) for row in teams]
    team_data = jsonable_encoder(team_data)

    return team_data


@teams_router.get("/conferenc_by_name/{name}")
async def get_teams_by_conferences(name: str):
    """
    Gets the basic information of all the teams in the given conference.

    Parameters:
    name (str): The name or abbreviation of the conference to gather a list of teams from.

    Returns:
    list: List of the teams in the given conference as well as thier basic information in json format.
    """
    sql_query = f"SELECT teams.abbr, teams.common_name, teams.name, teams.logo, conferences.abbr, conferences.name, divisions.abbr, divisions.name FROM teams INNER JOIN conferences ON teams.conference = conferences.id INNER JOIN divisions ON teams.division = divisions.id WHERE conferences.name = '{name.title()}' OR conferences.abbr = '{name.title()}';"

    teams = db.execute_query(sql_query)
    teams = teams.fetchall()

    team_data = [dict(zip(columns, row)) for row in teams]
    team_data = jsonable_encoder(team_data)

    return team_data
