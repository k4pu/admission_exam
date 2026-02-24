#!/bin/bash
time="$(date +%Y%m%d%H%M)"
output_file="/home/fpcrow/temp/$time.json"

/usr/bin/docker-compose exec web python manage.py dumpdata --natural-primary --natural-foreign --exclude=contenttypes --exclude=auth.permission --indent 2 > $output_file
