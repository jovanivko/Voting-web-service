from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from flask import Response


def role_check(role):
    def inner_role(function):
        @wraps(function)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if ("roles" in claims) and (role in claims["roles"]):
                return function(*args, **kwargs)
            else:
                return Response("Permission denied!", status=403)

        return decorator

    return inner_role
