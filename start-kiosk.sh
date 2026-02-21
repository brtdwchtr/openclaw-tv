#!/bin/bash
sleep 5
cd /home/bart/clawdpi-tv
python3 server.py &
sleep 2
export DISPLAY=:0
unclutter -idle 0 -root &
chromium --kiosk --no-sandbox --disable-gpu --password-store=basic --autoplay-policy=no-user-gesture-required http://localhost:8080/avatar.html
