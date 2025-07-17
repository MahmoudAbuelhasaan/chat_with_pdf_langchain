from app.auth.urls import auth_routs_bp


def register_routes(app):

    app.register_blueprint(auth_routs_bp,url_prefix='/auth')
