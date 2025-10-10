from nhlpy import NHLClient
from icecream import ic
import time

from dotenv import dotenv_values

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

all_teams = []
all_players = []
all_divisions = []
all_conferences = []

# config = dotenv_values(".env")

# DB_USER = config["DB_USER"]
# DB_PASSWORD = config["DB_PASSWORD"]
# DB_HOST = config["DB_HOST"]
# DB_PORT = config["DB_PORT"]
# DB_NAME = config["DB_NAME"]

# db_con_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

client = NHLClient()

# try:
#     engine = create_engine(db_con_string, echo=False)

#     with engine.connect() as conn:
#         result = conn.execute(text("SELECT version();"))
#         version = result.fetchone()
#         ic(f"Successfully connected to PostgreSQL")
#         ic(f"PostgreSQL version: {version[0]}")

#     Session = sessionmaker(bind=engine)
#     session = Session()

#     result = session.execute(text("SELECT current_database();"))
#     db_name = result.fetchone()
#     ic(f"Current database: {db_name[0]}")

#     session.close()

# except SQLAlchemyError as e:
#     ic(f"Error connecting to database: {e}")
# finally:
#     if "engine" in locals():
#         engine.dispose()


teams = client.teams.teams()

ic(teams[0]["division"]["name"])
# for team in teams:
#     all_teams.append(team)
#     if team["conference"] not in all_conferences:
#         all_conferences.append(team["conference"])

#     if team["division"] not in all_divisions:
#         all_divisions.append(team["division"])

#     players = client.players.players_by_team(team["abbr"], "20252026")

#     for dmen in players["defensemen"]:
#         all_players.append(dmen)
#     for forward in players["forwards"]:
#         all_players.append(forward)
#     for goalie in players["goalies"]:
#         all_players.append(goalie)

#     time.sleep(0.5)

# ic(all_teams)
# ic(len(all_teams))

# ic(all_conferences)
# ic(len(all_conferences))

# ic(all_divisions)
# ic(len(all_divisions))

# ic(len(all_players))
