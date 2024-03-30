FROM python:3.9.5-slim-buster

WORKDIR /

COPY requirements.txt /

RUN pip3 config --user set global.progress_bar off
RUN pip3 install -r requirements.txt

EXPOSE 8008

COPY . /
RUN ls var

RUN chmod 0644 cronjobs && chmod +x renew.sh

RUN apt-get update && apt-get install -y cron
RUN crontab /cronjobs

CMD service cron start && python manage.py collectstatic --noinput && python manage.py migrate && gunicorn tonnftscan.wsgi:application --bind 0.0.0.0:8008