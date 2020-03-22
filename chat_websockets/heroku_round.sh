#!/bin/bash
heroku container:rm worker web --app=hrxftl
heroku container:push web worker --recursive --app=hrxftl
heroku container:release --app=hrxftl worker web
heroku ps:scale worker=1 --app=hrxftl
sleep 8
heroku ps --app=hrxftl
