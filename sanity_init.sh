#!/bin/bash

set -e

. "$(pipenv --venv)/"bin/activate
cd chat_websockets/

export LOG_DIR=$HOME/hendrix_logs
case "$1" in
	integration)
		trap 'kill $(jobs -p)' EXIT
		redis-server &
		python manage.py msg_process_worker --sub_topic=worker-input --worker_class=websockets_server.core.chat_msg_worker:AioredisWorker &
		python -m pytest -k integration
		;;
	unit)
		coverage run -m pytest -k unit -v
		;;
	*)
		echo "not a valid action option: $1"
		;;
esac

