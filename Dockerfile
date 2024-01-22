FROM python:3.9

WORKDIR /

COPY requirements.txt /

RUN pip install -r requirements.txt

EXPOSE 8008

COPY . /

RUN chmod 0644 cronjobs && chmod 744 /var/run/crond.pid


RUN apt-get update && apt-get install -y cron
RUN crontab /cronjobs

CMD service cron start && python manage.py collectstatic --noinput && python manage.py migrate && gunicorn tonnftscan.wsgi:application --bind 0.0.0.0:8008