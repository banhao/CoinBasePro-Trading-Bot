#!/bin/bash
clear
while true;
do
	_PROCESS=`ps -ef | grep "CoinBasePro_Trading_Bot.py" | grep -v grep`
	if [ -z $_PROCESS ]; then
		python3 -B CoinBasePro_Trading_Bot.py & echo $! >> run.pid
	fi
	sleep 600
done
