import logging
import logging.config

import flask
from flask import Response
from flask import request
from flask import jsonify
from .user_profile.user_profile import *

app = flask.Flask("user_profiles_api")

logging.config.fileConfig("logger.conf")
log = logging.root

@app.route("/health-check", methods=["Gapp.loggerET"])
def health_check():
    """
    Endpoint to health check API
    """
    log.info("Health Check!")
    return Response("All Good!", status=200)

@app.route('/users/<user>/profile', methods=['GET'])
def get_profiles(user):
    """
    Endpoint to get user profile data for a given organization/user.
    """
    log.info("Get users profiles")
    github_token = None
    if request.headers.get('x-github-auth-token') != None:
        github_token = request.headers['x-github-auth-token']

    return get_user_profile_data(user, github_token)


@app.errorhandler(BadRequest)
def handle_bad_request(error):
    """
    Handles bad request and returns status code 400.
    """
    log.error(error)
    payload = dict(error.payload or ())
    payload['status'] = error.status
    payload['message'] = error.message
    return jsonify(payload), 400


@app.errorhandler(BadCredentials)
def handle_bad_creds_request(error):
    """
    Handles bad credentials and returns status code 401.
    """
    log.error(error)
    payload = dict(error.payload or ())
    payload['status'] = error.status
    payload['message'] = error.message
    return jsonify(payload), 401

@app.errorhandler(ResourceNotFound)
def handle_resource_not_found_request(error):
    """
    Handles resource not found request and returns status code 404.
    """
    log.error(error)
    payload = dict(error.payload or ())
    payload['status'] = error.status
    payload['message'] = error.message
    return jsonify(payload), 404


@app.errorhandler(ForbiddenRequest)
def handle_forbidden_request(error):
    """
    Handles forbidden request and returns status code 403.
    """
    log.error(error)
    payload = dict(error.payload or ())
    payload['status'] = error.status
    payload['message'] = error.message
    return jsonify(payload), 403


@app.errorhandler(InvalidRequest)
def handle_invalid_request(error):
    """
    Handles invalid request and returns status code 422.
    """
    log.error(error)
    payload = dict(error.payload or ())
    payload['status'] = error.status
    payload['message'] = error.message
    return jsonify(payload), 422

@app.errorhandler(InternalServerError)
def handle_internal_exception(error):
    """
    Handles internal exception and returns status code 500.
    """
    log.error(error)
    payload = dict(error.payload or ())
    payload['status'] = error.status
    payload['message'] = error.message
    return jsonify(payload), 500

@app.errorhandler(Exception)
def handle_generic_exception(error):
    """
    Handles generic exception and returns status code 500.
    """
    log.error(error)
    payload = {}
    payload['status'] = 500
    payload['message'] = 'Internal server error'
    return jsonify(payload), 500

