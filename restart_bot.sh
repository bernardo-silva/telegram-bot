#!/bin/sh

pkill -f bot.py
source /home/bs/.virtualenvs/telegram/bin/activate
nohup python3 bot.py &
