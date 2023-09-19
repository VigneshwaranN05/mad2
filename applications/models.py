from applications.database import db 
from flask_sqlalchemy import SQLAlchemy 
from datetime import date 

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True , nullable = False)
    password=db.Column(db.String, nullable=False)

class Manager(db.Model):
    __tablename__ = "manager"
    manager_id = db.Column(db.Integer, primary_key=True , autoincrement=True)
    manager_name = db.Column(db.String, nullable=False)
    manager_email = db.Column(db.String,unique=True, nullable = False)
    password=db.Column(db.String, nullable=False)

class Product(db.Model):
    __tablename__ = "product"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    owner = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String, nullable=False)
    category = db.Column(db.String, nullable=False)
    unit = db.Column(db.String,nullable = False)
    stock = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    expiry_date = db.Column(db.Date, nullable=False)

class Purchases(db.Model):
    __tablename__ = "purchases"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product = db.Column(db.Integer, nullable=False)
    owner = db.Column(db.Integer, nullable=False)
    customer = db.Column(db.Integer, nullable=False)
    count = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable = False)
    date_added = db.Column(db.Date, nullable=False, default=date.today)