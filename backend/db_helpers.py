from icecream import ic

from pony.orm import db_session

from datetime import datetime, timedelta

from db_models.entities import Player, Team, PlayerTeamSeason, Conference, Division


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

    def _should_update_database(self, objects: list, t_delta: timedelta):
        """
        Checks to see if objects in the database are stale.

        Parameters:
            objects: The list of database objects to check.
            t_delta: The timedelta for the staleness calculation.
                (How old data can be, before its deemed stale and needs to be updated)

        Returns:
            True if the data is missing, or is determined to be stale. False if the data does not
            need to be updated.
        """

        if not objects:
            return True

        update_threshold = datetime.now() - t_delta

        return any(obj.last_updated <= update_threshold for obj in objects)

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
    def update_player_team_season(self, player_id, team_id, season, update_data):
        """
        Updates an existing player-team-season record.

        Parameters:
            player_id: Player ID.
            team_id: Team ID.
            season: The season string (ex: "20252026").
            update_data: Dictionary containing fields to update.
                sweater_number: int (optional)
                games_played: int (optional)
                start_date: date (optional)
                end_date: date (optional)

        Returns:
            A dictionary representation of the updated PlayerTeamSeason record, or None if
            the record doesn't exist.
        """
        player = Player[player_id]
        team = Team[team_id]

        pts = PlayerTeamSeason.get(player=player, team=team, season=season)

        if not pts:
            return None

        if "sweater_number" in update_data:
            pts.sweater_number = update_data["sweater_number"]
        if "games_played" in update_data:
            pts.games_played = update_data["games_played"]
        if "start_date" in update_data:
            pts.start_date = update_data["start_date"]
        if "end_date" in update_data:
            pts.end_date = update_data["end_date"]

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
                            "birth_city": player.birth_city,
                            "birth_country": player.birth_country,
                            "birth_province_state": player.birth_province_state,
                            "shoots_catches": player.shoots_catches,
                            "height_in_centimeters": player.height_in_centimeters,
                            "height_in_inches": player.height_in_inches,
                            "weight_in_kilograms": player.weight_in_kilograms,
                            "weight_in_pounds": player.weight_in_pounds,
                            "headshot": player.headshot,
                            "sweater_number": pts.sweater_number,
                            "games_played": pts.games_played,
                            "last_updated": player.last_updated,
                        }
                    )
            return roster
        return []

    @db_session
    def get_player_with_teams(self, player_id):
        """
        Gets a players information as well as team history.

        Parameters:
            player_id: The ID of the player to retrieve.

        Returns:
            A dictionary containing player information and their team history,
            or None if the player is not found/doesn't exist.
        """
        player = Player.get(id=player_id)

        if not player:
            return None

        team_history = []
        for pts in player.team_seasons:
            team_history.append(
                {
                    "team_id": pts.team.id,
                    "team_name": pts.team.name if hasattr(pts.team, "name") else None,
                    "team_common_name": (
                        pts.team.common_name
                        if hasattr(pts.team, "common_name")
                        else None
                    ),
                    "team_abbr": pts.team.abbr if hasattr(pts.team, "abbr") else None,
                    "season": pts.season,
                    "sweater_number": pts.sweater_number,
                    "games_played": pts.games_played,
                }
            )

        return {
            "id": player.id,
            "first_name": player.first_name,
            "last_name": player.last_name,
            "position": player.position,
            "birth_city": player.birth_city,
            "birth_country": player.birth_country,
            "birth_province_state": player.birth_province_state,
            "shoots_catches": player.shoots_catches,
            "height_in_centimeters": player.height_in_centimeters,
            "height_in_inches": player.height_in_inches,
            "weight_in_kilograms": player.weight_in_kilograms,
            "weight_in_pounds": player.weight_in_pounds,
            "headshot": player.headshot,
            "last_updated": player.last_updated,
            "team_history": team_history,
        }

    @db_session
    def upsert_conference(self, conf_data):
        """
        Inserts or updates a conference by its name.

        Parameters:
            conf_data: A dictionary with conference data.

        Returns:
            The created or updated Conference entity.
        """
        existing = Conference.get(name=conf_data["name"])

        if existing:
            if "abbr" in conf_data:
                existing.abbr = conf_data["abbr"]
            existing.last_updated = datetime.now()
            return existing
        else:
            return Conference(**conf_data)

    @db_session
    def upsert_division(self, div_data):
        """
        Inserts or updates a division by its name.

        Parameters:
            div_data: A dictionary with division data.

        Returns:
            The created or updated Division entity.
        """
        existing = Division.get(name=div_data["name"])

        if existing:
            if "abbr" in div_data:
                existing.abbr = div_data["abbr"]
            existing.last_updated = datetime.now()
            return existing
        else:
            return Division(**div_data)

    @db_session
    def upsert_many_conferences(self, conferences):
        """
        Upsert multiple conferences at once.
        """
        return [self.upsert_conference(conf) for conf in conferences]

    @db_session
    def upsert_many_divisions(self, divisions):
        """
        Upsert multiple divisions at once.
        """
        return [self.upsert_division(div) for div in divisions]


def create_db_helper(db_connection):
    """
    Creates an Database Helper instance.

    Parameters:
        db_connection: DatabaseConnection instance.

    Returns:
        A DatabaseHelper instance.
    """
    return DatabaseHelper(db_connection=db_connection)
