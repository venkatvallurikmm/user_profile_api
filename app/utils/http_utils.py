from flask import Response
from flask import json
import requests

def send_error_rest_response(status, message):
    """
    For a given status and message returns HTTP Error Response.
    """
    return Response(
        status=status,
        response=json.dumps({'message': message}),
        mimetype='application/json')


def send_rest_response(status, data):
    """
    For a given status and data returns http Response.
    """
    return Response(
        status=status,
        response=json.dumps(data),
        mimetype='application/json'
    )

def get_response(url, token, custom_mimetype):
    """
    Gets the response for a given URL with custom_mimetype and optional token.
    """
    headers = {}
    if token != None and token != "":
        headers['Authorization'] = f'token {token}'
    if custom_mimetype != None:
        headers['Accept'] = custom_mimetype

    git_resp = requests.get(url, headers=headers)
    if git_resp.status_code == 400:
        raise BadRequest(git_resp.json())
    elif git_resp.status_code == 404:
        raise ResourceNotFound(git_resp.json())
    elif git_resp.status_code == 422:
        raise InvalidRequest(git_resp.json())
    elif git_resp.status_code == 401:
        raise BadCredentials(git_resp.json())
    elif git_resp.status_code == 403:
        raise ForbiddenRequest(git_resp.json())
    elif git_resp.status_code == 500:
        raise InternalServerError(git_resp.json())

    return git_resp.json()

class BadRequest(Exception):
    """
    Handles BadRequest exceptions.
    """
    def __init__(self, message, status=400, payload=None):
        self.message = message
        self.status = status
        self.payload = payload


class ResourceNotFound(Exception):
    """
    Handles ResourceNotFound exceptions.
    """
    def __init__(self, message, status=404, payload=None):
        self.message = message
        self.status = status
        self.payload = payload


class InvalidRequest(Exception):
    """
    Handles InvalidRequest exceptions.
    """
    def __init__(self, message, status=422, payload=None):
        self.message = message
        self.status = status
        self.payload = payload

class BadCredentials(Exception):
    """
    Handles BadCredentials exceptions.
    """
    def __init__(self, message, status=401, payload=None):
        self.message = message
        self.status = status
        self.payload = payload

class InternalServerError(Exception):
    """
    Handles InternalServerError exceptions.
    """
    def __init__(self, message, status=500, payload=None):
        self.message = message
        self.status = status
        self.payload = payload


class ForbiddenRequest(Exception):
    """
    Handles ForbiddenRequest exceptions.
    """
    def __init__(self, message, status=403, payload=None):
        self.message = message
        self.status = status
        self.payload = payload

