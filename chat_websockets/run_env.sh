#!/bin/bash

trap 'kill $(jobs -p)' EXIT INT TERM

#export LOG_DIR=$HOME/hendrix_logs

python manage.py msg_process_worker --sub_topic=worker-input --worker_class=websockets_server.core.chat_msg_worker:DbAccessWorker &
python manage.py msg_process_worker --sub_topic=worker-input-1 --worker_class=websockets_server.core.chat_msg_worker:DbAccessWorker &
python manage.py msg_process_worker --sub_topic=worker-input-2 --worker_class=websockets_server.core.chat_msg_worker:DbAccessWorker &
python manage.py msg_process_worker --sub_topic=worker-input-3 --worker_class=websockets_server.core.chat_msg_worker:DbAccessWorker &
python manage.py msg_process_worker --sub_topic=workers-responded --worker_class=websockets_server.tlgrm.tlgrm_notifier:HendrixTelegramNotify &
python manage.py msg_process_worker --sub_topic=hendrix --worker_class=websockets_server.tlgrm.tlgrm_notifier:HendrixTelegramNotify &
./bot_supervisor.sh &

#gunicorn websockets_server.core.app:app --access-logfile /home/app/web/access.log --bind 0.0.0.0:8080 --workers 1 --worker-class aiohttp.worker.GunicornWebWorker
gunicorn websockets_server.core.app:app --bind 0.0.0.0:8080 --workers 1 --worker-class aiohttp.worker.GunicornWebWorker
