import os
from pony.orm import Database, db_session, select, commit, rollback
from contextlib import contextmanager
from dotenv import dotenv_values

from icecream import ic

try:
    DB_USER = os.environ.get("DB_USER")
    DB_PASSWORD = os.environ.get("DB_PASSWORD")
    DB_HOST = os.environ.get("DB_HOST", "localhost")
    DB_PORT = os.environ.get("DB_PORT", "5432")
    DB_NAME = os.environ.get("DB_NAME")

    if None in (DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME):
        config = dotenv_values(".env")
        DB_USER = config.get("DB_USER")
        DB_PASSWORD = config.get("DB_PASSWORD")
        DB_HOST = config.get("DB_HOST")
        DB_PORT = config.get("DB_PORT")
        DB_NAME = config.get("DB_NAME")
except Exception as e:
    ic(f"Error loading Database environment variables: {e}")
    raise e


class DatabaseConnection:
    def __init__(self, user=None, password=None, host=None, port=None, database=None):
        """
        Initializes the databases connetion parameters.

        Parameters:
            user: Database username.
                (default: from .env file or from env)
            password: Database user password.
                (default: from .env file or from env)
            host: Database host.
                (default: from .env file or from env or 'localhost')
            port: Database port.
                (default: from .env file or from env or '5432')
            database: Database name.
                (default: fron .env file or from env or 'postgres')
        """
        self.user = user or DB_USER
        self.password = password or DB_PASSWORD
        self.host = host or DB_HOST
        self.port = port or DB_PORT
        self.database = database or DB_NAME

        self.db = Database()
        self._connected = False

    def connect(self, debug=False):
        """
        Binds the database to PostgreSQL.

        Parameters:
            debug: Prints all SQL queries if set to True.

        Returns:
            True if connection to database is successful, False on error.
        """
        try:
            self.db.bind(
                provider="postgres",
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
                database=self.database,
            )

            if debug:
                from pony.orm import set_sql_debug

                set_sql_debug(True)

            self._connected = True
            # print("Successfully connected to database.")
            ic("Successfully connected to database.")
            return True
        except Exception as e:
            print(f"Error connecting to database: {e}")
            return False

    def generate_mappings(self, create_tables=False):
        """
        Generates the database mappings for all entities.

        Parameters:
            create_tables: Creates all tables that do not exist if set to True.
                (default: False)
        """
        if not self._connected:
            raise RuntimeError("Database not connected. Call connect() first.")

        try:
            self.db.generate_mapping(create_tables=create_tables)
            if create_tables:
                print("Tables created successfully")
        except Exception as e:
            print(f"Error generating mappings: {e}")

    def create_tables(self):
        """
        Creates all database tables as defined in entities.
        """
        self.generate_mappings(create_tables=True)

    def drop_all_tables(self):
        """
        Drops all database tables.
        WARNING: This deletes ALL DATA.
        """
        if not self._connected:
            raise RuntimeError("Database not connected. Call connect() first.")

        self.db.drop_all_tables(with_all_data=True)
        print("All tables dropped.")

    @db_session
    def get_all(self, entity, filters=None, **kwargs):
        """
        Gets all records from an entity with optional filtering available.

        Parameters:
            entity: PonyORM entity class.
            filters: A dictionary of optional filters.
                (default: None)
            **kwargs: Keyword arguments for filtering (e.g name='Tony')

        Returns:
            A list of entity instances.
        """
        # Merge filters dict and kwargs
        # Merge filters dict and kwargs
        all_filters = {}
        if filters:
            all_filters.update(filters)
        all_filters.update(kwargs)

        if all_filters:
            # Fetch all and filter in Python (avoids lambda decompiler issues)
            all_entities = list(entity.select())

            filtered_results = []
            for instance in all_entities:
                match = True
                for key, value in all_filters.items():
                    instance_value = getattr(instance, key, None)

                    # Handle foreign key relationships - compare IDs if value is an integer
                    if isinstance(value, int) and hasattr(instance_value, "id"):
                        if instance_value.id != value:
                            match = False
                            break
                    elif instance_value != value:
                        match = False
                        break

                if match:
                    filtered_results.append(instance)

            return filtered_results

        # No filters - return all
        return list(entity.select())

    @db_session
    def get_by_id(self, entity, id_value):
        """
        Gets a single record by the primary key.

        Parameter:
            entity: PonyORM entity class.
            id_value: Primary key value.

        Returns:
            Entity instance or None if not found.
        """
        return entity.get(id=id_value)

    @db_session
    def get_one(self, entity, filters=None, **kwargs):
        """
        Get a single record that matches the given filters.

        Parameters:
            entity: PonyORM entity class.
            filters: A dictonary of optional filters.
            **kwargs: Keyword arguments for filtering.

        Returns:
            Entity instance or None if not found.
        """
        all_filters = {}
        if filters:
            all_filters.update(filters)
        all_filters.update(kwargs)
        return entity.get(**all_filters) if all_filters else None

    @db_session
    def insert_one(self, entity, data=None, **kwargs):
        """
        Inserts a new record into the database.

        Parameters:
            entity: PonyORM entity class.
            data: A dictionary or object with attributes to insert.
                (this parameter is optional)
            **kwargs: Column values for the new record.

        Returns:
            The inserted entity instance.

        Examples:
            Method 1: Keyword arguments
                user = db.insert_one(User, name='Tony', age=25)

            Method 2:
                data = {'name': 'Tony', 'age': 25}
                user = db.insert_one(User, data=data)

            Method 3:
                class UserData:
                    name = 'Tony'
                    age = 25
                user = db.insert_one(User, data=UserData())
        """
        all_data = {}

        if data is not None:
            if isinstance(data, dict):
                all_data.update(data)
            else:
                all_data.update(
                    {k: v for k, v in data.__dict__.items() if not k.startswith("_")}
                )

        all_data.update(kwargs)
        instance = entity(**all_data)
        commit()
        return instance

    @db_session
    def insert_many(self, entity, records):
        """
        Insert multiple records into the database.

        Parameters:
            entity: PonyORM entity class.
            records: A list of dictionaries, objects, or both.

        Returns:
            List of inserted entity instances.

        Examples:
            List of dictionaries:
                records = [
                    {'name': 'Tony', 'age': 25},
                    {'name': 'Alvin', 'age': 43}
                ]
                users = db.insert_many(User, records)

            List of objects:
                class UserData:
                    def __init__(self, name, age):
                        self.name = name
                        self.age = age

                records = [
                    UserData('Tony', 25),
                    UserData('Alvin', 43)
                ]
                users = db.insert_many(User, records)
        """
        instances = []
        for record in records:
            if isinstance(record, dict):
                instances.append(entity(**record))
            else:
                data = {
                    k: v for k, v in record.__dict__.items() if not k.startswith("_")
                }
                instances.append(entity(**data))
        commit()
        return instances

    @db_session
    def update_one(self, entity, id_value, updates=None, **kwargs):
        """
        Updates a record by primary key.

        Parameters:
            entity: PonyORM entity class.
            id_value: Primary key value of record to update.
            updates: A dictionary or object with attributes to update.
                (this parameter is optional)
            **kwargs: Column values to update.

        Returns:
            The updated instance or None if record not found.

        Examples:
            Method 1: Keyword arguments
                user = db.update_one(User, name='Jeff', 'age' = 19)

            Method 2: Dictionary
                updates = {'name' = 'Jeff', 'age': 19}
                user = db.update_one(User, updates=updates)

            Method 3: Object with attributes
                class UpdateData:
                    name = 'Jeff'
                    age = 19
                user = db.update_one(User, updates=UpdateData())

            Method 4: Mix dictionary and kwargs (kwargs override)
                user = db.update_one(User, updates={'name':'Jeff'}, age=19))
        """
        instance = entity.get(id=id_value)
        if instance:
            all_updates = {}

            if updates is not None:
                if isinstance(updates, dict):
                    all_updates.update(updates)
                else:
                    all_updates.update(
                        {
                            k: v
                            for k, v in updates.__dict__.items()
                            if not k.starswith("_")
                        }
                    )

            all_updates.update(kwargs)

            instance.set(**all_updates)
            commit()
            return instance
        return None

    @db_session
    def update_many(self, entity, filters, updates=None, **kwargs):
        """
        Updates multiple records matching filters.

        Parameters:
            entity: PonyORM entity class.
            filters: A dictionary of column:value pairs to filter by.
            updates: A dictionary or object with attributes to update.
                (This parameter is optional)
            **kwargs: Column values to update.

        Returns:
            The number of records updated.

        Examples:
            Method 1: Keyword arguments
                count = db.update_many(User, {'name': 'Jeff'}, age=19)

            Method 2: Dictionary for updates
                updates = {'age': 19, 'city': 'Detroit'}
                count = db.update_many(User, {'name': 'Jeff'}, updates=updates)

            Method 3: Object with attributes
                class UpdateData:
                    age = 19
                    city = 'Detroit'
                count = db.update_many(User, {'name': 'Jeff'}, updates=UpdateData())

            Method 4: Mix dictionary and kwargs
                count = db.update_many(User, {'name': 'Jeff'}, updates={'age':19}, city='Detroit')
        """
        all_updates = {}

        # Handle updates parameter (dict or object)
        if updates is not None:
            if isinstance(updates, dict):
                all_updates.update(updates)
            else:
                # Assume it's an object with attributes
                all_updates.update(
                    {k: v for k, v in updates.__dict__.items() if not k.startswith("_")}
                )

        # Kwargs override updates
        all_updates.update(kwargs)

        # Fetch all and filter in Python (avoids lambda decompiler issues)
        all_entities = list(entity.select())

        records_to_update = []
        for instance in all_entities:
            match = True
            for key, value in filters.items():
                if getattr(instance, key, None) != value:
                    match = False
                    break
            if match:
                records_to_update.append(instance)

        count = 0
        for record in records_to_update:
            record.set(**all_updates)
            count += 1
        commit()
        return count

    @db_session
    def delete_one(self, entity, id_value):
        """
        Deletes a record by primary key.

        Parameter:
            entity: PonyORM entity class.
            id_value: Primary key value of record to delete.

        Returns:
            True if record is deleted, False if record not found.
        """
        instance = entity.get(id=id_value)
        if instance:
            instance.delete()
            commit()
            return True
        return False

    @db_session
    def delete_many(self, entity, filters=None, **kwargs):
        """
        Deletes multiple records matching filters.

        Parameters:
            entity: PonyORM entity class.
            filters: A dictionary or object with filter attributes.
                (This parameter is optional)
            **kwargs: Keyword arguments for filtering.

        Returns:
            The number of records deleted.

        Examples:
            Method 1: Keyword arguments
                count = db.delete_many(User, age=18)

            Method 2: Dictionary
                filters = {'name': 'Tony', 'age': 18}
                count = db.delete_many(User, filters=filters)

            Method 3: Object with attributes
                class FilterCriteria:
                    name = 'Tony'
                    age = 18
                count = db.delete_many(User, filters=FilterCriteria())

            Method 4: Mix dictionary and kwargs (kwargs override)
                count = db.delete_many(User, filters={'name':'Tony'}, age=18)
        """
        all_filters = {}

        # Handle filters parameter (dict or object)
        if filters is not None:
            if isinstance(filters, dict):
                all_filters.update(filters)
            else:
                # Assume it's an object with attributes
                all_filters.update(
                    {k: v for k, v in filters.__dict__.items() if not k.startswith("_")}
                )

        # Kwargs override filters
        all_filters.update(kwargs)

        if not all_filters:
            return 0  # Safety: don't delete all if no filters

        # Use entity.select() with filter
        query = entity.select()
        for key, value in all_filters.items():
            query = query.filter(lambda e: getattr(e, key) == value)

        records = list(query)
        count = len(records)
        for record in records:
            record.delete()
        commit()
        return count

    @db_session
    def execute_query(self, query, globals=None, locals=None):
        """
        Executes a raw SQL query.

        Parameters:
            query: SQL query string.
            globals: Global variables for query execution.
            locals: Local variables for query execution.

        Return:
            Query results
        """
        return list(self.db.select(query, globals=globals, locals=locals))

    @db_session
    def count(self, entity, **filters):
        """
        Count records matching filters.

        Parameters:
            entity: PonyORM entity class.
            **filters: Keyword arguments for filtering.

        Returns:
            The number of records.
        """
        if filters:
            return select(
                e for e in entity if all(getattr(e, k) == v for k, v in filters.items())
            ).count()
        return select(e for e in entity).count()

    @db_session
    def to_dict_with_relations(self, instance, exclude=None, relation_fields=None):
        """
        Converts entity instance to dictionary with expanded relationships.

        Parameters:
            exclude: Lisnt of fields to exclude.
                (default: ['id'])
            relationship_fields: A dictionary mapping the relation names of fields to include.
                If None, relations are included as full nested objects.

            Returns:
                A dictionary with expanded relationships.

            Examples:
                Include all fields from relations
                    data = db.to_dict_wiith_relations(
                        user,
                        exclude=['id'],
                        relation_fields={'location': ['city', 'state']}
                    )
        """
        if exclude is None:
            exclude = ["id"]

        # Get base dictionary
        result = instance.to_dict(exclude=exclude, with_collections=False)

        # Manually add relationships
        # Get all attributes from the instance
        for attr_name in dir(instance):
            # Skip private attributes and methods
            if attr_name.startswith("_"):
                continue

            try:
                attr_value = getattr(instance, attr_name)

                # Check if it's an entity instance (related object)
                if hasattr(attr_value, "_table_"):
                    # This is a related entity
                    if relation_fields and attr_name in relation_fields:
                        # Include only specified fields
                        result[attr_name] = {
                            field: getattr(attr_value, field)
                            for field in relation_fields[attr_name]
                        }
                    else:
                        # Include full object without id
                        result[attr_name] = attr_value.to_dict(exclude=["id"])
            except:
                # Skip any attributes that cause errors (methods, etc.)
                continue

        return result

    @db_session
    def get_all_with_relations(
        self, entity, filters=None, exclude=None, relation_fields=None, **kwargs
    ):
        """
        Get all records with expanded relationships as dictionaries.

        Parameters:
            entity: PonyORM entity class.
            filters: A dictionary or object with filter attributes.
                (This parameter is optional)
            exclude: A list of fields to exclude from results.
                (default: ['id'])
            relation_fields: A dictionary mapping relation names of fields to include.
            **kwargs: Keyword arguments for filtering.

        Returns:
            A list of dictionaries with expanded relationships.

        Examples:
            Get all users with full location information.
                users = db.get_all_with_relations(User, state='Michigan')

            With specific relation fields
                users = db.get_all_with_relations(
                    User,
                    relation_fields={'location': ['city', 'state']}
                )

            With filters
                users = db.get_all_with_relations(
                    User,
                    filters={'state': 'Michigan'},
                    exclude=['id'],
                    relation_fields={'location':['city']}
                )
        """
        entities = self.get_all(entity, filters=filters, **kwargs)

        return [
            self.to_dict_with_relations(
                e, exclude=exclude, relation_fields=relation_fields
            )
            for e in entities
        ]

    @db_session
    def get_one_with_relations(
        self, entity, filters=None, exclude=None, relation_fields=None, **kwargs
    ):
        """
        Gets a single record with expanded relationship information as a dictionary.

        Parameters:
            entity: PonyORM entity class.
            filters: A dictionary or object with filter attributes.
                (This parameter is optional)
            exclude: A list of fields to exclude from results.
                (default: ['id'])
            relation_fields: A dictionary mapping relation names of fields to include.
            **kwargs: Keyword arguments for filtering.

        Return:
            A dictionary with expanded relationships or None if record not found.

        Examples:
            Get user with location info
                user = db.get_one_with_relations(User, name='Tony')

            With specific relation fields
                user = db.get_one_with_relations(
                    User,
                    filters={'name': 'Tony'},
                    relation_fields={'location': ['city', 'state']}
                )

            By ID with relations
                user = db.get_one_with_relations(
                    User,
                    filters={'id': 1},
                    excludes=['id'],
                    relation_fields={'location': ['city', 'state']}
                )
        """
        instance = self.get_one(entity, filters=filters, **kwargs)

        if instance:
            return self.to_dict_with_relations(
                instance, exclude=exclude, relation_fields=relation_fields
            )

        return None

    @db_session
    def get_one_by_id_with_relations(
        self, entity, id_value, exclude=None, relation_fields=None
    ):
        """
        Gets a single record by ID with expanded relationships as a dictionary.

        Parameters:
            entity: PonyORM entity class.
            id_value: Primary key value.
            exclude: A list of fields to exclude from result.
                (default: ['id'])
            relation_fields: A dictionary mapping relation names of fields to include.

        Returns:
            A dictionary with expanded relationships or None if record not found.

        Examples:
            Get user by ID with location info
                user = db.get_one_by_id_with_relations(
                    User,
                    id_value=1,
                    relation_fields={'location': ['city', 'state']}
                )
        """
        instance = self.get_by_id(entity, id_value)

        if instance:
            return self.to_dict_with_relations(
                instance, exclude=exclude, relation_fields=relation_fields
            )

        return None

    @db_session
    def search_by_any_field(self, entity, search_value, fields, case_sensitive=False):
        """
        Search for a record where the search_value matches ANY of the specified fields.

        Parameters:
            entity: PonyORM entity class.
            search_value: Value to search for.
            fields: A list of field names to search in.

        Returns:
            First matching entity instance or None if not found.

        Examples:
            Search a user by first_name, last_name, or email
                user = db.search_by_any_field(
                    User,
                    'Tony',
                    ['first_name', 'last_name', 'email']
                )
        """
        all_entities = list(entity.select())

        if not case_sensitive:
            search_value_lower = search_value.lower()

            for instance in all_entities:
                for field in fields:
                    field_value = getattr(instance, field, None)
                    if field_value and field_value.lower() == search_value_lower:
                        return instance
        else:
            for instance in all_entities:
                for field in fields:
                    field_value = getattr(instance, field, None)
                    if field_value == search_value:
                        return instance

        return None

    @db_session
    def search_all_by_any_field(
        self, entity, search_value, fields, case_sensitive=False
    ):
        """
        Searches for all records where the search_value matches ANY of the specified fields.

        Parameters:
            entity: PonyORM entity class.
            search_value: The value to search for.
            fields: A list of field names to search in.
            case_sensitive: Performs case-insensitive search if set to False.
                (default: False)

        Returns:
            A list of entity instances matching the search_value. Or an empty list if nothing found.

        Examples:
            Find all users where name is 'Doe' (checking both first and last name field)
                users = db.search_all_by_any_field(User, 'Doe', ['first_name', 'last_name'])

            Find all users with location of New York.
                users = db.search_all_by_any_field(User, 'New York', ['city', 'state'])
        """
        # Fetch all entities and search in Python
        all_entities = list(entity.select())
        results = []

        if not case_sensitive:
            search_value_lower = search_value.lower()

            for instance in all_entities:
                for field in fields:
                    field_value = getattr(instance, field, None)
                    if field_value and field_value.lower() == search_value_lower:
                        results.append(instance)
                        break  # Don't add the same instance multiple times
        else:
            for instance in all_entities:
                for field in fields:
                    field_value = getattr(instance, field, None)
                    if field_value == search_value:
                        results.append(instance)
                        break  # Don't add the same instance multiple times
        return results

    @db_session
    def search_by_any_field_with_relations(
        self,
        entity,
        search_value,
        fields,
        exclude=None,
        relation_fields=None,
        case_sensitive=False,
    ):
        """
        Search for a record by multiple fields and returns with expanded relationships.

        Parameters:
            entity: PonyORM entity class.
            search_value: Value to search for.
            fields: A list of field names to search in.
            exclude: A list of fields to exclude from results.
                (default: ['id'])
            relation_fields: A dictionary mapping relation names to fields to include.

        Returns:
            A dictionary with expanded relationships or None if not found.

        Examples:
            Search user by any identifier and get full details
                user = db.search_by_any_field_with_relations(
                    User,
                    'Tony',
                    ['first_name', 'last_name', 'email'],
                    relaiton_fields={'location': ['city', 'state']}
                )
        """
        instance = self.search_by_any_field(
            entity, search_value, fields, case_sensitive=case_sensitive
        )

        if instance:
            return self.to_dict_with_relations(
                instance, exclude=exclude, relation_fields=relation_fields
            )

        return None

    @db_session
    def search_all_by_any_field_with_relations(
        self,
        entity,
        search_value,
        fields,
        exclude=None,
        relation_fields=None,
        case_sensitive=False,
    ):
        """
        Search for all records by multiple fields and returns with expanded relationships.

        Parameters:
            entity: PonyORM entity class.
            search_value: The value to search for.
            fields: A list of field names to search in.
            exclude: A list of fields to exclude from results.
                (default: ['id'])
            relation_field: A dictionary mapping relation names of fields to include.
            case_sensitive: Performs case-insensitive search when set to False.
                (default: False)

        Returns:
            A list of dictionaries with expanded relationships, or an empty list if no records are found.

        Examples:
            Search all users with name 'Doe'
                users = db.search_all_by_any_field_with_relations(
                    User,
                    'Doe',
                    ['first_name', 'last_name'],
                    relation_fields={'location': ['city', 'state']}
                )
        """
        instances = self.search_all_by_any_field(
            entity, search_value, fields, case_sensitive=case_sensitive
        )

        return [
            self.to_dict_with_relations(
                instance, exclude=exclude, relation_fields=relation_fields
            )
            for instance in instances
        ]

    def disconnect(self):
        """
        Disconnects from the database.
        """
        self.db.disconnect()
        print("Database connection closed.")


db = DatabaseConnection()


def init_db(
    user=None,
    password=None,
    host=None,
    port=None,
    database=None,
    debug=False,
    create_tables=False,
):
    """
    Initializes and connects to the database.

    Parameters:
        user: Database username.
        password: Database password.
        host: Database host.
        port: Database port.
        database: Database name.
        debug: Enables SQL debug output if set to True.
        create_tables: Creates database tables that do not exist if set to True.

    Returns:
        DatabaseConnection instance.
    """
    db_conn = DatabaseConnection(user, password, host, port, database)
    db_conn.connect(debug=debug)
    if create_tables:
        db_conn.create_tables()

    return db_conn
