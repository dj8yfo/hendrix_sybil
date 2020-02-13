#!/bin/bash

. $(pipenv --venv)/bin/activate
cd chat_websockets/

python -m pytest
