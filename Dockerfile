FROM python:3.11-bullseye

WORKDIR /

COPY requirements.txt /

RUN pip3 install -r requirements.txt

EXPOSE 8001

COPY . /

CMD python manage.py collectstatic --noinput && python manage.py migrate && gunicorn tonnftscan.wsgi:application --bind 0.0.0.0:8001