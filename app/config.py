import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, "..", ".env"))


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key-change-in-production")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-secret-key-change-in-production")
    JWT_ACCESS_TOKEN_EXPIRES = 3600
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", f"sqlite:///{os.path.join(basedir, '..', 'data.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    OMBALA_API_KEY = os.getenv("OMBALA_API_KEY")
    OMBALA_SENDER_NAME = os.getenv("OMBALA_SENDER_NAME", "AGENDAMENTO")
