from db_connection import Base
from sqlalchemy import Column, Integer, String


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True)
    abbr = Column(String)
    common_name = Column(String)
    name = Column(String)
    conference = Column(Integer)
    division = Column(Integer)
    logo = Column(String)
