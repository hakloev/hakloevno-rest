FROM python:3.5

MAINTAINER Håkon Ødegård Løvdal

ENV PYTHONUNBUFFERED 1
ENV NAME=hakloevno
ENV DIR=/srv/app

RUN mkdir $DIR
WORKDIR $DIR

ADD ./requirements.txt $DIR
RUN pip install -r requirements.txt --upgrade

ADD . $DIR

RUN mkdir -p static media
ENV DJANGO_SETTINGS_MODULE=$NAME.settings
RUN python manage.py collectstatic --noinput --clear

EXPOSE 8080
EXPOSE 8081

CMD ["sh", "docker-entrypoint.sh"]

