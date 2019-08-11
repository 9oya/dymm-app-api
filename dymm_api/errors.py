from flask import jsonify


def bad_req(message='Bad request'):
    return jsonify(ok=False,
                   message=message), 400


def unauthorized(pattern=None, message='Unauthorized'):
    return jsonify(ok=False,
                   pattern=pattern,
                   message=message), 401


def forbidden(pattern=None, message='Forbidden'):
    return jsonify(ok=False,
                   pattern=pattern,
                   message=message), 403


def ok(data=None, message='Ok'):
    return jsonify(ok=True,
                   message=message,
                   data=data), 200
