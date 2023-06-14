"""HTTPS routes for the Flask app"""
from datetime import datetime
import os
from threading import Thread
import logging

import flask
from flask import Blueprint, request, jsonify, \
    current_app, Response

from .convert import process
from .publish import publish


# FlaskThread pushes the Flask applcation context
class FlaskThread(Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = current_app._get_current_object()

    def run(self):
        with self.app.app_context():
            super().run()

blueprint = Blueprint('routes', __name__)

# The post request from the eventarc trigger that queries this route will come in this format:
# https://github.com/googleapis/google-cloudevents/blob/main/proto/google/events/cloud/storage/v1/data.proto
@blueprint.route('/process', methods=['POST'])
def process_route () -> Response:
    """
    Takes in the eventarc trigger payload and creates a thread
    to perform the latexml conversion on the blob specified
    in the payload.

    Returns
    -------
    Response
        Returns a 202 response with no payload
    """
    logging.info (request.json)
    thread = FlaskThread(target=process, args=(request.json,))
    thread.start()
    return '', 202

@blueprint.route('/publish', methods=['POST'])
def publish_route () -> Response:
    logging.info(request.json)
    thread = FlaskThread(target=publish, args=(request.json,))
    thread.start()
    return '', 202

@blueprint.route('/health', methods=['GET'])
def health() -> tuple[flask.Response, int]:
    """
    Returns the latexml statuses and current time.

    Returns
    -------
    tuple[flask.Response, int]
        List of current cloud run tasks and the current time.
    """
    data = {
        "time": datetime.now(),
        "CLOUD_RUN_TASK_INDEX": list(os.environ.items())
    }
    print (data)
    return jsonify(data), 200
    