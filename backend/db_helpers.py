from pony.orm import db_session

from db_models.entities import Player, Team, PlayerTeamSeason


class DatabaseHelper:
    """
    Helper class for NHL specific database operations.
    """

    def __init__(self, db_connection):
        """
        Initializes the Database Helper class.

        Parameters:
            db_connection: Instance of DatabaseConnection from the db_connection module.
        """
        self.db = db_connection

    @db_session
    def insert_player_team_season(self, player_id, team_id, season_data):
        """
        Inserts player-team-season record.

        Parameters:
            player_id: Player ID
            team_id: Team ID
            season_data:
                season: str (ex: "20252026")
                sweater_number: int (optional)
                games_played: int (optional)
                start_date: date (optional)
                end_date: date (optional)

        Returns:
            A dictionary representation of the created PlayerTeamSeason record.
        """
        player = Player[player_id]
        team = Team[team_id]

        pts = PlayerTeamSeason(
            player=player,
            team=team,
            season=season_data["season"],
            sweater_number=season_data.get("sweater_number"),
        )

        return pts.to_dict()

    @db_session
    def get_team_roster(self, team_id: int, season: str):
        """
        Gets a teams roster for a given season.

        Parameters:
            team_id: the ID of the team to get roster for.
            season: the Season from which to find the roster for.
                (ex: "20252026" is the 2025-2026 season.)

        Returns:
            A list of all players on the given team for the given season.
        """
        team = Team[team_id]
        if team:
            roster = []
            for pts in team.player_seasons:
                if pts.season == season:
                    player = pts.player
                    roster.append(
                        {
                            "id": player.id,
                            "first_name": player.first_name,
                            "last_name": player.last_name,
                            "position": player.position,
                            "sweater_number": pts.sweater_number,
                            "games_played": pts.games_played,
                            "last_updated": player.last_updated,
                        }
                    )
            return roster
        return []


def create_db_helper(db_connection):
    """
    Creates an Database Helper instance.

    Parameters:
        db_connection: DatabaseConnection instance.

    Returns:
        A DatabaseHelper instance.
    """
    return DatabaseHelper(db_connection=db_connection)
