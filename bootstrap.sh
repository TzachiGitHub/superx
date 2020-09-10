#!/usr/bin/env bash

apt-get update
apt-get install python3 python3-pip -y
pip3 install flask
pip3 install flask-bootstrap PyMySQL mysql
pip3 install mysql-connector-python==8.0.11

export FLASK_APP=/vagrant/main.py

export FLASK_ENV=development

flask run -h 0.0.0.0 -p 5000
