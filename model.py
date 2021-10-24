
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Participant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    classname = db.Column(db.String(7), nullable=False)
    email_student = db.Column(db.String(120), unique=True, nullable=False)
    company_name = db.Column(db.String(80), nullable=False)
    trainer_name = db.Column(db.String(80), nullable=False)
    email_trainer = db.Column(db.String(120), nullable=False)
    student_validation = db.Column(db.String(40), unique=True)
    trainer_validation = db.Column(db.String(40), unique=True)
    student_validated = db.Column(db.Boolean(), default=False)
    trainer_validated = db.Column(db.Boolean(), default=False)

    def __repr__(self):
        return f'<Student {self.username}, {self.classname} from {self.company_name}>'
