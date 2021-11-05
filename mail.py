
import smtplib
from enum import Enum
from email.message import EmailMessage
from email.headerregistry import Address

from flask.helpers import url_for

import config


class MessageType(Enum):
    STUDENT = 1
    TRAINER = 2
    DELETED = 3


student_validation_text = """Hallo {username},

vielen Dank für das Interesse an der Excellence Initiative der BBS Brinkstraße.
        
Zur Bestätigung der Anmeldung müssen Sie noch einmal den folgenden Link anklicken, um Ihre Email-Adresse zu bestätigen:

    {validation_link}

Nach dem Klick auf den Bestätigungslink wird als nächstes eine Email an Ihre Ausbilderin bzw. Ihren Ausbilder versandt, in der sie bzw er der Teilnahme zustimmen muss.

Mit freundlichen Grüßen

Berufsbildende Schulen Brinkstraße
"""

trainer_validation_text = """Hallo {trainer_name},

Ihre Auszubildende bzw. Ihr Auszubildender {username} hat sich für die Excellence Initiative der BBS Brinkstraße angemeldet. Dabei geht es um eine AG mit dem Thema "Weiterentwicklung einer Smart Factory und Abbildung der wesentliche Prinzipien des Produktionsprozesses mit einem Projektmanagement nach dem Kanban-Prinzip". Weitere Informationen finden Sie auf der Homepage unter dem Link {info_link}.
        
Eine Teilnahme bedeutet einen weiteren Berufsschultag für die Auszubildenden. Dazu ist natürlich Ihr Einverständnis notwendig!
        
Wenn Sie damit einverstanden sind, dass Ihre Auszubildende bzw. Ihr Auszubildender {username} an der Excellence Initiative teilnehmen darf, klicken Sie bitte zur Bestätigung der Anmeldung auf den folgenden Link:

    {validation_link}

Mit freundlichen Grüßen

Berufsbildende Schulen Brinkstraße
"""


def send_mail(participant, message_type):
    """
    Send a specific mail in the registration process depending on the parameter 'message_type' (Enum 'MessageType').

    Source: https://docs.python.org/3.8/library/email.examples.html
    """
    # Create the base text message.
    msg = EmailMessage()
    msg['Subject'] = config.EMAIL_SUBJECT
    msg['From'] = Address(config.EMAIL_SENDER_NAME, config.EMAIL_SENDER_USER, config.EMAIL_SENDER_DOMAIN)
    if message_type == MessageType.STUDENT:
        user, domain = participant.email_student.split('@')
        msg['To'] = (Address(participant.get_full_name(), user, domain))
    elif message_type == MessageType.TRAINER:
        user, domain = participant.email_trainer.split('@')
        msg['To'] = (Address(participant.trainer_name, user, domain))
    else:
        print('Error!!!')
    if message_type == MessageType.STUDENT:
        msg.set_content(student_validation_text.format(username=participant.get_full_name(), validation_link=url_for('do_validate_student',
                        _external=True, student=participant.student_validation)))
    elif message_type == MessageType.TRAINER:
        msg.set_content(trainer_validation_text.format(trainer_name=participant.trainer_name, username=participant.get_full_name(),
                        info_link=url_for('info', _external=True),
                        validation_link=url_for('do_validate_trainer', _external=True, trainer=participant.trainer_validation)))
    else:
        print('Error!!!')

    # send the message via SMTP server.
    with smtplib.SMTP_SSL(config.EMAIL_SERVER_HOST, port=config.EMAIL_SERVER_PORT) as s:
        s.login(user=config.EMAIL_SERVER_USER, password = config.EMAIL_SERVER_PASSWORD)
        s.send_message(msg)
