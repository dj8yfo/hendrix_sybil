#!/bin/bash
# so as to not bother with telegram webhooks setup

trap 'kill $(jobs -p); exit' TERM INT
i=0
echo $(which python)
while :
do
	echo "inited $i iteration of telegram pybot"
	python websockets_server/tlgrm/tlgrm_listen.py &
	child=$!
	wait "$child"
	sleep 180
	((i++))
done
