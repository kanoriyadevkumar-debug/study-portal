from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="student")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    materials = db.relationship("Material", backref="uploader", lazy=True)
    resume = db.relationship("Resume", backref="owner", uselist=False, lazy=True)
    bookmarks = db.relationship("Bookmark", backref="user", lazy=True)
    enrollments = db.relationship("Enrollment", backref="student", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Material(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    tags = db.Column(db.String(200))
    filename = db.Column(db.String(300), nullable=False)
    uploaded_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    modules_text = db.Column(db.Text)  # one module per line
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    enrollments = db.relationship("Enrollment", backref="course", lazy=True)

    def module_list(self):
        if not self.modules_text:
            return []
        return [m.strip() for m in self.modules_text.splitlines() if m.strip()]


class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("course.id"), nullable=False)
    progress = db.Column(db.Integer, default=0)  # percent complete
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)


class Resume(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), unique=True, nullable=False)
    full_name = db.Column(db.String(120))
    phone = db.Column(db.String(30))
    education = db.Column(db.Text)
    skills = db.Column(db.Text)
    projects = db.Column(db.Text)
    experience = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Opportunity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    company = db.Column(db.String(150))
    type = db.Column(db.String(50))  # internship / job / hackathon
    location = db.Column(db.String(150))
    deadline = db.Column(db.String(50))
    link = db.Column(db.String(300))
    posted_by = db.Column(db.Integer, db.ForeignKey("user.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Bookmark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    opportunity_id = db.Column(db.Integer, db.ForeignKey("opportunity.id"), nullable=False)
    opportunity = db.relationship("Opportunity")
