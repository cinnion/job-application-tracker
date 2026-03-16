#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

# Run the migrations
python manage.py migrate

# Update static files
rm -rf staticfiles/*
python manage.py collectstatic --no-input --ignore=css/* --ignore=js/* --ignore=applications/css/* --ignore=applications/js/*

exec "$@"
