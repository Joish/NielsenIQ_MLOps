from dataclasses import dataclass
from typing import List, Optional, Literal

from pydantic import BaseModel, Field

from counter.constants import Constants, ModelConstants


@dataclass
class Box:
    xmin: float
    ymin: float
    xmax: float
    ymax: float


@dataclass
class Prediction:
    class_name: str
    score: float
    box: Box


@dataclass
class ObjectCount:
    object_class: str
    count: int


class CountResponse(BaseModel):
    """Response model for object counting operations.

    This class represents the response structure for object detection and counting operations.
    It contains both the current count of detected objects and optionally the total historical
    count of all objects detected.

    Attributes:
        current_objects (List[ObjectCount]): List of object counts from the current detection.
        total_objects (Optional[List[ObjectCount]]): Optional list of total historical object counts.

    Configuration:
        exclude_none: Excludes None values from JSON serialization
    """
    current_objects: List[ObjectCount]
    total_objects: Optional[List[ObjectCount]] = None

    class Config:
        exclude_none = True


class ObjectCountInput(BaseModel):
    """Input model for object counting requests.

    This class defines the input parameters for object detection and counting operations.
    It includes configuration for detection threshold, model selection, and total count retrieval.

    Attributes:
        threshold (float): Confidence threshold for object detection, between 0.0 and 1.0.
        model_name (str): Name of the object detection model to use.
        return_total (bool): Flag to indicate whether to return total object counts.
    """

    threshold: float = Field(default=Constants.DEFAULT_THRESHOLD, ge=0.0, le=1.0)
    model_name: Literal[*ModelConstants.get_allowed_models()] = ModelConstants.RFCN_MODEL_NAME
    return_total: bool = False
