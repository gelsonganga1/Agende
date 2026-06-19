from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flasgger import Swagger
from .config import Config
from .models import db
from .routes import api


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config["SWAGGER"] = {
        "title": "Agendamento Angola API",
        "description": "API centralizada para agendamento de serviços públicos em Angola",
        "version": "1.0.0",
        "termsOfService": "",
        "hide_top_bar": True,
    }

    CORS(app)
    db.init_app(app)
    JWTManager(app)
    Swagger(app, template={
        "swagger": "2.0",
        "info": {
            "title": "Agendamento Angola API",
            "description": "API para agendamento de serviços públicos. "
                           "Utilize o botão Authorize para testar rotas protegidas com JWT.",
            "version": "1.0.0",
        },
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "Token JWT no formato: Bearer <token>",
            }
        },
    })

    app.register_blueprint(api)

    with app.app_context():
        db.create_all()

    return app
