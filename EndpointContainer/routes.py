from flask import request, secure_filename, Blueprint, jsonify, render_template

from functools import wraps

from typing import Any, Callable

import config
from factory import create_web_app
from util import *
import datetime
from google.cloud import storage
from authorize import authorize_user_for_submission

blueprint = Blueprint('routes', __name__, '')

def authorize_for_submission(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any):
        if request.auth: # try hasattr(request, 'auth')
            if request.auth.user and ('submission_id' in request.form):
                if (authorize_user_for_submission(request.auth.user.user_id, request.form['submission_id'])):
                    return func(*args, **kwargs)
        return jsonify ({"message": "You don't have permission to view this resource"}), 403
    return wrapper

@blueprint.route('/download', methods=['GET'])
@authorize_for_submission
def download (request):
    tar = get_file()
    source = untar(tar)
    return render_template(f"{request.form['submission_id']}.html")


@blueprint.route('/upload', methods=['POST'])
@authorize_for_submission
def upload (request):
    """Generates a v4 signed URL for uploading a blob using HTTP PUT.

    Note that this method requires a service account key file. You can not use
    this if you are using Application Default Credentials from Google Compute
    Engine or from the Google Cloud SDK.
    """
    bucket_name = 'latexml_submission_source'
    blob_name = request.auth.user + "_submission"

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    url = blob.generate_signed_url(
        version="v4",
        # This URL is valid for 10 minutes
        expiration=datetime.timedelta(minutes=10),
        # Allow PUT requests using this URL.
        method="PUT",
    )

    # print("Generated PUT signed URL:")
    # print(url)
    # print("You can use this URL with any user agent, for example:")
    # print(
    #     "curl -X PUT -H 'Content-Type: application/octet-stream' "
    #     "--upload-file my-file '{}'".format(url)
    # )
    # The above snippet is how to use the URL
    # Needs to be sent to XML endpoint in 
    return url
    # Do security things
    # We give them a signed write url
