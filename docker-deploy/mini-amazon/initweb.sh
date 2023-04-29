#!/bin/bash
python3 amazon_web/manage.py makemigrations
python3 amazon_web/manage.py migrate
res="$?"
while [ "$res" != "0" ]
do
    sleep 3;
    python3 amazon_web/manage.py migrate
    res="$?"
done

