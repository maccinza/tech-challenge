#!/bin/sh
/wait
python manage.py migrate
python manage.py import_companies --filepath data/companies.json

exec "$@"
