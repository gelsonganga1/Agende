from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flasgger import Swagger

db = SQLAlchemy()
jwt = JWTManager()
cors = CORS()
swagger = Swagger(template={
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
