from db_connection import Base
from sqlalchemy import Column, Integer, String


class Conference(Base):
    __tablename__ = "conferences"

    id = Column(Integer, primary_key=True)
    abbr = Column(String)
    name = Column(String)


class Division(Base):
    __tablename__ = "divisions"

    id = Column(Integer, primary_key=True)
    abbr = Column(String)
    name = Column(String)
