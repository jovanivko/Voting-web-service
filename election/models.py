from flask_sqlalchemy import SQLAlchemy
from ast import literal_eval

database = SQLAlchemy()


class ElectionParticipant(database.Model):
    __tablename__ = "electionparticipant"

    id = database.Column(database.Integer, primary_key=True)
    electionId = database.Column(database.Integer, database.ForeignKey("elections.id"), nullable=False)
    participantId = database.Column(database.Integer, database.ForeignKey("participants.id"), nullable=False)


class Election(database.Model):
    __tablename__ = "elections"

    id = database.Column(database.Integer, primary_key=True)
    start = database.Column(database.DATETIME, nullable=False, unique=True)
    end = database.Column(database.DATETIME, nullable=False, unique=True)
    individual = database.Column(database.BOOLEAN, nullable=False)

    participants = database.relationship("Participant", secondary=ElectionParticipant.__table__,
                                         back_populates="elections")
    votes = database.relationship("Vote")

    def __repr__(self):
        return "{{'id': {}, 'start': '{}', 'end': '{}', 'individual': {}, 'participants': {}}}".format(self.id,
                                                                                                       self.start,
                                                                                                       self.end,
                                                                                                       str(self.individual),
                                                                                                       [
                                                                                                           dict(id=
                                                                                                                participant.id,
                                                                                                                name=
                                                                                                                participant.name)
                                                                                                           for
                                                                                                           participant
                                                                                                           in
                                                                                                           self.participants])


class Participant(database.Model):
    __tablename__ = "participants"

    name = database.Column(database.String(256), nullable=False)
    individual = database.Column(database.BOOLEAN, nullable=False)
    id = database.Column(database.Integer, primary_key=True)

    elections = database.relationship("Election", secondary=ElectionParticipant.__table__,
                                      back_populates="participants")

    def __repr__(self):
        dict = {};
        dict["name"] = self.name
        dict["individual"] = self.individual
        dict["id"] = self.id
        return str(dict)


class Vote(database.Model):
    __tablename__ = "votes"

    guid = database.Column(database.String(40), primary_key=True)
    electionId = database.Column(database.Integer, database.ForeignKey("elections.id"), nullable=False)
    pollNumber = database.Column(database.Integer, nullable=False)
    officialsJmbg = database.Column(database.String(13), nullable=False)


class InvalidVote(database.Model):
    __tablename__ = "invalidvotes"

    id = database.Column(database.Integer, primary_key=True)
    guid = database.Column(database.String(40))
    electionId = database.Column(database.Integer, database.ForeignKey("elections.id"), nullable=False)
    pollNumber = database.Column(database.Integer, nullable=False)
    officialsJmbg = database.Column(database.String(13), nullable=False)
    reason = database.Column(database.String(256), nullable=False)

    def __repr__(self):
        return str(dict(ballotGuid=self.guid, electionOfficialJmbg=self.officialsJmbg, pollNumber=self.pollNumber,
                        reason=self.reason))
