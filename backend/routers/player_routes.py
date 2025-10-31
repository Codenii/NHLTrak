from icecream import ic

from fastapi import APIRouter

from db_connection import init_db
from db_helpers import create_db_helper
from nhl_api_helpers import create_nhl_api_helper

player_router = APIRouter()

db = init_db(create_tables=True)
db_helper = create_db_helper(db)
nhl_api_helper = create_nhl_api_helper(db_connection=db, db_helper=db_helper)


@player_router.get("/test")
async def test(team_id):
    nhl_api_helper.get_player_by_id(team_id)
