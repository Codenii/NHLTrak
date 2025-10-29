from icecream import ic

from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder

from datetime import timedelta

from pony.orm import TransactionIntegrityError

from db_connection import init_db
from db_helpers import create_db_helper
from nhl_api_helpers import create_nhl_api_helper

from db_models.entities import Team, Conference, Division

team_router = APIRouter()

db = init_db(create_tables=True)
db_helper = create_db_helper(db)
nhl_api_helper = create_nhl_api_helper(db_connection=db, db_helper=db_helper)


@team_router.get("/all_teams")
async def get_all_teams():
    db_teams = db.get_all(Team)
    db_confs = db.get_all(Conference)
    db_divs = db.get_all(Division)

    confs_need_update = db_helper._should_update_database(db_confs, timedelta(days=7))
    divs_need_update = db_helper._should_update_database(db_divs, timedelta(days=7))
    teams_need_update = db_helper._should_update_database(db_teams, timedelta(days=7))

    needs_update = confs_need_update or divs_need_update or teams_need_update

    if needs_update:
        nhl_api_helper.clear_cache()

    if confs_need_update or teams_need_update:
        all_conferences = nhl_api_helper.get_all_conferences()

        db_helper.upsert_many_conferences(all_conferences)

    if divs_need_update or teams_need_update:
        all_divisions = nhl_api_helper.get_all_divisions()

        db_helper.upsert_many_divisions(all_divisions)

    if teams_need_update:
        all_teams = nhl_api_helper.get_all_teams()

        try:
            db.insert_many(Team, records=all_teams)
        except TransactionIntegrityError as e:
            db.update_many(Team, updates=all_teams)

    out_teams = db.get_all_with_relations(
        Team,
        relation_fields={"conference": ["abbr", "name"], "division": ["abbr", "name"]},
    )
    out_teams = jsonable_encoder(out_teams)

    return out_teams


@team_router.get("/id")
async def get_team_by_id(team_id):
    """
    Gets a teams information by its ID.

    Parameters:
        team_id: The ID of the team to retrieve data for.

    Returns:
        A dictionary of the teams data in json format.
    """
    team = db.get_one_by_id_with_relations(
        Team,
        team_id,
        relation_fields={"conference": ["abbr", "name"], "division": ["abbr", "name"]},
    )

    if not team:
        return {"error": "Team was not found. Please try again, or contact support."}

    team = jsonable_encoder(team)
    return team


@team_router.get("/name")
async def get_team_by_name(team_name):
    """
    Gets a teams information by the teams name, common name, or abbreviation.

    Parameter:
        team_id: The name, common name, or abbreviation of the team to retrieve.

    Returns:
        A dictionary of the teams data in json format.
    """
    team = db.search_all_by_any_field_with_relations(
        Team,
        search_value=team_name,
        fields=["name", "common_name", "abbr"],
        relation_fields={"conference": ["abbr", "name"], "division": ["abbr", "name"]},
        case_sensitive=False,
    )
    team = jsonable_encoder(team)

    if not team:
        return {"error": "No team found. If this persists, please contact support."}
    return team


@team_router.get("/conference/id")
async def get_teams_by_conference_id(conf_id: int):
    """
    Gets team information for all teams in a conferenc indicated by conference ID.

    Parameters:
        conf_id: The ID of the conference to get teams for.

    Returns:
        A list of teams for the given conference.
    """
    teams = db.get_all_with_relations(
        Team,
        filters={"conference": conf_id},
        relation_fields={"conference": ["abbr", "name"], "division": ["abbr", "name"]},
    )
    teams = jsonable_encoder(teams)

    if not teams:
        return {"error": "No teams found. If this persists, please contact support."}

    return teams


@team_router.get("/conference/name")
async def get_teams_by_conference_name(conf_name: str):
    """
    Gets team information for all teams in a conference indicated by conference name or abbreviation.

    Parameters:
        conf_name: The name or abbreviation of the conference to retrieve teams for.

    Returns:
        A list of teams for the given conference.
    """
    try:
        conference = db.search_by_any_field(Conference, conf_name, ["name", "abbr"]).id

        teams = db.get_all_with_relations(
            Team,
            filters={"conference": conference},
            relation_fields={
                "conference": ["abbr", "name"],
                "division": ["abbr", "name"],
            },
        )
        teams = jsonable_encoder(teams)

        if not teams:
            return {
                "error": "No teams found. If this error persists, please contact support."
            }

        return teams
    except AttributeError as e:
        return {
            "error": "Conference not found. If this error persists, please contact support."
        }


@team_router.get("/division/id")
async def get_teams_by_division_id(div_id: int):
    """
    Gets team information for all teams in a division indicated by division ID.

    Parameters:
        div_id: The ID of the division to retrieve teams for.

    Returns:
        A list of teams for the given division.
    """
    teams = db.get_all_with_relations(
        Team,
        filters={"division": div_id},
        relation_fields={"conference": ["abbr", "name"], "division": ["abbr", "name"]},
    )
    teams = jsonable_encoder(teams)

    if not teams:
        return {
            "error": "No teams found. If this error persists, please contact support."
        }

    return teams


@team_router.get("/divisions/name")
async def get_teams_by_division_name(div_name: str):
    """
    Gets team information for all teams in a division indicated by the divisions
    name or abbreviation.

    Parameters:
        div_name: The name or abbreviation of the division to retrieve teams for.

    Returns:
        A list of teams for the given division.
    """
    try:
        division = db.search_by_any_field(Division, div_name, ["abbr", "name"]).id

        teams = db.get_all_with_relations(
            Team,
            filters={"division": division},
            relation_fields={
                "conference": ["abbr", "name"],
                "division": ["abbr", "name"],
            },
        )
        teams = jsonable_encoder(teams)

        if not teams:
            return {
                "error": "No teams found. If this error persists, please contact support."
            }

        return teams
    except AttributeError as e:
        return {
            "error": "Division was not found. If this error persists, please contact support."
        }
