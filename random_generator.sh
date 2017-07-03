#!/bin/bash

while(true)
do
	curl 127.0.0.1:5000/save/1/$((RANDOM % 100))/$((RANDOM % 100))/0
	curl 127.0.0.1:5000/save/12/$((RANDOM % 100))/$((RANDOM % 100))/0
	curl 127.0.0.1:5000/save/4/$((RANDOM % 100))/$((RANDOM % 100))/0
	sleep 0.8
done
