from db_connection import Base
from sqlalchemy import Column, Integer, String, Boolean, Date


class Stats(Base):
    __tablename__ = "stats"

    id = Column(Integer, primary_key=True)
    assists = Column(Integer)
    common_name = Column(String)
    game_winning_goal = Column(Boolean, default=False)
    goals = Column(Integer)
    home_road_flag = Column(Boolean)
    opponent_abbr = Column(String)
    opponent_common_name = Column(String)
    ot_goals = Column(Integer)
    pim = Column(Integer)
    plus_minus = Column(Integer)
    points = Column(Integer)
    power_play_goals = Column(Integer)
    power_play_points = Column(Integer)
    shifts = Column(Integer)
    shorthanded_goals = Column(Integer)
    shorthanded_points = Column(Integer)
    shots = Column(Integer)
    team_abbr = Column(String)
    toi = Column(Integer)
    game_date = Column(Date)
    player = Column(Integer)
    game_id = Column(Integer)
    season = Column(String)
