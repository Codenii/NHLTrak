from icecream import ic

from nhlpy import NHLClient

from pony.orm import TransactionIntegrityError

from db_connection import init_db
from db_helpers import create_db_helper
from db_models.entities import (
    Team,
    Player,
    Conference,
    Division,
    PlayerTeamSeason,
    Stat,
)


nhl_client = NHLClient()


class NhlApiHelper:
    """
    Helper class for making queries to the NHL API.
    """

    def __init__(self, nhl_client=None, db_connection=None, db_helper=None):
        """
        Initializes the NHL API Helper class.

        Parameters:
            nhl_client: An instance of NHLClient from nhlpy. If None, a
            new instance is created.
            db_connection: An instance of DatabaseConnection for database operations.
                (optional)
            db_helper: An instance of DatabaseHelper for database operations.
                (optional)
        """
        self.nhl_client = nhl_client if nhl_client else NHLClient()
        self.db = db_connection
        self.db_helper = db_helper
        self._teams_cache = None

    def _fetch_and_cache_team_data(self):
        """
        Fetches all team data from the NHL API and caches it.

        Returns:
            A list of team data from the NHL API.
        """
        if self._teams_cache is None:
            self._teams_cache = self.nhl_client.teams.teams()
        return self._teams_cache

    def _clear_cache(self):
        """
        Clears the cached teams data, forcing a fresh API call on next request.
        """
        self._teams_cache = None

    def get_all_teams(self):
        """
        Gets a list of all teams from the NHL API.

        Returns:
            A list of all NHL teams.
        """
        all_teams = []
        teams = self._fetch_and_cache_team_data()

        for team in teams:
            conf = self.db.get_one(Conference, name=team["conference"]["name"])
            div = self.db.get_one(Division, name=team["division"]["name"])
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

        return all_teams

    def get_all_conferences(self):
        """
        Gets a list of all conferences from the NHL API.

        Returns:
            A list of all NHL conferences.
        """
        all_conferences = []
        teams = self._fetch_and_cache_team_data()

        for team in teams:
            if team["conference"] not in all_conferences:
                all_conferences.append(team["conference"])

        return all_conferences

    def get_all_divisions(self):
        """
        Gets a list of all divisions from the NHL API.

        Returns:
            A list of all NHL divisions.
        """
        all_divisions = []
        teams = self._fetch_and_cache_team_data()

        for team in teams:
            if team["division"] not in all_divisions:
                all_divisions.append(team["division"])

        return all_divisions


def create_nhl_api_helper(nhl_client=None, db_connection=None, db_helper=None):
    """
    Creates an NHL API Helper instance.

    Parameters:
        nhl_client: An instance of NHLClient.
        db_connection: An instance of DatabaseConnection.
        db_helper: An instance of DatabaseHelper.
    """
    return NhlApiHelper(
        nhl_client=nhl_client, db_connection=db_connection, db_helper=db_helper
    )
