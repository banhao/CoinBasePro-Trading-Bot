#!/bin/bash
clear
while true;
do
	_PROCESS=`ps -ef | grep "CoinBasePro.py" | grep -v grep`
	if [ -z $_PROCESS ]; then
		python3 -B CoinBasePro.py & echo $! >> run.pid
	fi
	sleep 900
done
