from _datetime import datetime

from flask import Flask
from election.configuration import Configuration
from election.models import database, Vote, InvalidVote, Election
from redis import Redis
from sqlalchemy import and_
from ast import literal_eval

application = Flask(__name__)
application.config.from_object(Configuration)

with application.app_context() as context:
    database.init_app(application)
    with Redis(host=Configuration.REDIS_HOST) as redis:
        channel = redis.pubsub()
        channel.subscribe(Configuration.REDIS_MESSAGE_CHANNEL)
        while True:
            message = channel.get_message()
            if (message and message["data"] != 1):
                now = datetime.now()
                datetime.now()
                jmbg = redis.get('jmbg')
                election = Election.query.filter(and_(Election.start <= now, Election.end >= now)).first()
                length = int(redis.get("length"))
                if election:
                    participants = election.participants
                for i in range(0, length):
                    bytes = redis.lpop(Configuration.REDIS_VOTES_LIST)
                    if bytes is not None:
                        vote = literal_eval(bytes.decode("utf-8"))
                        pollNumber = int(vote[1])
                        _Vote = Vote.query.filter(Vote.guid == vote[0]).first()
                        if not election:
                            continue
                        if _Vote is not None:
                            invalidvote = InvalidVote(guid=vote[0], officialsJmbg=jmbg, electionId=election.id,
                                                      pollNumber=pollNumber,
                                                      reason="Duplicate ballot.")
                            database.session.add(invalidvote)
                            database.session.commit()
                        elif pollNumber > len(participants):
                            invalidvote = InvalidVote(guid=vote[0], officialsJmbg=jmbg, electionId=election.id,
                                                      pollNumber=pollNumber,
                                                      reason="Invalid poll number.")
                            database.session.add(invalidvote)
                            database.session.commit()
                        else:
                            _Vote = Vote(pollNumber=pollNumber, electionId=election.id, officialsJmbg=jmbg,
                                         guid=vote[0])
                            database.session.add(_Vote)
                            database.session.commit()
