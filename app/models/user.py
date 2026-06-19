from datetime import datetime, timezone, timedelta
import random
from ..extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    role = db.Column(db.String(20), default="client")
    is_active = db.Column(db.Boolean, default=False)
    is_phone_verified = db.Column(db.Boolean, default=False)
    otp_code = db.Column(db.String(6), nullable=True)
    otp_expiry = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    appointments = db.relationship("Appointment", backref="user", lazy=True)

    def generate_otp(self):
        self.otp_code = f"{random.randint(0, 999999):06d}"
        self.otp_expiry = datetime.now(timezone.utc) + timedelta(minutes=5)
        return self.otp_code

    def verify_otp(self, code: str) -> bool:
        if not self.otp_code or not self.otp_expiry:
            return False
        now = datetime.now(timezone.utc)
        expiry = self.otp_expiry
        if expiry.tzinfo is None:
            expiry = expiry.replace(tzinfo=timezone.utc)
        if now > expiry:
            return False
        return self.otp_code == code

    def clear_otp(self):
        self.otp_code = None
        self.otp_expiry = None

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "role": self.role,
            "is_active": self.is_active,
            "is_phone_verified": self.is_phone_verified,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
