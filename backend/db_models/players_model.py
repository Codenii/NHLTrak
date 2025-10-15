from db_connection import Base
from sqlalchemy import Column, Integer, String, DateTime


class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True)
    birth_city = Column(String)
    birth_country = Column(String)
    birth_date = Column(String)
    birth_province_state = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    headshot = Column(String)
    height_in_centimeters = Column(Integer)
    height_in_inches = Column(Integer)
    position = Column(String)
    shoots_catches = Column(String)
    sweater_number = Column(Integer)
    weight_in_kilograms = Column(Integer)
    weight_in_pounds = Column(Integer)
    current_team = Column(Integer)
    last_updated = Column(DateTime)
