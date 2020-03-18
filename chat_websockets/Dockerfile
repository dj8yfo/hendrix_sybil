FROM python:3.8.2-alpine3.11

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

ENV HOME=/home/app
ENV APP_HOME=/home/app/web
RUN mkdir -p $APP_HOME/logs/run
WORKDIR $APP_HOME
RUN addgroup -S app && adduser -S -G app app

COPY . $APP_HOME
ENV LOG_DIR=$APP_HOME/logs
RUN chown -R app:app $APP_HOME

EXPOSE 8080
USER app
CMD ./run_env.sh

# sudo docker container run --publish 8000:8080 --add-host=database:127.0.0.1 --net=host --detach --name hrx hendrix:1.0
