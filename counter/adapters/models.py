from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from counter.adapters.helpers import Base


class ObjectCountDB(Base):
    """SQLAlchemy model representing object count storage in the database.

    Attributes:
        object_class (str): Primary key representing the class/type of the detected object.
        count (int): The count of detected objects for the given class, defaults to 0.
    """

    __tablename__ = "object_counts"

    object_class: Mapped[str] = mapped_column(String, primary_key=True)
    count: Mapped[int] = mapped_column(Integer, default=0)
