#!/bin/bash

trap 'kill $(jobs -p)' EXIT INT TERM

#export LOG_DIR=$HOME/hendrix_logs
sleep 2

echo "DATABASE_URL: ": $DATABASE_URL
echo "REDIS_URL: ": $REDIS_URL
python manage.py flush --no-input
python manage.py migrate

python manage.py msg_process_worker --sub_topic=worker-input --worker_class=websockets_server.core.chat_msg_worker:DbAccessWorker &
python manage.py msg_process_worker --sub_topic=worker-input-1 --worker_class=websockets_server.core.chat_msg_worker:DbAccessWorker &
python manage.py msg_process_worker --sub_topic=workers-responded --worker_class=websockets_server.tlgrm.tlgrm_notifier:HendrixTelegramNotify &
python manage.py msg_process_worker --sub_topic=hendrix --worker_class=websockets_server.tlgrm.tlgrm_notifier:HendrixTelegramNotify &
./bot_supervisor.sh &

sleep infinity
# gunicorn websockets_server.core.app:app --bind 0.0.0.0:${PORT} --workers 1 --worker-class aiohttp.worker.GunicornWebWorker
