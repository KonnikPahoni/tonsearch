FROM python:3.11-bullseye

WORKDIR /

COPY requirements.txt /

RUN pip3 install -r requirements.txt

EXPOSE 8008

COPY . /

RUN chmod 0644 cronjobs

RUN apt-get update && apt-get install -y cron && crontab /cronjobs

CMD service cron start && python manage.py collectstatic --noinput && python manage.py migrate && gunicorn tonnftscan.wsgi:application --bind 0.0.0.0:8008