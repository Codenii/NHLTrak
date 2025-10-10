from db_connection import init_db, db, Base
from dotenv import dotenv_values
from contextlib import asynccontextmanager

from icecream import ic

from fastapi import FastAPI

from nhlpy import NHLClient

nhl_client = NHLClient()

# app = FastAPI()

config = dotenv_values(".env")
DB_USER = config["DB_USER"]
DB_PASSWORD = config["DB_PASSWORD"]
DB_HOST = config["DB_HOST"]
DB_PORT = config["DB_PORT"]
DB_NAME = config["DB_NAME"]

db = init_db(DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)


@asynccontextmanager
async def lifespan(app: FastAPI):
    all_teams = []
    all_players = []
    all_divisions = []
    all_conferences = []

    teams = nhl_client.teams.teams()

    for team in teams:
        all_teams.append(team)

        if team["conference"] not in all_conferences:
            all_conferences.append(team["conference"])

        if team["division"] not in all_divisions:
            all_divisions.append(team["division"])

        players = nhl_client.players.players_by_team(team["abbr"], "20252026")

        for dmen in players["defensemen"]:
            if dmen not in all_players:
                all_players.append(dmen)
        for forward in players["forwards"]:
            if forward not in all_players:
                all_players.append(forward)
        for goalie in players["goalies"]:
            if goalie not in all_players:
                all_players.append(goalie)

    for division in all_divisions:
        results = db.execute_query(
            f"SELECT * FROM divisions WHERE name = '{division['name']}'"
        )
        results = results.fetchall()

        if not results:
            db.execute_query(
                f"INSERT INTO divisions (abbr, name) VALUES ('{division['abbr']}', '{division['name']}');"
            )
    for conference in all_conferences:
        results = db.execute_query(
            f"SELECT * FROM conferences WHERE name = '{conference['name']}'"
        )
        results = results.fetchall()

        if not results:
            db.execute_query(
                f"INSERT INTO conferences (abbr, name) VALUES ('{conference['abbr']}', '{conference['name']}');"
            )
    for team in all_teams:
        results = db.execute_query(
            f"SELECT * FROM teams WHERE name = '{team['name']}';"
        )
        results = results.fetchall()

        if not results:
            division_id = db.execute_query(
                f"SELECT id FROM divisions WHERE name = '{team['division']['name']}'"
            )
            division_id = division_id.fetchall()[0]
            division_id = division_id[0]
            conference_id = db.execute_query(
                f"SELECT id FROM conferences WHERE name = '{team['conference']['name']}'"
            )
            conference_id = conference_id.fetchall()[0]
            conference_id = conference_id[0]
            query_string = f"INSERT INTO teams (id, abbr, common_name, name, conference, division, logo) VALUES ('{team['franchise_id']}', '{team['abbr']}', '{team['common_name']}', '{team['name']}', '{conference_id}', '{division_id}', '{team['logo']}');"
            db.execute_query(query_string)
    yield


app = FastAPI(lifespan=lifespan)
