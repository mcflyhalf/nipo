#!/bin/bash

export POSTGRES_USER="psql_username"
export POSTGRES_PASS=psql_password
export POSTGRES_PORT=5432
export POSTGRES_NIPO_DBNAME=nipo
export POSTGRES_NIPO_TEST_DBNAME=nipo_test
export FLASK_APP=nipo_api.py
export FLASK_ENV=development
export FLASK_SECRET_KEY= b'donotuseme' #generate a good one as described at https://flask.palletsprojects.com/en/1.1.x/quickstart/#sessions

