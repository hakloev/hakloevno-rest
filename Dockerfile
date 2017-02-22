FROM python:3.5.3-alpine

MAINTAINER Håkon Ødegård Løvdal

ENV PYTHONUNBUFFERED 1
ENV NAME=hakloevno
ENV DIR=/srv/app

RUN mkdir $DIR
WORKDIR $DIR

ADD ./requirements $DIR/requirements
RUN pip install -r requirements/production.txt --upgrade

ADD . $DIR

RUN mkdir -p static media
ENV DJANGO_SETTINGS_MODULE=$NAME.settings.base
RUN python manage.py collectstatic --noinput --clear
ENV DJANGO_SETTINGS_MODULE=$NAME.settings.production

EXPOSE 8080
EXPOSE 8081

CMD ["sh", "docker-entrypoint.sh"]

