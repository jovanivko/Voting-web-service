from ast import literal_eval
from dateutil import parser
from datetime import datetime
from flask import Flask, request, jsonify
from election.configuration import Configuration
from sqlalchemy import and_, or_
from election.decorator import role_check
from flask_jwt_extended import JWTManager, jwt_required
from election.models import database, Participant, ElectionParticipant, Election, Vote, InvalidVote

application = Flask(__name__)
application.config.from_object(Configuration)

jwt = JWTManager(application)


def getMaxIndex(list):
    max = 0
    maxindex = -1
    for i in range(0, len(list)):
        if (list[i] > max):
            max = list[i]
            maxindex = i
    return maxindex


@application.route("/createParticipant", methods=["POST"])
@jwt_required()
@role_check(role="administrator")
def create_participant():
    name = request.json.get("name", "")
    individual = request.json.get("individual", "")
    if len(name) == 0:
        return jsonify(message="Field name is missing."), 400
    if len(str(individual)) == 0:
        return jsonify(message="Field individual is missing."), 400
    if len(name) > 256 or (type(individual) is not bool):
        return jsonify(message="Invalid input value."), 400
    participant = Participant(name=name, individual=individual)
    database.session.add(participant)
    database.session.commit()

    return jsonify(id=str(participant.id))


@application.route("/getParticipants", methods=["GET"])
@jwt_required()
@role_check(role="administrator")
def get_participants():
    participants = Participant.query.all()
    _list = [literal_eval(repr(participant)) for participant in
             participants]
    _list.sort(key=lambda x: x["name"])
    return jsonify(
        participants=_list)


@application.route("/createElection", methods=["POST"])
@jwt_required()
@role_check(role="administrator")
def create_election():
    start = request.json.get("start", "")
    end = request.json.get("end", "")
    individual = request.json.get("individual", "")
    participants = request.json.get("participants", "")

    if len(start) == 0:
        return jsonify(message="Field start is missing."), 400
    if len(end) == 0:
        return jsonify(message="Field end is missing."), 400
    if len(str(individual)) == 0:
        return jsonify(message="Field individual is missing."), 400
    if len(str(participants)) == 0:
        return jsonify(message="Field participants is missing."), 400

    try:
        start = parser.isoparse(start)
        end = parser.isoparse(end)
    except ValueError:
        return jsonify(message="Invalid date and time."), 400
    if end <= start or (Election.query.filter(or_(or_(and_(Election.start <= start, Election.end >= start),
                                                      and_(Election.start <= end,
                                                           Election.end >= end)),
                                                  and_(Election.start >= start,
                                                       Election.end <= end)))).first() is not None:
        return jsonify(message="Invalid date and time."), 400
    if len(participants) <= 2:
        return jsonify(message="Invalid participants."), 400
    for participant in participants:
        if type(participant) is not int:
            return jsonify(message="Invalid participants."), 400
        p = Participant.query.filter(Participant.id == participant).first()
        if p is None or p.individual != individual:
            return jsonify(message="Invalid participants."), 400
    election = Election(start=start, end=end, individual=individual)
    database.session.add(election)
    database.session.commit()
    for participant in participants:
        electionParticipant = ElectionParticipant(electionId=election.id, participantId=participant)
        database.session.add(electionParticipant)
        database.session.commit()
    pollNumbers = [i for i in range(1, len(participants) + 1)]
    return jsonify(pollNumbers=pollNumbers)


@application.route("/getElections", methods=["GET"])
@jwt_required()
@role_check(role="administrator")
def get_elections():
    elections = Election.query.all()
    _list = [literal_eval(repr(election)) for election in
             elections]
    _list.sort(key=lambda x: x["id"])
    return jsonify(elections=_list)


@application.route("/getResults", methods=["GET"])
@jwt_required()
@role_check(role="administrator")
def get_results():
    election_id = request.args.get("id");
    if election_id is None:
        return jsonify(message="Field id is missing."), 400
    election = Election.query.filter(Election.id == election_id).first()
    if election is None:
        return jsonify(message="Election does not exist."), 400
    now = datetime.now()
    if election.end >= now:
        return jsonify(message="Election is ongoing."), 400
    votes = Vote.query.filter(Vote.electionId == election.id).all()
    invalidvotes = InvalidVote.query.filter(InvalidVote.electionId == election.id).all()
    invalidvotes = [
        dict(ballotGuid=vote.guid, electionOfficialJmbg=vote.officialsJmbg, pollNumber=vote.pollNumber,
             reason=vote.reason)
        for vote in invalidvotes]
    results = {}
    allVotes = 0
    for vote in votes:
        allVotes += 1
        participant = Participant.query.filter(Participant.id == election.participants[vote.pollNumber - 1].id).first()
        try:
            results[vote.pollNumber - 1][1] += 1
        except KeyError:
            results[vote.pollNumber - 1] = [participant.name, 1]
    if election.individual:
        for participant in results.keys():
            results[participant][1] = round(results[participant][1] / allVotes, 2)
    else:
        seats = [0] * len(election.participants)
        census = int(allVotes * 0.05)
        quot = [0] * len(election.participants)
        for j in results.keys():
            if results[j][1] < census:
                results[j][1] = 0
            quot[j] = results[j][1]
        for i in range(0, 250):
            seatalloc = getMaxIndex(quot)
            print(seatalloc)
            seats[seatalloc] += 1
            for j in results.keys():
                quot[j] = results[j][1] / (seats[j] + 1)
        for participant in results.keys():
            results[participant][1] = seats[participant]

    return jsonify(participants=[
        {"name": results[participant][0], "pollNumber": participant + 1, "result": results[participant][1]} for
        participant in sorted(results.keys())], invalidVotes=invalidvotes)


@application.route("/", methods=["GET"])
def index():
    return "Hello world!";


if (__name__ == "__main__"):
    database.init_app(application);
    application.run(debug=True, host="0.0.0.0", port=5001);
