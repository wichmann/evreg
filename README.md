# evreg - Event Registration
A simple web app to register for a school event and validate mail addresses of
the student and the trainer.

## Usage
To start the web app with the internal web server of Flask:

    FLASK_ENV=development flask run

Or run the App directly in the pipenv:

    pipenv run flask run

## Docker
To build the image just execute the following command:

    docker image build -t evreg .

When running the container you can specify your actual configuration by
overwriting the existing file inside the container:

    docker run -p 5000:5000 -v ./config.actual.py:/app/config.py -d evreg

## Requirements
* email-validator
* flask
* flask-wtf
* flask-bootstrap
* flask-sqlalchemy
