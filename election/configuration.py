from datetime import timedelta
import os

try:
    databaseUrl = os.environ["DATABASE_URL"]
except KeyError:
    databaseUrl = "localhost"
try:
    redisHost = os.environ["REDIS_URI"]
except KeyError:
    redisHost = "localhost"


class Configuration():
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:root@{databaseUrl}/election"
    REDIS_HOST = redisHost
    REDIS_VOTES_LIST = "votes"
    REDIS_MESSAGE_CHANNEL = "notification"
    JWT_SECRET_KEY = "JWTSecretDevKey"
    JSON_SORT_KEYS = False
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=60)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
