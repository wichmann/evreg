[![Docker Image CI](https://github.com/wichmann/evreg/actions/workflows/docker-image.yml/badge.svg)](https://github.com/wichmann/evreg/actions/workflows/docker-image.yml)

# evreg - Event Registration
A simple web app to register for a school event and validate mail addresses of
the student and the trainer.

## Usage
To start the web app with the internal web server of Flask:

    FLASK_DEBUG=True flask run

Or run the App directly in the pipenv:

    pipenv run flask run

## Docker
To build the image just execute the following command:

    docker image build -t evreg .

When running the container you can specify your actual configuration by
overwriting the existing file inside the container:

    docker run -p 5000:5000 -v ./config.actual.py:/app/config.py -d evreg

If you are using docker compose with a traefik reverse proxy, the configuration
could look like this:

    version: '3'

    services:
      evreg:
        build: https://github.com/wichmann/evreg.git
        volumes:
        - ./config.actual.py:/app/config.py
        image: evreg
        restart: always
        labels:
        - "traefik.enable=true"
        - "traefik.http.services.evreg.loadbalancer.server.port=5000"
        - "traefik.http.routers.evreg.rule=Host(`evreg.domain.com`)"
        - "traefik.http.routers.evreg.tls=true"
        - "traefik.http.routers.evreg.tls.certresolver=letsencrypt"

## Requirements
* email-validator
* flask
* flask-wtf
* flask-bootstrap
* flask-sqlalchemy
