from pony.orm import Required, Optional, PrimaryKey, Set
from datetime import datetime, date
from pony_db_connection import init_db, db

db = init_db()


class Team(db.db.Entity):
    _table_ = "teams"

    id = PrimaryKey(int, auto=False)
    abbr = Optional(str)
    common_name = Optional(str)
    name = Optional(str)
    conference = Required("Conference")
    division = Required("Division")
    logo = Optional(str)
    players = Set("Player")


class Conference(db.db.Entity):
    _table_ = "conferences"

    id = PrimaryKey(int, auto=True)
    abbr = Optional(str)
    name = Optional(str)
    teams = Set("Team")


class Division(db.db.Entity):
    _table_ = "divisions"

    id = PrimaryKey(int, auto=True)
    abbr = Optional(str)
    name = Optional(str)
    teams = Set("Team")


class Player(db.db.Entity):
    _table_ = "players"

    id = PrimaryKey(int, auto=False)
    birth_city = Optional(str)
    birth_country = Optional(str)
    birth_date = Optional(str)
    birth_province_state = Optional(str)
    first_name = Optional(str)
    last_name = Optional(str)
    headshot = Optional(str)
    height_in_centimeters = Optional(int)
    height_in_inches = Optional(int)
    position = Optional(str)
    shoots_catches = Optional(str)
    sweater_number = Optional(int)
    weight_in_kilograms = Optional(int)
    weight_in_pounds = Optional(int)
    current_team = Optional("Team")
    last_updated = Required(datetime)
    stats = Set("Stat")


class Stat(db.db.Entity):
    _table_ = "stats"

    id = PrimaryKey(int, auto=False)
    assists = Optional(int)
    common_name = Optional(str)
    game_winning_goal = Optional(bool)
    goals = Optional(int)
    home_road_flag = Optional(bool)
    opponent_abbr = Optional(str)
    opponent_common_name = Optional(str)
    ot_goals = Optional(str)
    pim = Optional(int)
    plus_minus = Optional(int)
    points = Optional(int)
    power_play_goals = Optional(int)
    power_play_points = Optional(int)
    shifts = Optional(int)
    shorthanded_goals = Optional(int)
    shorthanded_points = Optional(int)
    shots = Optional(int)
    team_abbr = Optional(str)
    toi = Optional(str)
    game_date = Optional(date)
    player = Optional("Player")
    game_id = Optional(int)
    season = Required(str)


db.generate_mappings(create_tables=True)
