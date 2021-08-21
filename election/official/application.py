import csv
import io
import re

from flask import Flask, request, Response, jsonify
from ..configuration import Configuration
from flask_jwt_extended import JWTManager, jwt_required, get_jwt
from redis import Redis;
from ..admin.decorator import role_check

application = Flask(__name__)
application.config.from_object(Configuration)

jwt = JWTManager(application)


@application.route("/vote", methods=["POST"])
@jwt_required()
@role_check(role="official")
def vote():
    content = request.files["file"].stream.read().decode(encoding='utf8')
    if not content:
        return jsonify(message="Field file missing."), 400
    stream = io.StringIO(content)
    reader = csv.reader(stream)
    for i in range(0, len(reader) + 1):
        if len(reader[i]) != 2:
            return jsonify(message="Incorrect number of values on line {}.".format(i))
    for i in range(0, len(reader) + 1):
        if ((re.compile("^[0-9]+$")).fullmatch(reader[i][1]) is None) or int(reader[i][1]) <= 0:
            return jsonify(message="Incorrect poll number on line {}.".format(i))

    claims = get_jwt();
    votes = [(row[1], row[2]) for row in reader]
    with Redis(host=Configuration.REDIS_HOST) as redis:
        redis.set("jmbg", claims["jmbg"])
        redis.append("length", len(votes))
        for vote in votes:
            redis.append(Configuration.REDIS_VOTES_LIST, vote)
        redis.publish(Configuration.REDIS_MESSAGE_CHANNEL,"New ballot box.")


    return Response(status=200)


if (__name__ == "__main__"):
    application.run(debug=True, host="0.0.0.0", port=5002);
