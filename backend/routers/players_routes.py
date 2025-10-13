from icecream import ic
from datetime import datetime, timedelta
from dateutil import parser

from fastapi import APIRouter, Body, Request, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder

from nhlpy import NHLClient

from db_connection import init_db, db
from config import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME


nhl_client = NHLClient()

db = init_db(DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)


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
    return {"message": "All players endpoint"}


@players_router.get("/all_players_past_seasons")
async def get_all_players_past_seasons(season: str):
    return {"message": f"All players endpoint for the {season} season"}


@players_router.get("/players_by_team_id/{id}")
async def get_players_by_team_id(id: int, season: str = "20252026"):
    player_sql_query = f"SELECT players.birth_city, players.birth_country, players.birth_date, players.birth_province_state, players.first_name, players.last_name, players.headshot, players.height_in_centimeters, players.height_in_inches, players.position, players.shoots_catches, players.sweater_number, players.weight_in_kilograms, players.weight_in_pounds, players.last_updated, teams.name FROM players INNER JOIN teams ON players.current_team = teams.id WHERE players.current_team = {id};"

    team_sql_query = (
        f"SELECT teams.id, teams.abbr, teams.name FROM teams WHERE teams.id = {id}"
    )

    team = db.execute_query(team_sql_query)
    team = team.fetchall()
    team_columns = ["id", "abbr", "name"]
    team_data = [dict(zip(team_columns, row)) for row in team]
    team_data = jsonable_encoder(team_data)

    players = db.execute_query(player_sql_query)
    players = players.fetchall()

    player_data = [dict(zip(columns, row)) for row in players]
    player_data = jsonable_encoder(player_data)

    need_to_update = datetime.now() - timedelta(hours=0.5)

    last_updated_time = parser.parse(player_data[0]["last_updated"])

    if len(player_data) == 0 or need_to_update >= last_updated_time:
        all_players = []
        players_from_api = nhl_client.players.players_by_team(
            team_data[0]["abbr"], season
        )
        ic(players_from_api)
        for position in players_from_api:
            for player in players_from_api[position]:
                player_id = player["id"]
                birth_city = player["birthCity"]["default"]
                birth_country = player["birthCountry"]
                birth_date = player["birthDate"]
                try:
                    birth_province_state = player["birthStateProvince"]["default"]
                except KeyError as e:
                    birth_province_state = None
                first_name = player["firstName"]["default"]
                last_name = player["lastName"]["default"]
                headshot = player["headshot"]
                height_in_centimeters = player["heightInCentimeters"]
                height_in_inches = player["heightInInches"]
                position = player["positionCode"]
                shoots_catches = player["shootsCatches"]
                sweater_number = player["sweaterNumber"]
                weight_in_kilograms = player["weightInKilograms"]
                weight_in_pounds = player["weightInPounds"]
                current_team = team_data[0]["id"]
                last_updated = datetime.now()

                if len(player_data) == 0:
                    insert_query = f"INSERT INTO players (id, birth_city, birth_country, birth_date, birth_province_state, first_name, last_name, headshot, height_in_centimeters, height_in_inches, position, shoots_catches, sweater_number, weight_in_kilograms, weight_in_pounds, current_team, last_updated) VALUES ({player_id}, '{birth_city}', '{birth_country}', '{birth_date}', '{birth_province_state}', '{first_name}', '{last_name}', '{headshot}', {height_in_centimeters}, {height_in_inches}, '{position}', '{shoots_catches}', {sweater_number}, {weight_in_kilograms}, {weight_in_pounds}, {current_team}, '{last_updated}');"
                elif need_to_update >= last_updated_time:
                    insert_query = f""
                else:
                    return {
                        "Error": "A critical error has occured. Please contact the system admin."
                    }
                db.execute_query(insert_query)
                all_players.append(
                    {
                        "birth_city": birth_city,
                        "birth_country": birth_country,
                        "birth_date": birth_date,
                        "birth_province_state": birth_province_state,
                        "first_name": first_name,
                        "last_name": last_name,
                        "headshot": headshot,
                        "height_in_centimeters": height_in_centimeters,
                        "height_in_inches": height_in_inches,
                        "position": position,
                        "shoots_catches": shoots_catches,
                        "sweater_number": sweater_number,
                        "weight_in_kilograms": weight_in_kilograms,
                        "weight_in_pounds": weight_in_pounds,
                        "current_team": team_data[0]["name"],
                    }
                )
        player_data = jsonable_encoder(all_players)

    return player_data
