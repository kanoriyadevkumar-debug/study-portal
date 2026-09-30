import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message_category = "error"


def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from app.auth.routes import auth_bp
    from app.materials.routes import materials_bp
    from app.courses.routes import courses_bp
    from app.resume.routes import resume_bp
    from app.opportunities.routes import opportunities_bp
    from app.main_routes import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(materials_bp, url_prefix="/materials")
    app.register_blueprint(courses_bp, url_prefix="/courses")
    app.register_blueprint(resume_bp, url_prefix="/resume")
    app.register_blueprint(opportunities_bp, url_prefix="/opportunities")

    with app.app_context():
        db.create_all()

    return app
