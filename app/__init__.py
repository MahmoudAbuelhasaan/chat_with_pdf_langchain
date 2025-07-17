from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_socketio import SocketIO
from config import Config
from flask_login import LoginManager
from flask_bcrypt import Bcrypt



db = SQLAlchemy()
socketio = SocketIO()
login_manager = LoginManager()
bcrypt = Bcrypt()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    socketio.init_app(app , cors_allowed_origins="*")
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    bcrypt.init_app(app)
    # Import and register blueprints
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    return app

@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))


