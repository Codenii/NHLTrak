from icecream import ic

from db_connection import init_db
from db_helpers import create_db_helper
from nhl_api_helpers import create_nhl_api_helper
from db_models.entities import Team, Conference, Division

from contextlib import asynccontextmanager
from fastapi import FastAPI

from nhlpy import NHLClient

from routers.team_routes import team_router
from routers.player_routes import player_router
from routers.stats_routes import stat_router

from datetime import datetime, timedelta

nhl_client = NHLClient()

db = init_db(create_tables=True)
db_helper = create_db_helper(db)
nhl_api_helper = create_nhl_api_helper(db_connection=db, db_helper=db_helper)


@asynccontextmanager
async def lifespan(app: FastAPI):
    db_teams = db.get_all(Team)
    db_confs = db.get_all(Conference)
    db_divs = db.get_all(Division)

    if db_helper._should_update_database(db_confs, timedelta(days=7)):
        nhl_api_helper._clear_cache()
        all_conferences = nhl_api_helper.get_all_conferences()
        db.insert_many(Conference, records=all_conferences)

    if db_helper._should_update_database(db_divs, timedelta(days=7)):
        all_divisions = nhl_api_helper.get_all_divisions()
        db.insert_many(Division, records=all_divisions)

    if db_helper._should_update_database(db_teams, timedelta(days=7)):
        all_teams = nhl_api_helper.get_all_teams()

        db.insert_many(Team, all_teams)

    yield


app = FastAPI(lifespan=lifespan)

app.include_router(team_router, tags=["team"], prefix="/teams")
app.include_router(player_router, tags=["player"], prefix="/players")
app.include_router(stat_router, tags=["stats"], prefix="/stats")
