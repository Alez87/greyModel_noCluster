#!/bin/bash
Tstart=$(date +%s%3N)

kill -9 $(lsof -i:25333 -t)
/usr/bin/yes | sudo pip uninstall py4j
sudo pip install py4j

javac -cp py4j/Jama-1.0.2.jar:py4j/py4j0.9.1.jar py4j/Grey.java py4j/IFilter.java
java -cp .:py4j/Jama-1.0.2.jar:py4j/py4j0.9.1.jar py4j/Grey py4j/IFilter &
sleep 1

Tend=$(date +%s%3N)
Tbuild=$(((Tend-Tstart)/1000))
echo "Time to build the environment: " $Tbuild"s"

python services_monitoring.py
