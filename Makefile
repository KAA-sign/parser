#!/bin/sh

export PYTHONPATH:=(shell pwd)/avito

run_admin:
	python avito/manage.py runserver

parse:
	python avito/manage.py parse_avito

makemigration:
	python avito/manage.py makemigration

migrate:
	python avito/manage.py migrate

