from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user import User
from .department import Department
from .service import Service
from .appointment import Appointment
