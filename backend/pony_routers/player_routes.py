from icecream import ic

from datetime import datetime, timedelta
from dateutil import parser

from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder

from pony_db_connection import init_db, db
from pony_db_models.entities import Team, Player

db = init_db(create_tables=True)

player_router = APIRouter()

current_season = datetime.now().year

if datetime.now().month >= 1 and datetime.now().month <= 4:
    current_season = str(current_season - 1) + str(current_season)
else:
    current_season = str(current_season) + str(current_season + 1)


@player_router.get("/players_by_team_id/{id}")
async def get_players_by_team_id(id: int, season: str = current_season):
    """
    Gets basic player information about all players on a given team.

    Parameters:
        id: The ID of the team to retrieve a list of players for.
        season: The season string for the season from which to get roster data for.
            (default: the current season)

    Returns:
        A list of players on the given team and a dictionary of thier basic information.
    """
    players = db.get_all_with_relations(
        Player,
        filters={"current_team": id},
        exclude=["id"],
        relation_fields={"current_team": ["name", "abbr"]},
    )
    need_to_update = datetime.now() - timedelta(hours=4)

    if len(players) != 0:
        for player in players:
            last_updated_time = parser.parse(player["last_updated"])
