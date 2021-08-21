from _datetime import datetime

from flask import Flask, request, Response, jsonify
from ..configuration import Configuration
from sqlalchemy import and_
from decorator import role_check
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, create_refresh_token, get_jwt, \
    get_jwt_identity
from ..models import database, Participant, ElectionParticipant, Election

application = Flask(__name__)
application.config.from_object(Configuration)

jwt = JWTManager(application)


@application.route("/createParticipant", methods=["POST"])
@jwt_required()
@role_check(role="admin")
def create_participant():
    name = request.json.get("name", "")
    individual = request.json.get("individual", "")
    if len(name) == 0:
        return jsonify(message="Field name is missing."), 400
    if len(individual) == 0:
        return jsonify(message="Field individual is missing."), 400
    if len(name) > 256 or (bool(individual) is not bool):
        return jsonify(message="Invalid input value."), 400
    participant = Participant(name=name, individual=individual)
    database.session.add(participant)
    database.session.commit()

    return jsonify(id=str(participant.id))


@application.route("/getParticipants", methods=["GET"])
@jwt_required()
@role_check(role="admin")
def get_participants():
    participants = Participant.query.all()
    list = [{'id': participant.id, 'name': participant.name, 'individual': participant.individual} for participant in
            participants]
    return jsonify(participants=list)


@application.route("/createElection", methods=["POST"])
@jwt_required()
@role_check(role="admin")
def create_election():
    start = request.json.get("start", "")
    end = request.json.get("end", "")
    individual = request.json.get("individual", "")
    participants = request.json.get("participants", "")

    if len(start) == 0:
        return jsonify(message="Field start is missing."), 400

    if len(end) == 0:
        return jsonify(message="Field end is missing."), 400
    if len(individual) == 0:
        return jsonify(message="Field individual is missing."), 400
    if len(participants) == 0:
        return jsonify(message="Field participants is missing."), 400


    
    datetime.fromisoformat(start)
    return Response(status=200)


@application.route("/getElections", methods=["GET"])
@jwt_required()
@role_check(role="admin")
def get_elections():
    return Response(status=200)


@application.route("/getResults", methods=["GET"])
@jwt_required()
@role_check(role="admin")
def get_results():
    return Response(status=200)
