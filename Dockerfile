FROM python:3.8.0-alpine

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN \
 apk add --no-cache postgresql-libs && \
 apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev &&\
 apk add bash

# install dependencies
RUN pip install --upgrade pip
RUN pip install pipenv

COPY Pipfile* /tmp/
RUN cd /tmp && pipenv lock --requirements > requirements.txt
RUN pip install -r /tmp/requirements.txt
RUN apk --purge del .build-deps

RUN mkdir -p /usr/src/app/logs/run
# copy project
COPY . /usr/src/app/
WORKDIR /usr/src/app/chat_websockets
ENV LOG_DIR=/usr/src/app/logs

EXPOSE 8080
CMD ./run_env.sh

# sudo docker container run --publish 8000:8080 --add-host=database:127.0.0.1 --net=host --detach --name hrx hendrix:1.0
