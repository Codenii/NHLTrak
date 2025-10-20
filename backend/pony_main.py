from pony_db_connection import init_db
from pony_db_models.entities import Team, Conference, Division, Player, Stat

from contextlib import asynccontextmanager

from icecream import ic

from fastapi import FastAPI

from nhlpy import NHLClient

from pony_routers.team_routes import team_router
from pony_routers.player_routes import player_router

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

    if len(db_teams) < 32:
        teams = nhl_client.teams.teams()

        for team in teams:
            if team["conference"] not in all_conferences:
                all_conferences.append(team["conference"])

            if team["division"] not in all_divisions:
                all_divisions.append(team["division"])

        if len(db_conf) < 2:
            for conference in all_conferences:
                db.insert_one(
                    Conference, abbr=conference["abbr"], name=conference["name"]
                )

        if len(db_div) < 4:
            for division in all_divisions:
                db.insert_one(Division, abbr=division["abbr"], name=division["name"])

        for team in teams:
            conf = db.get_one(Conference, name=team["conference"]["name"])
            div = db.get_one(Division, name=team["division"]["name"])
            team_data = {
                "id": team["franchise_id"],
                "abbr": team["abbr"],
                "common_name": team["common_name"],
                "name": team["name"],
                "conference": conf.id,
                "division": div.id,
                "logo": team["logo"],
            }
            all_teams.append(team_data)

        teams_inserted = db.insert_many(Team, all_teams)

    yield


app = FastAPI(lifespan=lifespan)

app.include_router(team_router, tags=["team"], prefix="/teams")
app.include_router(player_router, tags=["player"], prefix="/players")
