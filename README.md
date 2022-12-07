Election voting service based on a microservice architecture, written in python, deployable with docker. For mutual communication, services use Reddis.

Service has two roles, administator and official. Administrator is concerned with starting the election, registering participants and calling the election winners, while election officials' responsibilities are counting and registering votes.

Seats are allocated using D'Hondt/Jefferson method.
