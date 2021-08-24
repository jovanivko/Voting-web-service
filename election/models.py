from flask_sqlalchemy import SQLAlchemy
from authentication.models import User

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
    votes = database.relationship("Vote", back_populates="elections")

    def __repr__(self):
        return "{\n id: {},\n start: {},\n end: {},\n individual: {},\n participants: {}}".format(self.id,
                                                                                                  str(self.start),
                                                                                                  str(self.end),
                                                                                                  str(self.individual),
                                                                                                  [
                                                                                                      participant.__repr__()
                                                                                                      for participant in
                                                                                                      self.participants])


class Participant(database.Model):
    __tablename__ = "participants"

    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(256), nullable=False)
    individual = database.Column(database.BOOLEAN, nullable=False)

    elections = database.relationship("Election", secondary=ElectionParticipant.__table__,
                                      back_populates="patricipants")
    votes = database.relationship("Vote", back_populates="patricipants")

    def __repr__(self):
        return "{\n id: {}, \n name: {}\n}".format(self.id, self.name)


class Vote(database.Model):
    __tablename__ = "votes"

    guid = database.Column(database.Integer, primary_key=True)
    electionId = database.Column(database.Integer, database.ForeignKey("elections.id"), nullable=False)
    pollNumber = database.Column(database.Integer, database.ForeignKey("participants.id"), nullable=False)
    officialsJmbg = database.Column(database.String(13), nullable=False)


class InvalidVote(database.Model):
    __tablename__ = "invalidvotes"

    guid = database.Column(database.Integer, primary_key=True)
    electionId = database.Column(database.Integer, database.ForeignKey("elections.id"), nullable=False)
    pollNumber = database.Column(database.Integer, nullable=False)
    officialsJmbg = database.Column(database.String(13), nullable=False)
    reason = database.Column(database.String(256), nullable=False)

    def __repr__(self):
        return "{\n electionOfficialJmbg: {}, \n ballotGuid: {}\n pollNumber: {}\n reason: {}\n}".format(
            self.officialsJmbg, self.guid, self.pollNumber, self.reason)
