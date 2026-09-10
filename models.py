from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from database import db


class User(UserMixin, db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    email = db.Column(
        db.String(150),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    resumes = db.relationship(
        "Resume",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def set_password(self, password):

        self.password = generate_password_hash(password)

    def check_password(self, password):

        return check_password_hash(
            self.password,
            password
        )


class Resume(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    filename = db.Column(
        db.String(255),
        nullable=False
    )

    resume_text = db.Column(
        db.Text,
        nullable=False
    )

    skills = db.Column(
        db.Text,
        default=""
    )

    uploaded_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


class Job(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    title = db.Column(
        db.String(150),
        nullable=False
    )

    company = db.Column(
        db.String(150),
        nullable=False
    )

    location = db.Column(
        db.String(100)
    )

    description = db.Column(
        db.Text,
        nullable=False
    )

    required_skills = db.Column(
        db.Text,
        nullable=False
    )


class Analysis(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    resume_id = db.Column(
        db.Integer,
        db.ForeignKey("resume.id"),
        nullable=False
    )

    job_id = db.Column(
        db.Integer,
        db.ForeignKey("job.id"),
        nullable=False
    )

    score = db.Column(
        db.Float,
        nullable=False
    )

    matched_skills = db.Column(
        db.Text
    )

    missing_skills = db.Column(
        db.Text
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )