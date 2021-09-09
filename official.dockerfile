FROM python:3

RUN mkdir -p /opt/src/election
WORKDIR /opt/src/election

COPY election/official/application.py ./official/application.py
COPY election/configuration.py ./configuration.py
COPY election/decorator.py ./decorator.py
COPY election/models.py ./models.py
COPY election/requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

ENV PYTHONPATH="/opt/src"

ENTRYPOINT ["python", "./official/application.py"]
