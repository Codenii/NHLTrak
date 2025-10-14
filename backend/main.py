from db_connection import init_db, db, Base
from dotenv import dotenv_values
from contextlib import asynccontextmanager

from icecream import ic

from fastapi import FastAPI

from nhlpy import NHLClient

from routers.teams_routes import teams_router
from routers.players_routes import players_router
from routers.stats_routes import stats_router

from config import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME

nhl_client = NHLClient()


db = init_db(DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)


@asynccontextmanager
async def lifespan(app: FastAPI):
    all_teams = []
    all_divisions = []
    all_conferences = []

    db_teams = db.execute_query(f"SELECT * FROM teams;")
    db_conf = db.execute_query(f"SELECT * FROM conferences;")
    db_div = db.execute_query(f"SELECT * FROM divisions;")
    if (
        len(db_teams.fetchall()) < 32
        or len(db_conf.fetchall()) < 2
        or len(db_div.fetchall()) < 4
    ):
        print(
            f"Teams/Conferences/Divisions missing from database. Adding missing data..."
        )
        teams = nhl_client.teams.teams()

        for team in teams:

            all_teams.append(team)

            if team["conference"] not in all_conferences:
                all_conferences.append(team["conference"])

            if team["division"] not in all_divisions:
                all_divisions.append(team["division"])

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
    else:
        print(f"All startup data exists. Application startup complete.")

    yield


app = FastAPI(lifespan=lifespan)

app.include_router(teams_router, tags=["teams"], prefix="/teams")
app.include_router(players_router, tags=["players"], prefix="/players")
app.include_router(stats_router, tags=["stats"], prefix="/stats")
