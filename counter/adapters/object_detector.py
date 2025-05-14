import json
from typing import List, BinaryIO

import numpy as np
import requests
from PIL import Image

from counter.constants import Constants, ModelConstants
from counter.domain.models import Prediction, Box
from counter.domain.ports import ObjectDetector


class FakeObjectDetector(ObjectDetector):
    def predict(self, image: BinaryIO) -> List[Prediction]:
        return [Prediction(class_name='cat',
                           score=0.999190748,
                           box=Box(xmin=0.367288858, ymin=0.278333426,
                                   xmax=0.735821366, ymax=0.6988855)
                           ),
                ]


class TFSObjectDetector(ObjectDetector):
    """TensorFlow Serving (TFS) based object detector implementation.

    This class implements the ObjectDetector interface to perform object detection
    using a TensorFlow model served via TensorFlow Serving. It communicates with
    the TFS server via REST API to get predictions.

    Args:
        host (str): Hostname or IP address of the TensorFlow Serving server
        port (int): Port number on which TFS server is listening
        model (str): Name of the model to use for predictions

    Attributes:
        url (str): Complete REST API URL for model predictions
        classes_dict (dict): Mapping of class IDs to human-readable class names
    """

    def __init__(self, host, port, model):
        self.url = f"http://{host}:{port}/v1/models/{model}:predict"
        self.classes_dict = self.__build_classes_dict()

    def predict(self, image: BinaryIO) -> List[Prediction]:
        np_image = self.__to_np_array(image)
        predict_request = '{"instances" : %s}' % np.expand_dims(np_image, 0).tolist()
        print(f"Sending request to TFS...{self.url}")
        response = requests.post(self.url, data=predict_request)
        predictions = response.json()['predictions'][0]
        return self.__raw_predictions_to_domain(predictions)

    @staticmethod
    def __build_classes_dict():
        with open('counter/adapters/mscoco_label_map.json') as json_file:
            labels = json.load(json_file)
            return {label['id']: label['display_name'] for label in labels}

    @staticmethod
    def __to_np_array(image: BinaryIO):
        image_ = Image.open(image)
        (im_width, im_height) = image_.size
        return np.array(image_.getdata()).reshape((im_height, im_width, 3)).astype(np.uint8)

    def __raw_predictions_to_domain(self, raw_predictions: dict) -> List[Prediction]:
        print("Parsing raw predictions...")
        num_detections = int(raw_predictions.get('num_detections'))
        predictions = []
        for i in range(0, num_detections):
            detection_box = raw_predictions['detection_boxes'][i]
            box = Box(xmin=detection_box[1], ymin=detection_box[0], xmax=detection_box[3], ymax=detection_box[2])
            detection_score = raw_predictions['detection_scores'][i]
            detection_class = raw_predictions['detection_classes'][i]
            class_name = self.classes_dict[detection_class]
            predictions.append(Prediction(class_name=class_name, score=detection_score, box=box))
        print(predictions)
        return predictions


def object_detector_strategy(model_name) -> ObjectDetector:
    """Creates and returns an appropriate ObjectDetector instance based on the model name.

    Args:
        model_name (str): Name of the model to be used for object detection.
            Must be one of the values defined in ModelConstants.

    Returns:
        ObjectDetector: An instance of ObjectDetector implementation based on the model name.
            Returns TFSObjectDetector for RFCN model or FakeObjectDetector for fake model.

    Raises:
        ValueError: If the provided model_name is not supported.
    """
    if model_name == ModelConstants.RFCN_MODEL_NAME:
        return TFSObjectDetector(host=Constants.TFS_HOST,
                                 port=Constants.TFS_PORT,
                                 model=ModelConstants.RFCN_MODEL_NAME
                                 )
    elif model_name == ModelConstants.FAKE_MODEL_NAME:
        return FakeObjectDetector()
    else:
        raise ValueError(f"Invalid model name: {model_name}")
