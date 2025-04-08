from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    shipments = db.relationship('Shipment', backref='created_by', lazy='dynamic')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
class Shipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    sender_id = db.Column(db.Integer, db.ForeignKey('client.id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('client.id'))
    carrier_id = db.Column(db.Integer, db.ForeignKey('carrier.id'))

    sender_name = db.Column(db.String(100))
    sender_phone = db.Column(db.String(20))
    sender_address = db.Column(db.String(200))

    recipient_name = db.Column(db.String(100))
    recipient_phone = db.Column(db.String(20))
    recipient_address = db.Column(db.String(200))

    destination_city = db.Column(db.String(100), nullable=False)

    carrier_name = db.Column(db.String(100))
    carrier_phone = db.Column(db.String(20))

    package_count = db.Column(db.Integer, nullable=False, default=1)
    weight_kg = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)
    notes = db.Column(db.Text)

    status = db.Column(db.String(50), nullable=False, default='En transit')  # 🆕

    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<Shipment {self.id} to {self.recipient_name} in {self.destination_city}>'

    
class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    address = db.Column(db.String(200))
    city = db.Column(db.String(100))
    is_sender = db.Column(db.Boolean, default=True)
    is_recipient = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations avec les envois
    shipments_as_sender = db.relationship('Shipment', 
                                         foreign_keys='Shipment.sender_id',
                                         backref='sender', lazy='dynamic')
    shipments_as_recipient = db.relationship('Shipment', 
                                            foreign_keys='Shipment.recipient_id',
                                            backref='recipient', lazy='dynamic')
    
    def __repr__(self):
        return f'<Client {self.name}>'
    
    def get_full_address(self):
        if self.address and self.city:
            return f"{self.address}, {self.city}"
        return self.address or self.city or "Adresse non renseignée"


class Carrier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relation avec les envois
    shipments = db.relationship('Shipment', backref='carrier', lazy='dynamic')
    
    def __repr__(self):
        return f'<Carrier {self.name}>'