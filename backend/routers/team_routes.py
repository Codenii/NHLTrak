from icecream import ic

from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder

from db_connection import init_db, db
from db_models.entities import Team, Division, Conference

db = init_db(create_tables=True)

team_router = APIRouter()


@team_router.get("/")
async def get_all_team():
    """
    Gets basic information about all NHL teams.

    Returns:
        A list of all basic team information in json format.
    """
    teams_list = db.get_all_with_relations(
        Team,
        relation_fields={"division": ["name", "abbr"], "conference": ["name", "abbr"]},
    )
    return {"teams": teams_list, "count": len(teams_list)}


@team_router.get("/id/{id}")
async def get_team_by_id(id: int):
    """
    Gets a teams basic information by its ID.

    Parameters:
        id: The ID of the team to search for.

    Returns:
        A dictionary of the teams basic information in json format, or None if not found.
    """
    # team = db.get_by_id(Team, id_value=id)
    team = db.get_one_by_id_with_relations(
        Team,
        id_value=id,
        exclude=["id"],
        relation_fields={"division": ["abbr", "name"], "conference": ["abbr", "name"]},
    )

    team = jsonable_encoder(team)

    return team


@team_router.get("/name/{name}")
async def get_team_by_name(name: str):
    """
    Gets teams basic information by its name, common name, or abbreviation.

    Parameters:
        name: The name, common name, or abbreviation of the team to search for.

    Returns:
        A dictionary of the teams basic information in json format, or None if not found.
    """
    team = db.search_by_any_field_with_relations(
        Team,
        search_value=name,
        fields=["name", "common_name", "abbr"],
        case_sensitive=False,
    )
    team = jsonable_encoder(team)
    return team


@team_router.get("/division/id/{id}")
async def get_teams_by_division_id(div_id: int):
    """
    Gets basic team information for all teams in the given division.

    Parameters:
        div_id: The ID of the division to get list of teams for.

    Returns:
        A list of teams and a dictionary of thier information in json format.
    """
    teams = db.get_all_with_relations(
        Team,
        filters={"division": div_id},
        exclude=["id"],
        relation_fields={"division": ["abbr", "name"], "conference": ["abbr", "name"]},
    )
    teams = jsonable_encoder(teams)

    return {"teams": teams, "count": len(teams)}


@team_router.get("division/name/{name}")
async def get_teams_by_division_name(div_name: str):
    """
    Gets basic team information for all teams in the given division.

    Parameters:
        div_name: the name or abbr of the division to get a list of teams for.

    Returns:
        A list of teams and a dictionary of thier information in json format.
    """
    division = db.search_by_any_field(Division, div_name, ["name", "abbr"]).id

    teams = db.get_all_with_relations(
        Team,
        filters={"division": division},
        exclude=["id"],
        relation_fields={"division": ["abbr", "name"], "conference": ["abbr", "name"]},
    )
    teams = jsonable_encoder(teams)

    return {"teams": teams, "count": len(teams)}


@team_router.get("/conference/id/{id}")
async def get_teams_by_conference_id(conf_id: int):
    """
    Gets basic team information for all teams in the given conference.

    Parameters:
        conf_id: The ID of the conference to get list of teams for.

    Returns:
        A list of teams and a dictionary of thier information in json format.
    """
    teams = db.get_all_with_relations(
        Team,
        filters={"conference": conf_id},
        exclude=["id"],
        relation_fields={"division": ["abbr", "name"], "conference": ["abbr", "name"]},
    )
    teams = jsonable_encoder(teams)

    return {"teams": teams, "count": len(teams)}


@team_router.get("/conference/name/{name}")
async def get_teams_by_conference_name(conf_name: str):
    """
    Gets basic team information for all teams in the given conference.

    Parameters:
        conf_name: The name of the conference to get list of teams for.

    Returns:
        A list of teams and a dictionary of thier information in json format.
    """
    conference = db.search_by_any_field(Conference, conf_name, ["abbr", "name"]).id

    teams = db.get_all_with_relations(
        Team,
        filters={"conference": conference},
        exclude=["id"],
        relation_fields={"division": ["abbr", "name"], "conference": ["abbr", "name"]},
    )
    teams = jsonable_encoder(teams)

    return {"teams": teams, "count": len(teams)}
