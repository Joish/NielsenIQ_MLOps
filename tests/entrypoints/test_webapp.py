import io
import json
from http import HTTPStatus
from pathlib import Path

import pytest

from counter.entrypoints.webapp import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def image_path():
    ref_dir = Path(__file__).parent
    return ref_dir.parent.parent / "resources" / "images" / "boy.jpg"


@pytest.fixture
def image_data(image_path):
    with open(image_path, 'rb') as f:
        return io.BytesIO(f.read())


def test_object_detection1(client, image_data):
    data = {'threshold': '0.9', 'model_name': 'rfcn', 'file': (image_data, 'test.jpg')}
    response = client.post('/v1/object-count', data=data,
                           content_type='multipart/form-data', buffered=True)
    assert response.status_code == HTTPStatus.OK
    assert json.loads(response.data)


def test_object_detection2(client, image_data):
    data = {'threshold': '0.9', 'model_name': 'fake', 'file': (image_data, 'test.jpg')}
    response = client.post('/v1/object-count', data=data,
                           content_type='multipart/form-data', buffered=True)
    assert response.status_code == HTTPStatus.OK
    assert json.loads(response.data)


def test_object_detection_validation_error1(client, image_data):
    data = {'threshold': '1.9', 'model_name': 'rfcn', 'file': (image_data, 'test.jpg')}
    response = client.post('/v1/object-count', data=data,
                           content_type='multipart/form-data', buffered=True)
    assert response.status_code == 422
    assert json.loads(response.data)


def test_object_detection_validation_error2(client, image_data):
    data = {'threshold': '1.9', 'model_name': 'rfcnn', 'file': (image_data, 'test.jpg')}
    response = client.post('/v1/object-count', data=data,
                           content_type='multipart/form-data', buffered=True)
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert json.loads(response.data)


def test_object_detection_value_error1(client):
    data = {'threshold': '1.9', 'model_name': 'rfcn'}
    response = client.post('/v1/object-count', data=data,
                           content_type='multipart/form-data', buffered=True)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert json.loads(response.data)
