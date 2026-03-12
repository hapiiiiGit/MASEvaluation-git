from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    roblox_username = db.Column(db.String(64), nullable=False)
    private_server_info = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    transactions = db.relationship('Transaction', backref='user', lazy=True)

    def __init__(self, username, email, password_hash, roblox_username, private_server_info):
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.roblox_username = roblox_username
        self.private_server_info = private_server_info

class Item(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    roblox_asset_id = db.Column(db.String(64), nullable=False)

    transactions = db.relationship('Transaction', backref='item', lazy=True)

    def __init__(self, name, description, price, roblox_asset_id):
        self.name = name
        self.description = description
        self.price = price
        self.roblox_asset_id = roblox_asset_id

class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(32), nullable=False, default='pending')
    payment_provider = db.Column(db.String(32), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    delivery_proof_url = db.Column(db.String(256), nullable=True)

    def __init__(self, user_id, item_id, amount, status, payment_provider, delivery_proof_url=None):
        self.user_id = user_id
        self.item_id = item_id
        self.amount = amount
        self.status = status
        self.payment_provider = payment_provider
        self.delivery_proof_url = delivery_proof_url