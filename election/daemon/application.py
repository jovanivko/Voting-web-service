from _datetime import datetime

from ..configuration import Configuration
from ..models import database, Vote, InvalidVote, Election
from redis import Redis
from sqlalchemy import and_

with Redis(host=Configuration.REDIS_HOST) as redis:
    channel = redis.pubsub()
    channel.subscribe(Configuration.REDIS_MESSAGE_CHANNEL)
    while True:
        channel.get_message()
        now = datetime.now()
        datetime.now()
        election = Election.query.filter(and_(Election.start <= now, Election.end >= now))
        if election is None:
            continue
        jmbg = redis.get('jmbg')
        length = redis.get("length")
        participants = Election.participants
        for i in range(0, length):
            vote = redis.lpop(Configuration.REDIS_VOTES_LIST)
            _Vote = Vote.query.filter(Vote.guid == vote[0])
            if Vote is not None:
                invalidvote = InvalidVote(guid=vote[0], officialsJmbg=jmbg, electionId=election.id, pollNumber=vote[1],
                                          reason="Duplicate ballot.")
                database.session.add(invalidvote)
                database.session.commit()
            elif vote[1] > len(participants):
                invalidvote = InvalidVote(guid=vote[0], officialsJmbg=jmbg, electionId=election.id, pollNumber=vote[1],
                                          reason="Invalid poll number.")
                database.session.add(invalidvote)
                database.session.commit()
            else:
                participantid = participants[vote[1]].id
                _Vote = Vote(participantId=participantid, electionId=election.id, officialsJmbg=jmbg, guid=vote[0])
                database.session.add(_Vote)
                database.session.commit()
