from pony_db_connection import init_db
from pony_db_models.entities import Team, Conference, Division, Player, Stat

from contextlib import asynccontextmanager

from icecream import ic

from fastapi import FastAPI

from nhlpy import NHLClient

from routers.teams_routes import teams_router
from routers.players_routes import players_router
from routers.stats_routes import stats_router

nhl_client = NHLClient()


db = init_db(create_tables=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    all_teams = []
    all_divisions = []
    all_conferences = []

    db_teams = db.get_all(Team)
    db_conf = db.get_all(Conference)
    db_div = db.get_all(Division)

    ic(
        f"Teams: {len(db_teams)} | Conferences: {len(db_conf)} | Divisions: {len(db_div)}"
    )
    teams = nhl_client.teams.teams()

    for team in teams:
        all_teams.append(team)

        if team["conference"] not in all_conferences:
            all_conferences.append(team["conference"])

        if team["division"] not in all_divisions:
            all_divisions.append(team["division"])

    for conference in all_conferences:
        db.insert_one(Conference, abbr=conference["abbr"], name=conference["name"])

    for division in all_divisions:
        db.insert_one(Division, abbr=division["abbr"], name=division["name"])

    yield


app = FastAPI(lifespan=lifespan)
