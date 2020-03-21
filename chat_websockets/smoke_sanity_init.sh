#!/bin/bash

. "$(pipenv --venv)/"bin/activate

export LOG_DIR=$HOME/hendrix_logs
export IS_TEST=flag
export DATABASE_URL=postgres://chatw:chatw@localhost:5432/chatw
case "$1" in
	integration)
		trap 'sleep 5; kill $(jobs -p)' EXIT INT TERM
		rm dump.rdb
		redis-server /etc/redis/6379.conf --loglevel debug &
		(
		set -e
		trap 'kill $(jobs -p)' EXIT INT TERM
		python manage.py msg_process_worker --sub_topic=worker-input --worker_class=websockets_server.core.chat_msg_worker:DbAccessWorker &
		python manage.py msg_process_worker --sub_topic=worker-input-1 --worker_class=websockets_server.core.chat_msg_worker:DbAccessWorker &
		python manage.py msg_process_worker --sub_topic=worker-input-2 --worker_class=websockets_server.core.chat_msg_worker:DbAccessWorker &
		python manage.py msg_process_worker --sub_topic=worker-input-3 --worker_class=websockets_server.core.chat_msg_worker:DbAccessWorker &
		python manage.py msg_process_worker --sub_topic=workers-responded --worker_class=websockets_server.tlgrm.tlgrm_notifier:HendrixTelegramNotify &
		./bot_supervisor.sh &
		sleep 1
		python tests/websockets_server/core/views_integration_agnostic.py
		python -m pytest -k integration -v
		)
		status=$?
		if [ $status -ne 0 ];
		then
			echo "############################## ERROR ##############################"
			exit 127
		else
			echo "############################## SUCCESS ##############################"
			exit 0
		fi
		;;
	unit)
		coverage run -m pytest -k unit -v
		;;
	*)
		echo "not a valid action option: $1"
		;;
esac
