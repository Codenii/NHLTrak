import os
from pony.orm import Database, db_session, select, commit, rollback
from contextlib import contextmanager
from dotenv import dotenv_values

config = dotenv_values(".env")
DB_USER = config["DB_USER"]
DB_PASSWORD = config["DB_PASSWORD"]
DB_HOST = config["DB_HOST"]
DB_PORT = config["DB_PORT"]
DB_NAME = config["DB_NAME"]


class DatabaseConnection:
    def __init__(self, user=None, password=None, host=None, port=None, database=None):
        self.user = user or DB_NAME or os.environ.get("DB_USER", "")
        self.password = password or DB_PASSWORD or os.environ.get("DB_PASSWORD", "")
        self.host = host or DB_HOST or os.environ.get("DB_HOST", "localhost")
        self.port = port or DB_PORT or os.environ.get("DB_PORT", "5432")
        self.database = database or DB_NAME or os.environ.get("DB_NAME", "postgres")

        self.db = Database()
        self._connected = False

    def connect(self, debug=False):
        try:
            self.db.bind(
                provider="postgres",
                user=self.user,
                password=self.user,
                host=self.host,
                port=self.port,
                database=self.database,
            )

            if debug:
                from pony.orm import set_sql_debug

                set_sql_debug(True)

            self._connected = True
            print(f"Successfully connected to database: {self.database}")
            return True
        except Exception as e:
            print(f"Error connecting to database: {e}")
            return False

    def generate_mappings(self, create_tables=False):
        if not self._connected:
            raise RuntimeError("Database not connected. Call connect() first.")

        try:
            self.db.generate_mapping(create_tables=create_tables)
            if create_tables:
                print("Tables created successfully.")
        except Exception as e:
            print(f"Error generating mappings: {e}")

    def create_tables(self):
        self.generate_mappings(create_tables=True)

    def drop_all_tables(self):
        if not self._connected:
            raise RuntimeError("Database not connected. Call connect() first.")

        self.db.drop_all_tables(with_all_data=True)
        print("All tables dropped.")

    @db_session
    def get_all(self, entity, **filters):
        if filters:
            return list(
                select(
                    e
                    for e in entity
                    if all(getattr(e, k) == v for k, v in filters.items())
                )
            )

        return list(select(e for e in entity)[:])

    @db_session
    def get_by_id(self, entity, id_value):
        return entity.get(id=id_value)

    @db_session
    def get_one(self, entity, **filters):
        return entity.get(**filters)

    @db_session
    def insert_one(self, entity, **kwargs):
        instance = entity(**kwargs)
        commit()
        return instance

    @db_session
    def insert_many(self, entity, records):
        instances = [entity(**record) for record in records]
        commit()
        return instances

    @db_session
    def update_one(self, entity, id_value, **updates):
        instance = entity.get(id=id_value)
        if instance:
            instance.set(**updates)
            commit()
            return instance
        return None

    @db_session
    def update_many(self, entity, filters, **updates):
        records = select(
            e for e in entity if all(getattr(e, k) == v for k, v in filters.items())
        )
        count = 0

        for record in records:
            record.set(**updates)
            count += 1
        commit()
        return count

    @db_session
    def delete_one(self, entity, id_value):
        instance = entity.get(id=id_value)
        if instance:
            instance.delete()
            commit()
            return True
        return False

    @db_session
    def delete_many(self, entity, **filters):
        records = select(
            e for e in entity if all(getattr(e, k) == v for k, v in filters.items())
        )

        count = len(records)
        for record in records:
            record.delete()
        commit()
        return count

    @db_session
    def execute_query(self, query, globals=None, locals=None):
        return list(self.db.select(query, globals=globals, locals=locals))

    @db_session
    def count(self, entity, **filters):
        if filters:
            return select(
                e for e in entity if all(getattr(e, k) == v for k, v in filters.items())
            ).count()
        return select(e for e in entity).count()

    @db_session
    def disconnect(self):
        self.db.disconnect()
        print("Disconnected from database.")


db = DatabaseConnection()


def init_db(
    user=None,
    password=None,
    host="localhost",
    port="5432",
    database=None,
    debug=False,
    create_tables=False,
):
    db_conn = DatabaseConnection(user, password, host, port, database)
    db_conn.connect(debug=debug)

    if create_tables:
        db_conn.create_tables()

    return db_conn
