import json
from datetime import datetime

from flask import Flask, request, jsonify
from election.configuration import Configuration
from sqlalchemy import and_, or_
from decorator import role_check
from flask_jwt_extended import JWTManager, jwt_required
from election.models import database, Participant, ElectionParticipant, Election, Vote, InvalidVote

application = Flask(__name__)
application.config.from_object(Configuration)

jwt = JWTManager(application)


def getMaxIndex(list):
    max = 0
    maxindex = -1
    for i in range(0, len(list)):
        if (list[i] >= max):
            max = list[i]
            maxindex = i
    return maxindex


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

    try:
        start = datetime.fromisoformat(start)
        end = datetime.fromisoformat(end)
    except ValueError:
        return jsonify(message="Invalid date and time."), 400
    if end <= start or (Election.query.filter(or_(and_(Election.start <= start, Election.end >= start),
                                                  and_(Election.start <= end,
                                                       Election.end >= end)))).first() is not None:
        return jsonify(message="Invalid date and time."), 400
    if len(participants) <= 2:
        return jsonify(message="Invalid participant."), 400
    for participant in participants:
        p = Participant.query.filter(Participant.id == participant).first()
        if p is None or p.individual != individual:
            return jsonify(message="Invalid participant."), 400
    election = Election(start=start, end=end, individual=individual)
    database.add(election)
    database.commit()
    for participant in participants:
        electionParticipant = ElectionParticipant(electionId=election.id, participantId=participant)
        database.add(electionParticipant)
        database.commit()
    pollNumbers = [i for i in range(1, len(participants) + 1)]
    return jsonify(pollNumbers=pollNumbers)


@application.route("/getElections", methods=["GET"])
@jwt_required()
@role_check(role="admin")
def get_elections():
    elections = Election.query.all()
    return jsonify(elections="{}".format([election.__repr__() for election in elections]))


@application.route("/getResults", methods=["GET"])
@jwt_required()
@role_check(role="admin")
def get_results():
    id = request.args["id"];
    if id is None:
        return jsonify(message="Field id is missing."), 400
    election = Election.query.filter(Election.id == id).first()
    if election is None:
        return jsonify(message="Election does not exist."), 400
    now = datetime.now()
    if election.end >= now:
        return jsonify(message="Election is ongoing."), 400
    votes = Vote.query.filter(Vote.electionId == election.id).all()
    invalidvotes = InvalidVote.query.filter(InvalidVote.electionId == election.id).all()
    results = {}
    allVotes = 0
    for vote in votes:
        allVotes += 1
        participant = Participant.query.filter(Participant.id == election.participants[vote.pollNumber])
        try:
            results[vote.pollNumber][1] += 1
        except KeyError:
            results[vote.pollNumber] = [participant.name, 1]
    if election.individual:
        for participant in results.keys():
            results[participant][1] = "{0:.2f}".format(results[participant][1] / allVotes)
    else:
        seats = [0] * len(election.participants)
        quot = [results[participant][1] for participant in results.keys()]
        for i in range(0, 250):
            seatalloc = getMaxIndex(quot)
            seats[seatalloc] += 1
            quot = [results[participant][1] / (seats[participant] + 1) for participant in results.keys()]
        for participant in results.keys():
            results[participant][1] = seats[participant]

    return jsonify(participants="{}".format(
        [json.dumps({"pollNumber": participant, "name": results[participant][0], "result": results[participant][1]}) for
         participant in results.keys()]), invalidVotes=invalidvotes)
