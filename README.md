[![Docker Image CI](https://github.com/wichmann/evreg/actions/workflows/docker-image.yml/badge.svg)](https://github.com/wichmann/evreg/actions/workflows/docker-image.yml)
[![Docker](https://github.com/wichmann/evreg/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/wichmann/evreg/actions/workflows/docker-publish.yml)
[![MIT License](https://img.shields.io/badge/license-MIT-red.svg?style=flat)](http://choosealicense.com/licenses/mit/)

# evreg - Event Registration
A simple web app to register for a school event and validate mail addresses of
the student and the trainer.

## Configuration

Before running the application, you need to configure it by editing `config.py`:

1. Set a secure `SECRET_KEY` for session management
2. Configure Friendly Captcha credentials:
   - `FRIENDLY_CAPTCHA_SITEKEY`: Your Friendly Captcha site key (get it from https://friendlycaptcha.com/)
   - `FRIENDLY_CAPTCHA_SECRET`: Your Friendly Captcha API secret
3. Configure email settings for sending validation emails
4. Set `SHOW_LIST_PASSWORD` for protected access to participant lists
5. Set `ENLIST_OPEN` to `True` to enable registration

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
* flask-sqlalchemy
* requests (for Friendly Captcha verification)

## Licenses
This app uses the font "Raleway". Copyright 2010 The Raleway Project Authors
(impallari@gmail.com), with Reserved Font Name "Raleway". This Font Software is
licensed under the SIL Open Font License, Version 1.1. This license is
available with a FAQ at: https://openfontlicense.org
