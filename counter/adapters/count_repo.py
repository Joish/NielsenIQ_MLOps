from typing import List

from pymongo import MongoClient

from counter.adapters.helpers import Helpers
from counter.adapters.models import ObjectCountDB
from counter.constants import CountRepoConstants, Constants
from counter.domain.models import ObjectCount
from counter.domain.ports import ObjectCountRepo


class CountInMemoryRepo(ObjectCountRepo):

    def __init__(self):
        self.store = dict()

    def read_values(self, object_classes: List[str] = None) -> List[ObjectCount]:
        if object_classes is None:
            return list(self.store.values())

        return [self.store.get(object_class) for object_class in object_classes]

    def update_values(self, new_values: List[ObjectCount]):
        for new_object_count in new_values:
            key = new_object_count.object_class
            try:
                stored_object_count = self.store[key]
                self.store[key] = ObjectCount(key, stored_object_count.count + new_object_count.count)
            except KeyError:
                self.store[key] = ObjectCount(key, new_object_count.count)


class CountMongoDBRepo(ObjectCountRepo):  # pragma: no cover

    def __init__(self, host, port, database):
        self.__host = host
        self.__port = port
        self.__database = database

    def __get_counter_col(self):
        client = MongoClient(self.__host, self.__port)
        db = client[self.__database]
        counter_col = db.counter
        return counter_col

    def read_values(self, object_classes: List[str] = None) -> List[ObjectCount]:
        counter_col = self.__get_counter_col()
        query = {"object_class": {"$in": object_classes}} if object_classes else None
        counters = counter_col.find(query)
        object_counts = []
        for counter in counters:
            object_counts.append(ObjectCount(counter['object_class'], counter['count']))
        return object_counts

    def update_values(self, new_values: List[ObjectCount]):
        counter_col = self.__get_counter_col()
        for value in new_values:
            counter_col.update_one({'object_class': value.object_class}, {'$inc': {'count': value.count}}, upsert=True)


class CountPostgresRepo(ObjectCountRepo):
    """A PostgreSQL implementation of the ObjectCountRepo interface.

    This class provides a concrete implementation of the repository pattern for storing
    and retrieving object counts using a PostgreSQL database. It manages the persistence
    of ObjectCount entities through SQLAlchemy ORM.

    Attributes:
        __database_url (str): The PostgreSQL connection URL containing credentials and connection details
        __session_factory: A callable that creates new SQLAlchemy database sessions

    The class implements two main operations:
    - read_values: Retrieves object counts from the database
    - update_values: Updates or creates new object counts in the database
    """

    def __init__(self, user: str, password: str, host: str, port: str, database: str):
        self.__database_url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        self.__session_factory = Helpers.create_postgres_session_factory(self.__database_url)

    def read_values(self, object_classes: List[str] = None) -> List[ObjectCount]:
        """Fetches object counts from the database, optionally filtered by object classes."""
        if object_classes is None:
            object_classes = []

        with self.__session_factory() as session:
            query = session.query(ObjectCountDB)
            if object_classes:
                query = query.filter(ObjectCountDB.object_class.in_(object_classes))

            return [ObjectCount(row.object_class, row.count) for row in query.all()]

    def update_values(self, new_values: List[ObjectCount]):
        """Updates or creates new object counts in the database."""
        with self.__session_factory() as session:
            try:
                for value in new_values:
                    count_obj = session.query(ObjectCountDB).filter_by(object_class=value.object_class).first()

                    if count_obj:
                        count_obj.count += value.count
                    else:
                        count_obj = ObjectCountDB(object_class=value.object_class, count=value.count)
                        session.add(count_obj)

                session.commit()
            except Exception as e:  # pragma: no cover
                session.rollback()
                raise e


def count_repo_strategy(count_repo) -> ObjectCountRepo:
    """Creates and returns the appropriate repository instance based on the specified repository type.

    This function implements the Strategy pattern for repository selection, creating
    and configuring the appropriate repository implementation based on the provided
    repository type constant.

    Args:
        count_repo: A string constant from CountRepoConstants specifying which
                   repository implementation to use.

    Returns:
        ObjectCountRepo: An instance of the specified repository implementation,
                        configured with appropriate connection parameters.

    Raises:
        ValueError: If the provided repository type is not recognized.
    """

    if count_repo == CountRepoConstants.POSTGRES_REPO:
        return CountPostgresRepo(user=Constants.POSTGRES_USER,
                                 password=Constants.POSTGRES_PASSWORD,
                                 host=Constants.POSTGRES_HOST,
                                 port=Constants.POSTGRES_PORT,
                                 database=Constants.POSTGRES_DB)
    elif count_repo == CountRepoConstants.MONGO_REPO:
        return CountMongoDBRepo(host=Constants.MONGO_HOST,
                                port=Constants.MONGO_PORT,
                                database=Constants.MONGO_DB)
    elif count_repo == CountRepoConstants.IN_MEMORY_REPO:
        return CountInMemoryRepo()
    else:  # pragma: no cover
        raise ValueError(f"Invalid count repo name: {count_repo}")
