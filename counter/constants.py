import inspect
import os


class Constants:
    DEFAULT_THRESHOLD = 0.5

    TFS_HOST = os.environ.get("TFS_HOST")
    TFS_PORT = os.environ.get("TFS_PORT")

    POSTGRES_HOST = os.environ.get("POSTGRES_HOST")
    POSTGRES_PORT = os.environ.get("POSTGRES_PORT")
    POSTGRES_USER = os.environ.get("POSTGRES_USER")
    POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
    POSTGRES_DB = os.environ.get("POSTGRES_DB")

    MONGO_HOST = os.environ.get("MONGO_HOST")
    MONGO_PORT = os.environ.get("MONGO_PORT")
    MONGO_USER = os.environ.get("MONGO_USER")
    MONGO_PASSWORD = os.environ.get("MONGO_PASSWORD")
    MONGO_DB = os.environ.get("MONGO_DB")

    ALLOWED_IMAGE_MIME_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}


class ModelConstants:
    RFCN_MODEL_NAME = "rfcn"
    FAKE_MODEL_NAME = "fake"

    @classmethod
    def get_allowed_models(cls):
        return [
            value for key, value in cls.__dict__.items()
            if not key.startswith("__") and not inspect.isroutine(value) and not isinstance(value, classmethod)
        ]


class CountRepoConstants:
    POSTGRES_REPO = "postgres"
    MONGO_REPO = "mongo"
    IN_MEMORY_REPO = "in_memory"


class EnvironmentConstants:
    DEV = "dev"
    PROD = "prod"
