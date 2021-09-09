FROM python:3

RUN mkdir -p /opt/src/election
WORKDIR /opt/src/election

COPY election/daemon/application.py ./daemon/application.py
COPY election/configuration.py ./configuration.py
COPY election/decorator.py ./decorator.py
COPY election/models.py ./models.py
COPY election/requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt
RUN rm -f /etc/localtime && ln -s /usr/share/zoneinfo/Europe/Belgrade /etc/localtime

ENV PYTHONPATH="/opt/src"

ENTRYPOINT ["python", "./daemon/application.py"]
