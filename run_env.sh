#!/bin/bash

trap 'kill $(jobs -p)' EXIT INT TERM
export LOG_DIR=$HOME/hendrix_logs
cd chat_websockets/
python manage.py msg_process_worker --sub_topic=worker-input --worker_class=websockets_server.core.chat_msg_worker:DbAccessWorker &
python manage.py msg_process_worker --sub_topic=worker-input-1 --worker_class=websockets_server.core.chat_msg_worker:DbAccessWorker &
python manage.py msg_process_worker --sub_topic=worker-input-2 --worker_class=websockets_server.core.chat_msg_worker:DbAccessWorker &
python manage.py msg_process_worker --sub_topic=worker-input-3 --worker_class=websockets_server.core.chat_msg_worker:DbAccessWorker &
python manage.py msg_process_worker --sub_topic=workers-responded --worker_class=websockets_server.tlgrm.tlgrm_notifier:HendrixTelegramNotify &
./bot_supervisor.sh
