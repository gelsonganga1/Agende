from flask import Flask
from .config import Config
from .extensions import db, jwt, cors, swagger
from .routes import api


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.config["SWAGGER"] = {
        "title": "Agendamento Angola API",
        "description": "API para agendamento de serviços públicos. "
                       "Utilize o botão Authorize para testar rotas protegidas com JWT.",
        "version": "1.0.0",
        "termsOfService": "",
        "hide_top_bar": True,
    }

    cors.init_app(app)
    db.init_app(app)
    jwt.init_app(app)
    swagger.init_app(app)

    app.register_blueprint(api)

    with app.app_context():
        db.create_all()

    return app
