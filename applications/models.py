from applications.database import db 
from flask_login import UserMixin

class User(db.Model , UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(25), nullable=False)
    email = db.Column(db.String(200), unique=True , nullable = False)
    password=db.Column(db.String, nullable=False)
    role = db.Column(db.String(10) , nullable=False)
    approved = db.Column(db.Boolean , nullable = False , default = False)
    purchase = db.relationship("Purchases" , backref = 'user' , lazy = True)
    cart = db.relationship('Cart' , backref = 'user' , lazy = True)
    products = db.relationship("Product" , backref = 'user' , lazy= True)
    request = db.relationship("Request" , backref = 'user' , lazy = True)

class Categories(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer , primary_key  = True , autoincrement = True)
    name = db.Column(db.String(20) , nullable=  False)
    products = db.relationship("Product" , backref='categories' , lazy = True)



class Product(db.Model):
    __tablename__ = "product"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id') , nullable=False)
    name = db.Column(db.String(20), nullable=False)
    category = db.Column(db.Integer,db.ForeignKey('categories.id') , nullable=False)
    unit = db.Column(db.String(8),nullable = False)
    stock = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    expiry_date = db.Column(db.Date, nullable=False)
    orders = db.relationship("Orders", backref='product' ,lazy = True)
    cart = db.relationship("Cart" , backref = "product" , lazy = True)

class Purchases(db.Model):
    __tablename__ = "purchases"
    id = db.Column(db.Integer , primary_key = True , autoincrement = True)
    user_id = db.Column(db.Integer , db.ForeignKey("user.id") , nullable = False)
    order = db.relationship("Orders" , backref= "purchases" , lazy = True)

class Orders(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key = True , autoincrement = True)
    purchase_id = db.Column(db.Integer , db.ForeignKey('purchases.id') , nullable = False)
    product_id = db.Column(db.Integer , db.ForeignKey('product.id') , nullable = False)
    quantity = db.Column(db.Integer , nullable = False)
    sold_price = db.Column(db.Float , nullable = False)

class Request(db.Model):
    __tablename__ = 'request'
    id = db.Column(db.Integer , primary_key = True , autoincrement = True)
    request_by = db.Column(db.Integer ,db.ForeignKey('user.id') , nullable = False)
    request_type = db.Column(db.String(20), nullable = False)
    took_action = db.Column(db.Boolean , nullable = False, default = False)
    request_message = db.Column(db.String(200) , nullable = False)

class Cart(db.Model):
    __tablename__ = 'cart'
    id = db.Column(db.Integer , primary_key = True , autoincrement = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id') , nullable = False)
    product_id = db.Column(db.Integer , db.ForeignKey('product.id') , nullable = False)
    quantity = db.Column(db.Integer , nullable = False)
    price = db.Column(db.Integer , nullable = False)
    date = db.Column(db.Date , nullable = False)
