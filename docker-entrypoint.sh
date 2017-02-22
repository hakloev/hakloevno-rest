#!/usr/bin/env sh
python manage.py migrate

rm /tmp/project-master.pid

touch /srv/app/hakloevno.log
tail -n 0 -f /srv/app/*.log &

echo Starting uWSGI

exec uwsgi --chdir=/srv/app \
    --module=hakloevno.wsgi:application \
    --env DJANGO_SETTINGS_MODULE=hakloevno.settings.production \
    --master --pidfile=/tmp/project-master.pid \
    --socket=0.0.0.0:8080 \
    --http=0.0.0.0:8081 \
    --buffer-size=32768 \
    --processes=5 \
    --harakiri=20 \
    --max-requests=5000 \
    --offload-threads=4 \
    --static-map=/static=/srv/app/static \
    --static-map=/media=/srv/app/media \
    --vacuum
