from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from werkzeug.datastructures import FileStorage

from counter.constants import Constants


class Base(DeclarativeBase):
    pass


class Helpers:
    @staticmethod
    def create_postgres_session_factory(database_url: str):
        """
        Creates and configures a PostgreSQL session factory using SQLAlchemy.

        This method initializes a database engine using the provided URL, creates all
        defined tables in the database if they don't exist, and returns a session factory
        that can be used to create new database sessions.

        :param database_url: A string containing the PostgreSQL connection URL
        :return: A configured SQLAlchemy sessionmaker instance for creating database sessions
        """
        engine = create_engine(database_url)
        Base.metadata.create_all(engine)
        return sessionmaker(engine)

    @staticmethod
    def validate_image_file(file: FileStorage) -> None:
        """
        Validates an uploaded image file to ensure it exists and has an allowed MIME type.
    
        This method checks if the provided file exists and verifies that its MIME type
        is among the allowed image types defined in Constants.ALLOWED_IMAGE_MIME_TYPES.
    
        Args:
            file (FileStorage): The file object to validate, typically from a file upload
    
        Raises:
            ValueError: If the file is missing or has an unsupported MIME type
        """

        if not file:
            raise ValueError("File is required.")
        if file.mimetype not in Constants.ALLOWED_IMAGE_MIME_TYPES:  # pragma: no cover
            raise ValueError(f"Unsupported image type: {file.mimetype}")
