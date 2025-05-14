import os

from counter.adapters.count_repo import count_repo_strategy
from counter.adapters.object_detector import object_detector_strategy
from counter.constants import CountRepoConstants, ModelConstants, EnvironmentConstants
from counter.domain.actions import CountDetectedObjects

_cached_actions = {}


def get_count_action(model_name) -> CountDetectedObjects:
    """
    Retrieves or creates a cached CountDetectedObjects action instance based on the environment and model name.

    This function manages a cache of CountDetectedObjects instances to avoid recreating them unnecessarily.
    In a development environment, it uses fake models and in-memory repositories, while in production
    it uses the actual specified model and PostgreSQL repository.

    Args:
        model_name (str): The name of the object detection model to use

    Returns:
        CountDetectedObjects: An instance of CountDetectedObjects configured with appropriate
        object detector and repository implementations based on the current environment
    """

    env = os.environ.get('ENV', 'dev')
    cache_key = (env.lower(), model_name)

    if cache_key not in _cached_actions:
        actual_model = ModelConstants.FAKE_MODEL_NAME if env.lower() == EnvironmentConstants.DEV else model_name
        count_repo = CountRepoConstants.IN_MEMORY_REPO if env.lower() == EnvironmentConstants.DEV else CountRepoConstants.POSTGRES_REPO

        _cached_actions[cache_key] = CountDetectedObjects(
            object_detector_strategy(model_name=actual_model),
            count_repo_strategy(count_repo=count_repo)
        )

    return _cached_actions[cache_key]
