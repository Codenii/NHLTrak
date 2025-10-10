import os
from contextlib import contextmanager

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError

Base = declarative_base()


class DatabaseConnection:
    def __init__(self, user=None, password=None, host=None, port=None, database=None):
        self.user = user or os.environ.get("DB_USER", "")
        self.password = password or os.environ.get("DB_PASSWORD", "")
        self.host = host or os.environ.get("DB_HOST", "localhost")
        self.port = port or os.environ.get("DB_PORT", "5432")
        self.database = database or os.environ.get("DB_NAME", "postgres")

        self.engine = None
        self.SessionLocal = None

    def get_connection_string(self):
        if self.password:
            return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
        else:
            return f"postgresql://{self.user}@{self.host}:{self.port}/{self.database}"

    def connect(self, echo=False):
        try:
            conn_string = self.get_connection_string()
            self.engine = create_engine(conn_string, echo=echo)
            self.SessionLocal = sessionmaker(bind=self.engine)
            print(f"Successfully connected to database: {self.database}")
            return True
        except SQLAlchemyError as e:
            print(f"Error connecting to the database: {e}")
            return False

    def test_connection(self):
        if not self.engine:
            raise RuntimeError("Database not connected. Call connect() first.")

        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT version();"))
                version = result.fetchone()
                return version[0]
        except SQLAlchemyError as e:
            print(f"Connection test failed: {e}")
            return None

    @contextmanager
    def get_session(self):
        if not self.SessionLocal:
            raise RuntimeError("Database is not connected. Call connect() first.")

        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def execute_query(self, query, params=None):
        with self.get_session() as session:
            result = session.execute(text(query), params or {})
            # return result.fetchall()
            return result

    def close(self):
        if self.engine:
            self.engine.dispose()
            print("Database connection has been closed.")


db = DatabaseConnection()


def init_db(
    user=None, password=None, host="localhost", port="5432", database=None, echo=False
):
    db_conn = DatabaseConnection(user, password, host, port, database)
    db_conn.connect(echo=echo)
    return db_conn
