
"""
evreg - Event Registration

A simple web app to register for a school event and validate mail addresses of
the student and the trainer.

Requirements:
* flask
* flask-wtf
* flask-sqlalchemy
* flask-bootstrap

Sources:
 * https://hackersandslackers.com/flask-wtforms-forms/

"""

import csv
import uuid
from io import StringIO, BytesIO

from flask import Flask, render_template, redirect, request, make_response, abort, send_file
from flask.helpers import url_for
from flask_wtf import FlaskForm, RecaptchaField
from flask_wtf.csrf import CSRFProtect
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Email

import mail
import config
from model import db, Participant


csrf = CSRFProtect()


def init_app():
    """Initialize the core application."""
    app = Flask(__name__, template_folder='.')
    app.config['FLASK_DEBUG'] = 1
    app.config['DEBUG'] = True
    app.config['SECRET_KEY'] = config.SECRET_KEY
    app.config['RECAPTCHA_PUBLIC_KEY'] = config.RECAPTCHA_PUBLIC_KEY
    app.config['RECAPTCHA_PRIVATE_KEY'] = config.RECAPTCHA_PRIVATE_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    app.config['WTF_CSRF_SSL_STRICT'] = False
    app.config['ENLIST_OPEN'] = config.ENLIST_OPEN
    app.config['SHOW_LIST_PASSWORD'] = config.SHOW_LIST_PASSWORD

    csrf.init_app(app)
    db.init_app(app)
    with app.app_context():
        db.create_all()
        return app


app = init_app()


class RegisterStudentForm(FlaskForm):
    # build a HTML form corresponding to the data model in module model.py
    firstname = StringField(label=('Vorname:'),
                            validators=[DataRequired(), Length(min=3, max=80, message='Name muss zwischen %(min)d und %(max)d Zeichen lang sein!')])
    lastname = StringField(label=('Nachname:'),
                           validators=[DataRequired(), Length(min=3, max=80, message='Name muss zwischen %(min)d und %(max)d Zeichen lang sein!')])
    classname = StringField(label=('Klasse:'),
                            validators=[DataRequired(), Length(min=4, max=8, message='Klassenbezeichnung muss zwischen %(min)d und %(max)d Zeichen lang sein!')])
    email_student = StringField(label=('Email-Adresse Auszubildende(r)'),
                                validators=[DataRequired(), Email(message='Keine gültige Email-Adresse!'), Length(max=120)])
    company_name = StringField(label=('Name des Ausbildungsbetriebs:'),
                               validators=[DataRequired(), Length(min=3, max=80, message='Name muss zwischen %(min)d und %(max)d Zeichen lang sein!')])
    trainer_name = StringField(label=('Name der Ausbilderin bzw. des Ausbilders:'),
                               validators=[DataRequired(), Length(min=3, max=80, message='Name muss zwischen %(min)d und %(max)d Zeichen lang sein!')])
    email_trainer = StringField(label=('Email-Adresse Ausbilder(in)'),
                                validators=[DataRequired(), Email(message='Keine gültige Email-Adresse!'), Length(max=120)])
    recaptcha = RecaptchaField()
    submit = SubmitField('Anmelden')


def register_new_student(student_validation, firstname, lastname, classname, email_student, email_trainer, company_name, trainer_name):
    # create new Participant with a new UUID for teacher validation...
    new_participant = Participant(firstname=firstname.data, lastname=lastname.data, classname=classname.data, email_student=email_student.data,
                                  company_name=company_name.data, trainer_name=trainer_name.data, email_trainer=email_trainer.data,
                                  student_validation=student_validation.hex, trainer_validation=uuid.uuid4().hex)
    # ...and store her in the database
    db.session.add(new_participant)
    db.session.commit()


@app.route('/', methods=['GET'])
@app.route('/info', methods=['GET'])
def info():
    return render_template('templates/info.html')


@app.route('/contact', methods=['GET'])
def contact():
    return render_template('templates/contact.html')


@app.route('/impressum', methods=['GET'])
def impressum():
    return render_template('templates/impressum.html')


@app.route('/flyer', methods=['GET'])
def download_flyer():
    return send_file('static/flyer.pdf')


@app.route('/list', methods=['GET'])
def list_participants():
    list_of_participants = []
    if 'password' in request.args and request.args['password'] == config.SHOW_LIST_PASSWORD:
        list_of_participants = Participant.query.all()
    return render_template('templates/list.html', list_of_participants=list_of_participants)


@app.route('/download_list', methods=['GET'])
def download_list():
    if 'password' in request.args and request.args['password'] == config.SHOW_LIST_PASSWORD:
        list_of_participants = Participant.query.all()
        csv_file = StringIO()
        outcsv = csv.writer(csv_file)
        outcsv.writerow(
            [column.name for column in Participant.__mapper__.columns])
        for p in list_of_participants:
            outcsv.writerow([getattr(p, column.name)
                            for column in Participant.__mapper__.columns])
        csv_file.seek(0)
        return send_file(BytesIO(csv_file.read().encode('utf-8')), attachment_filename='teilnehmerliste.csv')
    return abort(403)


@app.route('/register', methods=['GET', 'POST'])
def index():
    form = RegisterStudentForm()
    if form.validate_on_submit():
        # TODO: Add better check for valid class names?
        p = Participant.query.filter_by(
            email_student=form.email_student.data).count()
        form.email_student.errors.append(
            'E-Mail-Adresse wurde bereits verwendet.')
        if p == 0:
            student_validation = uuid.uuid4()
            register_new_student(student_validation, form.firstname, form.lastname, form.classname, form.email_student,
                                 form.email_trainer, form.company_name, form.trainer_name)
            return redirect(url_for('validate_student', student=student_validation.hex, firsttime=True))
    return render_template('templates/register.html', form=form)


@app.route('/validate_student', methods=['GET'])
def validate_student():
    if 'student' in request.args:
        p = Participant.query.filter_by(
            student_validation=request.args['student']).first()
        if p:
            if 'firsttime' in request.args:
                if not p.student_validated:
                    # send mail only if student was not validated already
                    mail.send_mail(p, mail.MessageType.STUDENT)
                # return page with button to resend mail for student validation
                return render_template('templates/success.html', student_validation=p.student_validation,
                                       trainer_validation=p.trainer_validation, participant=p, firsttime=True)
            else:
                return render_template('templates/success.html', student_validation=p.student_validation,
                                       trainer_validation=p.trainer_validation, participant=p)
    return render_template('templates/success.html', student_validation='', trainer_validation='', participant='')


@app.route('/send_mail', methods=['GET'])
def send_mail_again():
    if 'student' in request.args:
        p = Participant.query.filter_by(
            student_validation=request.args['student']).first()
        if p:
            # send mail
            mail.send_mail(p, mail.MessageType.STUDENT)
            # return page with button to resend mail for student validation
            return render_template('templates/simple_message.html', success=True, message='Die Bestätigungsmail wurde ein weiteres Mal versendet.',
                                   title='Bestätigungsmail versenden')
    elif 'trainer' in request.args:
        p = Participant.query.filter_by(
            trainer_validation=request.args['trainer']).first()
        if p:
            # send mail
            mail.send_mail(p, mail.MessageType.TRAINER)
            # return page with button to resend mail for student validation
            return render_template('templates/simple_message.html', success=True, message='Die Bestätigungsmail wurde ein weiteres Mal versendet.',
                                   title='Bestätigungsmail versenden')
    return render_template('templates/simple_message.html', success=False, message='Die Bestätigungsmail konnte nicht versendet werden!',
                           title='Bestätigungsmail versenden')


@app.route('/do_validate_student', methods=['GET'])
def do_validate_student():
    if 'student' in request.args:
        p = Participant.query.filter_by(
            student_validation=request.args['student']).first()
        if p:
            print('{} was validated!'.format(p))
            # store validation in database
            p.student_validated = True
            db.session.commit()
            # send mail
            if not p.trainer_validated:
                mail.send_mail(p, mail.MessageType.TRAINER)
            # return page with information that trainer has to be validated next
            return render_template('templates/student_validated.html', participant=p)
    return render_template('templates/student_validated.html', participant=None)


@app.route('/do_validate_trainer', methods=['GET'])
def do_validate_trainer():
    if 'trainer' in request.args:
        p = Participant.query.filter_by(
            trainer_validation=request.args['trainer']).first()
        if p:
            print('{} was validated!'.format(p))
            # store validation in database
            p.trainer_validated = True
            db.session.commit()
            # return page saying the process is completed
            return render_template('templates/trainer_validated.html', student_validation=p.student_validation,
                                   trainer_validation=p.trainer_validation, username=p.get_full_name())
    return render_template('templates/trainer_validated.html', student_validation='', trainer_validation='', username='')


@app.route('/delete_registration', methods=['GET'])
def delete_registration():
    if 'student' in request.args:
        p = Participant.query.filter_by(
            student_validation=request.args['student']).first()
        if p:
            db.session.delete(p)
            db.session.commit()
            return render_template('templates/simple_message.html', success=True, message='Anmeldung wurde erfolgreich gelöscht!', title='Anmeldung löschen')
    return render_template('templates/simple_message.html', success=False, message='Die Anmeldung konnte nicht gelöscht werden!', title='Anmeldung löschen')


@app.errorhandler(404)
def not_found(error):
    """Page not found."""
    return make_response(render_template("templates/404.html"), 404)


if __name__ == "__main__":
    app.run(host='0.0.0.0')
