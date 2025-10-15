import os
from contextlib import contextmanager

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError

Base = declarative_base()


class DatabaseConnection:
    def __init__(self, user=None, password=None, host=None, port=None, database=None):
        """
        Init function to initialize database connection parameters.

        Parameters:
            user: Database username
            password: Database password
            host: Database host
            port: Database port
            database: Database name
        """
        self.user = user or os.environ.get("DB_USER", "")
        self.password = password or os.environ.get("DB_PASSWORD", "")
        self.host = host or os.environ.get("DB_HOST", "localhost")
        self.port = port or os.environ.get("DB_PORT", "5432")
        self.database = database or os.environ.get("DB_NAME", "postgres")

        self.engine = None
        self.SessionLocal = None

    def get_connection_string(self):
        """
        Generates connection string for PostgreSQL.
        """
        if self.password:
            return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
        else:
            return f"postgresql://{self.user}@{self.host}:{self.port}/{self.database}"

    def connect(self, echo=False):
        """
        Creates the database engine and session factory

        Parameters:
        echo: Logs all SQL statements if set to True
              (default: False)
        """
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
        """
        Tests connection to database, and prints version information if successful.
        """
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
        """
        Context manager for the database sessions.
        Automatically handles commit/rollback and cleanup.

        Usage Example:
            with db.get_session() as session:
                # Use session here
                pass
        """
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
        """
        Executes a query using raw sql and returns the results

        Parameters:
            query: The SQL query string
            params: A dictonary of query parameters.
                    (optional)

        Returns:
        sqlalchemy.engine.cursor.CursorResult:
            Returns the CursorResult of the SQL query that was ran.
        """
        with self.get_session() as session:
            result = session.execute(text(query), params or {})
            return result

    def get_all(self, model, filters=None, order_by=None, limit=None):
        """
        Gets all records from database table with optional filtering.

        Parameters:
            model: The SQLAlchemy model class.
            filters: A dictionary of column:value pairs to filter by.
            order_by: Column to order by (can be either column or column.desc()).
            limit: Max number of results to return.

        Returns:
            list: List of model instances.
        """
        with self.get_session() as session:
            query = session.query(model)

            if filters:
                for column, value in filters.items():
                    query = query.filter(getattr(model, column) == value)

            if order_by is not None:
                query = query.order_by(order_by)

            if limit:
                query = query.limit(limit)

            return query.all()

    def get_by_id(self, model, id_value, id_column="id"):
        """
        Get a single record by its ID.

        Parameters:
            model: The SQLAlchemy model class.
            id_value: The ID value to search for.
            id_column: The name of the ID column.
                       (default: 'id')

        Returns:
            The model instance, or None if the record is not found.
        """
        with self.get_session() as session:
            return (
                session.query(model)
                .filter(getattr(model, id_column) == id_value)
                .first()
            )

    def get_one(self, model, filters):
        """
        Gets a single record matching filters.

        Parameters:
            model: The SQLAlchemy model class
            filters: A dictionary of column:value pairs to filter by.

        Returns:
            The model instance, or None if the record is not found.
        """
        with self.get_session() as session:
            query = session.query(model)
            for column, value in filters.items():
                query = query.filter(getattr(model, column) == value)
            return query.first()

    def insert_one(self, model_instance):
        """
        Insert a single new record into the database.

        Parameters:
            model_instance: Instanco of a SQLAlchemy model.

        Returns:
            The inserted model instance with its ID.
        """
        with self.get_session() as session:
            session.add(model_instance)
            session.flush()
            session.refresh(model_instance)
            return model_instance

    def insert_many(self, model_instances):
        """
        Insert multiple records into the database.

        Parameters:
            model_instances: A list of SQLAlchemy model instances.

        Returns:
            A list of inserted model instances.
        """
        with self.get_session() as session:
            session.add_all(model_instances)
            session.flush()
            for instance in model_instances:
                session.refresh(instance)
            return model_instances

    def update_one(self, model, id_value, updates, id_column="id"):
        """
        Updates a single record by its ID.

        Parameters:
            model: SQLAlchemy model class.
            id_value: ID of record to update.
            id_column: The name of the ID column.
                       (default: 'id')

        Returns:
            The updated model instance, or None if record is not found.
        """
        with self.get_session() as session:
            record = (
                session.query(model)
                .filter(getattr(model, id_column) == id_value)
                .first()
            )

            if record:
                for column, value in updates.items():
                    setattr(record, column, value)
                session.flush()
                session.refresh(record)
                return record
            return None

    def update_many(self, model, filters, updates):
        """
        Updates multiple records matching filters.

        Parameters:
            model: SQLAlchemy model class.
            filters: A dictionary of column:value pairs to filter by.
            updates: A dictionary of column:value pairs to update.

        Returns:
            The number of updated records.
        """
        with self.get_session() as session:
            query = session.query(model)
            for column, value in filters.items():
                query = query = query.filter(getattr(model, column) == value)

            count = query.update(updates)
            return count

    def delete_one(self, model, id_value, id_column="id"):
        """
        Deletes a single record by ID.

        Parameters:
            model: SQLAlchemy model class.
            id_value: The ID value of the record to delete.
            id_column: The name of the ID column.
                       (default: 'id')

        Returns:
            True if the record is deleted, or False if the record is not found.
        """
        with self.get_session() as session:
            record = (
                session.query(model)
                .filter(getattr(model, id_column) == id_value)
                .first()
            )

            if record:
                session.delete(record)
                return True
            return False

    def delete_many(self, model, filters):
        """
        Deletes multiple records matching filters.

        Parameters:
            model: SQLAlchemy model class.
            filters: A dictionary of column:value pairs to filter by.

        Returns:
            The number records that were deleted.
        """
        with self.get_session() as session:
            query = session.query(model)
            for column, value in filters.items():
                query = query.filter(getattr(model, column) == value)

            count = query.delete()
            return count

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
