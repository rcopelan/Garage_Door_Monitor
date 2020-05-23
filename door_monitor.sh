#!/bin/bash
while true
do
  echo "door_monitor.py starting"
  python3 /home/pi/sensors/door_monitor.py &
  echo "door_monitor.py started" 
  wait $!
  echo "door_monitor.py stopped" 
  sleep 10
done
exit


