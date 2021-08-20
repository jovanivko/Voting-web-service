import base64

from flask import Flask, request, Response, jsonify
from ..configuration import Configuration
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, create_refresh_token, get_jwt, \
    get_jwt_identity
from ..admin.decorator import role_check

application = Flask(__name__)
application.config.from_object(Configuration)

jwt = JWTManager(application)


@application.route("/vote", methods=["POST"])
@role_check(role="official")
@jwt_required()
def vote():
    bytes=request.files.get('votes')
    votes=base64.decode(bytes)
    votes=votes.
    return Response(status=200)


if (__name__ == "__main__"):
    application.run(debug=True, host="0.0.0.0", port=5002);