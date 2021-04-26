#!/bin/bash

cat run.pid | while read _PID;
do
	kill -9 $_PID;
done
> run.pid
clear
