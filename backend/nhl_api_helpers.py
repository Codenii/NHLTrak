from icecream import ic

from datetime import datetime

import logging

from nhlpy import NHLClient

from db_models.entities import Conference, Division, Team

"""
! Important NHL API hints/tips:
    * When getting stats:
        gameTypeId:
            1 - Preseason
            2 - Regular Season
            3 - Playoffs
            4 - All-Star
"""
nhl_client = NHLClient()

logger = logging.getLogger(__name__)

current_season = datetime.now().year

if datetime.now().month >= 1 and datetime.now().month <= 4:
    current_season = str(current_season - 1) + str(current_season)
else:
    current_season = str(current_season) + str(current_season + 1)


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

        Raises:
            Exception: If the API call fails.
        """
        if self._teams_cache is None:
            try:
                self._teams_cache = self.nhl_client.teams.teams()
                logger.info("Successfully fetched team data from NHL API")
            except Exception as e:
                logger.error(f"Failed to fetch team data from NHL API: {e}")
                raise Exception(f"NHL API error: Unable to fetch team data. {str(e)}")
        return self._teams_cache

    def clear_cache(self):
        """
        Clears the cached teams data, forcing a fresh API call on next request.
        """
        self._teams_cache = None

    def get_all_teams(self):
        """
        Gets a list of all teams from the NHL API.

        Returns:
            A list of all NHL teams.

        Raises:
            Exception: If database lookups fail or data is missing
        """
        all_teams = []
        try:
            teams = self._fetch_and_cache_team_data()

            for team in teams:
                try:
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
                except KeyError as e:
                    logger.error(
                        f"Error processing team {team.get('name', 'Unknown')}: {e}"
                    )
                    continue
        except Exception as e:
            logger.error(f"Failed to get all teams: {e}")
            raise Exception(f"Error retrieving data from database. {str(e)}")

        return all_teams

    def get_all_conferences(self):
        """
        Gets a list of all conferences from the NHL API.

        Returns:
            A list of all NHL conferences.
        """
        all_conferences = {}
        teams = self._fetch_and_cache_team_data()

        for team in teams:
            conf = team["conference"]
            if conf["name"] not in all_conferences:
                all_conferences[conf["name"]] = conf

        return list(all_conferences.values())

    def get_all_divisions(self):
        """
        Gets a list of all divisions from the NHL API.

        Returns:
            A list of all NHL divisions.
        """
        all_divisions = {}
        teams = self._fetch_and_cache_team_data()

        for team in teams:
            div = team["division"]
            if div["name"] not in all_divisions:
                all_divisions[div["name"]] = div

        return list(all_divisions.values())

    def get_all_players_by_team_id(self, team_id, season=current_season):
        """
        Gets all player information for a teams roster during a given season.
        NOTE: This function gets *ALL* data for each player on the given
        teams current roster (this means historical stats data, team history,
        etc.)

        Parameters:
            team_id: The team ID of the team to retrieve roster data for.
            season: The season string for the season to get roster data for.
                (Example: "20252026")

        Returns:
            A list of all players on the teams roster for the requested season.
        """
        team = self.db.get_by_id(Team, team_id).abbr
        roster = nhl_client.teams.team_roster(team, season)

        for position in roster:
            for player in roster[position]:
                if player["firstName"]["default"] == "Claude":
                    stats = nhl_client.stats.player_career_stats(player["id"])
                    for season in stats["seasonTotals"]:
                        data = {
                            "season": season["season"],
                            "league": season["leagueAbbrev"],
                            "team": season["teamName"]["default"],
                            "game_type": season["gameTypeId"],
                        }
                        ic(season)
                    # ic(stats["seasonTotals"])
                    return


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
