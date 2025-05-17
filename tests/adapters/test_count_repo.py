import pytest

from counter.adapters.count_repo import CountPostgresRepo
from counter.adapters.count_repo import count_repo_strategy, CountInMemoryRepo, CountMongoDBRepo
from counter.constants import CountRepoConstants
from counter.domain.models import ObjectCount


def test_count_repo_strategy1():
    assert isinstance(count_repo_strategy(count_repo=CountRepoConstants.POSTGRES_REPO), CountPostgresRepo)
    assert isinstance(count_repo_strategy(count_repo=CountRepoConstants.IN_MEMORY_REPO), CountInMemoryRepo)
    assert isinstance(count_repo_strategy(count_repo=CountRepoConstants.MONGO_REPO), CountMongoDBRepo)


@pytest.fixture
def count_in_memory_repo():
    """Fixture to create a fresh in-memory repository for each test."""
    return CountInMemoryRepo()


@pytest.fixture
def repo():
    # credentials don't matter – they’re never used after monkey-patching
    return CountPostgresRepo("user", "pwd", "localhost", "5432", "irrelevant_db")


def test_read_values(count_in_memory_repo):
    """Test read_values() for both all objects and filtered ones."""
    # Setup initial data
    count_in_memory_repo.store = {
        'cat': ObjectCount('cat', 10),
        'dog': ObjectCount('dog', 5),
        'bird': ObjectCount('bird', 3),
    }

    # Test read all values
    result_all = count_in_memory_repo.read_values()
    assert len(result_all) == 3, "Expected three object counts"
    assert result_all[0].object_class == 'cat'
    assert result_all[1].object_class == 'dog'
    assert result_all[2].object_class == 'bird'

    # Test filtered values (only 'cat' and 'dog')
    result_filtered = count_in_memory_repo.read_values(object_classes=['cat', 'dog'])
    assert len(result_filtered) == 2, "Expected two object counts"
    assert result_filtered[0].object_class == 'cat'
    assert result_filtered[1].object_class == 'dog'


def test_update_values(count_in_memory_repo):
    """Test update_values() for updating existing values and adding new ones."""
    # Setup initial data
    count_in_memory_repo.store = {
        'cat': ObjectCount('cat', 10),
        'dog': ObjectCount('dog', 5),
    }

    # Test updating an existing value ('cat')
    count_in_memory_repo.update_values([ObjectCount('cat', 5)])
    assert count_in_memory_repo.store['cat'].count == 15, "Expected count for 'cat' to be 15"

    # Test adding a new value ('bird')
    count_in_memory_repo.update_values([ObjectCount('bird', 3)])
    assert count_in_memory_repo.store['bird'].count == 3, "Expected count for 'bird' to be 3"
    assert len(count_in_memory_repo.store) == 3, "Expected the store to contain three object counts"


def test_postgres_read_values_empty(repo):
    assert repo.read_values() == []


def test_postgres_update_and_read_multiple(repo):
    repo.update_values([
        ObjectCount("car", 3),
        ObjectCount("person", 2),
    ])
    values = sorted(repo.read_values(), key=lambda oc: oc.object_class)
    assert [(v.object_class, v.count) for v in values] == [("car", 3), ("person", 2)]


def test_postgres_increment_existing_value(repo):
    repo.update_values([ObjectCount("cat", 1)])
    repo.update_values([ObjectCount("cat", 4)])
    cat_count = repo.read_values(["cat"])[0]
    assert cat_count.count == 5
