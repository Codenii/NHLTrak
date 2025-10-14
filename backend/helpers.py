from icecream import ic

from fastapi.encoders import jsonable_encoder

from db_connection import init_db, db
from config import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME

from sqlalchemy.exc import IntegrityError

from datetime import datetime, timedelta
from dateutil import parser

from nhlpy import NHLClient

db = init_db(DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)
nhl_client = NHLClient()

player_columns = [
    "birth_city",
    "birth_country",
    "birth_date",
    "birth_province_state",
    "first_name",
    "last_name",
    "headshot",
    "height_in_centimeters",
    "height_in_inches",
    "position",
    "shoots_catches",
    "sweater_number",
    "weight_in_kilograms",
    "weight_in_pounds",
    "last_updated",
    "current_team",
]

stats_columns = [
    "id",
    "assists",
    "common_name",
    "game_winning_goal",
    "goals",
    "home_road_flag",
    "opponent_abbr",
    "opponent_common_name",
    "ot_goals",
    "pim",
    "plus_minus",
    "points",
    "power_play_goals",
    "power_play_points",
    "shifts",
    "shorthanded_goals",
    "shorthanded_points",
    "shots",
    "team_abbr",
    "toi",
    "game_date",
    "player",
    "game_id",
    "season",
]


def get_players_by_team(team_sql_query: str, player_sql_query: str, season: str):
    """
    Gets players basic information based on a given team.

    Parameters:
    team_sql_query (str): SQL query string to retrieve the team information needed to get player information
    player_sql_query (str): SQL query string to retrieve the individual players information.
    season (str): The season for which to retrieve the roster for.

    Returns:
    list: List of players on the given team and thier basic information in json format.
    """
    team = db.execute_query(team_sql_query)
    team = team.fetchall()
    team_columns = ["id", "abbr", "name"]
    team_data = [dict(zip(team_columns, row)) for row in team]
    team_data = jsonable_encoder(team_data)

    players = db.execute_query(player_sql_query)
    players = players.fetchall()

    player_data = [dict(zip(player_columns, row)) for row in players]
    player_data = jsonable_encoder(player_data)

    if len(player_data) != 0:
        need_to_update = datetime.now() - timedelta(hours=4)

        last_updated_time = parser.parse(player_data[0]["last_updated"])

    # If there is no player data for the given team, or if the available
    # data is out of date, we gather new data from the NHL API.
    if len(player_data) == 0 or need_to_update >= last_updated_time:
        all_players = []
        players_from_api = nhl_client.players.players_by_team(
            team_data[0]["abbr"], season
        )
        for position in players_from_api:
            for player in players_from_api[position]:
                player_id = player["id"]
                birth_city = player["birthCity"]["default"]
                birth_country = player["birthCountry"]
                birth_date = player["birthDate"]
                try:
                    birth_province_state = player["birthStateProvince"]["default"]
                except KeyError as e:
                    birth_province_state = None
                first_name = player["firstName"]["default"]
                last_name = player["lastName"]["default"]
                headshot = player["headshot"]
                height_in_centimeters = player["heightInCentimeters"]
                height_in_inches = player["heightInInches"]
                position = player["positionCode"]
                shoots_catches = player["shootsCatches"]
                sweater_number = player["sweaterNumber"]
                weight_in_kilograms = player["weightInKilograms"]
                weight_in_pounds = player["weightInPounds"]
                current_team = team_data[0]["id"]
                last_updated = datetime.now()

                insert_query = f"INSERT INTO players (id, birth_city, birth_country, birth_date, birth_province_state, first_name, last_name, headshot, height_in_centimeters, height_in_inches, position, shoots_catches, sweater_number, weight_in_kilograms, weight_in_pounds, current_team, last_updated) VALUES ({player_id}, '{birth_city}', '{birth_country}', '{birth_date}', '{birth_province_state}', '{first_name}', '{last_name}', '{headshot}', {height_in_centimeters}, {height_in_inches}, '{position}', '{shoots_catches}', {sweater_number}, {weight_in_kilograms}, {weight_in_pounds}, {current_team}, '{last_updated}');"
                update_query = f"UPDATE players SET birth_city = '{birth_city}', birth_country = '{birth_country}', birth_date = '{birth_date}', birth_province_state = '{birth_province_state}', first_name = '{first_name}', last_name = '{last_name}', headshot = '{headshot}', height_in_centimeters = {height_in_centimeters}, height_in_inches = {height_in_inches}, position = '{position}', shoots_catches = '{shoots_catches}', sweater_number = {sweater_number}, weight_in_kilograms = {weight_in_kilograms}, weight_in_pounds = {weight_in_pounds}, current_team = {current_team}, last_updated = '{last_updated}' WHERE id = {player_id};"

                # We try to create the entry in the database, but we will
                # get an IntegrityError if the player already exists.
                # If this happens, we update the players information instead
                # of creating a new DB entry.
                try:
                    db.execute_query(insert_query)
                except IntegrityError as e:
                    print(
                        f"Player, {first_name} {last_name}, already exists. Updating data instead."
                    )
                    db.execute_query(update_query)

                # Along with adding the players to the database, we also create
                # a json object of the players information to return to the
                # user.
                all_players.append(
                    {
                        "birth_city": birth_city,
                        "birth_country": birth_country,
                        "birth_date": birth_date,
                        "birth_province_state": birth_province_state,
                        "first_name": first_name,
                        "last_name": last_name,
                        "headshot": headshot,
                        "height_in_centimeters": height_in_centimeters,
                        "height_in_inches": height_in_inches,
                        "position": position,
                        "shoots_catches": shoots_catches,
                        "sweater_number": sweater_number,
                        "weight_in_kilograms": weight_in_kilograms,
                        "weight_in_pounds": weight_in_pounds,
                        "current_team": team_data[0]["name"],
                    }
                )
        player_data = jsonable_encoder(all_players)

    return player_data


def get_stats_by_player(stats_sql_query: str, season: str, id: str):
    """
    Gets statistics for a given player for the given season.

    Parameters:
    stats_sql_query (str): SQL query string to retrieve the stats for the given player.
    season (str): The season string to retrieve stats for.
    id (str): The ID of the player to retrieve stats for.

    Returns:
    list: List of game stats for the season provided for the given player in json format.
    """
    all_games = []

    stats = db.execute_query(stats_sql_query)
    stats = stats.fetchall()
    stats_data = [dict(zip(stats_columns, row)) for row in stats]
    stats_data = jsonable_encoder(stats_data)

    if len(stats_data) == 0:
        ic("Loading stats from API")
        stats = nhl_client.stats.player_game_log(id, season, 2)
        for game in stats:
            stats_id = ""
            stats_id = str(game["gameId"]) + str(id)
            stats_id = int(stats_id)
            assists = game["assists"]
            common_name = game["commonName"]["default"]
            game_winning_goal = game["gameWinningGoals"]
            if game_winning_goal == 0:
                game_winning_goal = False
            else:
                game_winning_goal = True
            goals = game["goals"]
            home_road_flag = game["homeRoadFlag"]
            if home_road_flag == "R":
                home_road_flag = False
            else:
                home_road_flag = True
            opponent_abbr = game["opponentAbbrev"]
            opponent_common_name = game["opponentCommonName"]["default"]
            ot_goals = game["otGoals"]
            pim = game["pim"]
            plus_minus = game["plusMinus"]
            points = game["points"]
            power_play_goals = game["powerPlayGoals"]
            power_play_points = game["powerPlayPoints"]
            shifts = game["shifts"]
            shorthanded_goals = game["shorthandedGoals"]
            shorthanded_points = game["shorthandedPoints"]
            shots = game["shots"]
            team_abbr = game["teamAbbrev"]
            toi = game["toi"]
            game_date = game["gameDate"]
            player = id
            game_id = game["gameId"]
            game_season = season

            insert_query = f"INSERT INTO stats (id, assists, common_name, game_winning_goal, goals, home_road_flag, opponent_abbr, opponent_common_name, ot_goals, pim, plus_minus, points, power_play_goals, power_play_points, shifts, shorthanded_goals, shorthanded_points, shots, team_abbr, toi, game_date, player, game_id, season) VALUES ({stats_id}, {assists}, '{common_name}', {game_winning_goal}, {goals}, '{home_road_flag}', '{opponent_abbr}', '{opponent_common_name}', {ot_goals}, {pim}, {plus_minus}, {points}, {power_play_goals}, {power_play_points}, {shifts}, {shorthanded_goals}, {shorthanded_points}, {shots}, '{team_abbr}', '{toi}', '{game_date}', {player}, {game_id}, {game_season});"

            db.execute_query(insert_query)

            all_games.append(
                {
                    "id": stats_id,
                    "assists": assists,
                    "common_name": common_name,
                    "game_winning_goal": game_winning_goal,
                    "goals": goals,
                    "home_road_flag": home_road_flag,
                    "opponent_abbr": opponent_abbr,
                    "opponent_common_name": opponent_common_name,
                    "ot_goals": ot_goals,
                    "pim": pim,
                    "plus_minus": plus_minus,
                    "points": points,
                    "power_play_goals": power_play_goals,
                    "power_play_points": power_play_points,
                    "shifts": shifts,
                    "shorthanded_goals": shorthanded_goals,
                    "shorthanded_points": shorthanded_points,
                    "shots": shots,
                    "team_abbr": team_abbr,
                    "toi": toi,
                    "game_date": game_date,
                    "player": id,
                    "game_id": game_id,
                    "season": game_season,
                }
            )
        stats_data = jsonable_encoder(all_games)

    return stats_data
