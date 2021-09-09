import csv
import io

from flask import Flask, request, Response, jsonify
from election.configuration import Configuration
from flask_jwt_extended import JWTManager, jwt_required, get_jwt
from redis import Redis;
from election.decorator import role_check

application = Flask(__name__)
application.config.from_object(Configuration)

jwt = JWTManager(application)


@application.route("/vote", methods=["POST"])
@jwt_required()
@role_check(role="user")
def vote():
    content = request.files.get("file", None)
    if not content:
        return jsonify(message="Field file is missing."), 400
    stream = io.StringIO(content.stream.read().decode(encoding='utf8'))
    reader = csv.reader(stream)
    for row in reader:
        if len(row) != 2:
            return jsonify(message="Incorrect number of values on line {}.".format(reader.line_num - 1)), 400
    stream.seek(0)
    reader = csv.reader(stream)
    for row in reader:
        try:
            int(row[1])
        except ValueError:
            return jsonify(message="Incorrect poll number on line {}.".format(reader.line_num - 1)), 400
        if int(row[1]) <= 0:
            return jsonify(message="Incorrect poll number on line {}.".format(reader.line_num - 1)), 400

    claims = get_jwt();
    stream.seek(0)
    reader = csv.reader(stream)
    votes = [(row[0], row[1]) for row in reader]
    with Redis(host=Configuration.REDIS_HOST) as redis:
        redis.set("jmbg", claims["jmbg"])
        redis.set("length", len(votes))
        for _vote in votes:
            redis.rpush(Configuration.REDIS_VOTES_LIST, str(_vote))
        redis.publish(Configuration.REDIS_MESSAGE_CHANNEL, "New ballot box.")

    return Response(status=200)


if (__name__ == "__main__"):
    application.run(debug=True, host="0.0.0.0", port=5002);
