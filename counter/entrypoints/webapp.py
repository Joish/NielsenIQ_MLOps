import time
from http import HTTPStatus
from io import BytesIO

from flask import Flask, request, jsonify
from pydantic import ValidationError

from counter.adapters.helpers import Helpers
from counter.config import get_count_action
from counter.constants import Constants
from counter.domain.models import ObjectCountInput


def create_app():
    app = Flask(__name__)
    app.config['MAX_CONTENT_LENGTH'] = Constants.MAX_CONTENT_LENGTH

    @app.route('/health', methods=['GET'])
    def health_check():
        """
        Endpoint to check the health status of the application.

        Returns:
            tuple: A tuple containing:
                - JSON response with 'status' and 'timestamp' fields
                - HTTP status code 200 indicating a successful response
        """
        return jsonify({'status': 'healthy', 'timestamp': time.time()}), HTTPStatus.OK  # pragma: no cover

    @app.route('/v1/object-count', methods=['POST'])
    def object_detection():
        """
        Endpoint to detect and count objects in an uploaded image.

        Expects a multipart/form-data POST request with:
            - file: An image file in a supported format (JPEG, PNG)
            - model_name: Name of the detection model to use
            - threshold: Minimum confidence threshold for object detection
            - returns_total: Flag to indicate whether to return total object counts

        Returns:
            tuple: A tuple containing:
                - JSON response with detected object counts
                - HTTP status code:
                    * 200: Successful detection and counting
                    * 400: Invalid request (e.g., missing/invalid file)
                    * 422: Invalid form data
                    * 500: Internal server error

        Raises:
            ValidationError: If form data validation fails
            ValueError: If file validation fails
            Exception: For any other unexpected errors
        """
        try:
            # Validate file
            uploaded_file = request.files.get('file')
            Helpers.validate_image_file(uploaded_file)

            # Validate form data using Pydantic
            data = ObjectCountInput(**request.form)

            # Prepare image
            image = BytesIO()
            uploaded_file.save(image)

            # Process
            count_action = get_count_action(model_name=data.model_name)
            count_response = count_action.execute(image, data.threshold, data.return_total)
            return jsonify(count_response.model_dump(exclude_none=True)), HTTPStatus.OK

        except ValidationError as ve:
            return jsonify({"error": ve.errors()}), HTTPStatus.UNPROCESSABLE_ENTITY
        except ValueError as e:
            return jsonify({"error": str(e)}), HTTPStatus.BAD_REQUEST
        except Exception as e:  # pragma: no cover
            return jsonify({"error": "Internal server error", "details": str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR

    return app


if __name__ == '__main__':  # pragma: no cover
    app = create_app()
    app.run('0.0.0.0', debug=True)
