from pony.orm import Required, Optional, PrimaryKey, Set
from datetime import datetime
from pony_db_connection import db


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
