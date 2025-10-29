from icecream import ic

import logging

from pony.orm import TransactionIntegrityError

from db_connection import init_db
from db_helpers import create_db_helper
from nhl_api_helpers import create_nhl_api_helper
from db_models.entities import Team, Conference, Division

from contextlib import asynccontextmanager
from fastapi import FastAPI

from routers.team_routes import team_router
from routers.player_routes import player_router
from routers.stats_routes import stat_router

from datetime import timedelta

db = init_db(create_tables=True)
db_helper = create_db_helper(db)
nhl_api_helper = create_nhl_api_helper(db_connection=db, db_helper=db_helper)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        db_teams = db.get_all(Team)
        db_confs = db.get_all(Conference)
        db_divs = db.get_all(Division)
        confs_need_update = db_helper._should_update_database(
            db_confs, timedelta(days=7)
        )
        divs_need_update = db_helper._should_update_database(db_divs, timedelta(days=7))
        teams_need_update = db_helper._should_update_database(
            db_teams, timedelta(days=7)
        )

        needs_update = confs_need_update or divs_need_update or teams_need_update

        if needs_update:
            nhl_api_helper.clear_cache()

        if confs_need_update or teams_need_update:
            all_conferences = nhl_api_helper.get_all_conferences()
            db_helper.upsert_conference(all_conferences)

        if divs_need_update or teams_need_update:
            all_divisions = nhl_api_helper.get_all_divisions()
            db_helper.upsert_many_divisions(all_divisions)

        if teams_need_update:
            all_teams = nhl_api_helper.get_all_teams()
            try:
                db.insert_many(Team, all_teams)
            except TransactionIntegrityError as e:
                db.update_many(Team, all_teams)
    except Exception as e:
        logger.critical(f"Critical error during application startup: {e}")

    yield


app = FastAPI(lifespan=lifespan)

app.include_router(team_router, tags=["team"], prefix="/teams")
app.include_router(player_router, tags=["player"], prefix="/players")
app.include_router(stat_router, tags=["stats"], prefix="/stats")
