from flask_restful import Resource, reqparse
from datetime import datetime
from flask import request
from passlib.hash import pbkdf2_sha256 as passhash
from applications.models import Product, db

parser = reqparse.RequestParser()
parser.add_argument('name', type=str)
parser.add_argument('category', type=str)
parser.add_argument('unit', type=str)
parser.add_argument('stock', type=int)
parser.add_argument('price', type=int)
parser.add_argument('expiry_date', type=str)

class ProductResource(Resource):
    def get(self, product_id):
        product = Product.query.get(product_id)
        if product:
            response_data = {
                'id': product.id,
                'owner': product.owner,
                'name': product.name,
                'category': product.category,
                'unit': product.unit,
                'stock': product.stock,
                'price': product.price,
                'expiry_date': product.expiry_date.strftime('%Y-%m-%d')  # Format date as 'YYYY-MM-DD'
            }
            return response_data, 200
        return {"message": "Product not found"}, 404

    
    def post(self):
        # Implement logic to create a new product
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        manager = Manager.query.filter_by(manager_email=email).first()
        if not manager:
            return {"message": "Manager Email not found"}, 401

        if not passhash.verify(password,manager.password):
            return {"message": "Authentication Failed"}, 401

        expiry_date_str = data.get('expiry_date')
        try:
            expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d').date()
        except ValueError:
            return {"message" : "Invalid date format"},400
        existed_product = Product.query.filter_by(name = data['name']).first()
        if existed_product is not None:
            return {"message" : "Product already exist"},401
        if data['unit'] not in ['Kg', 'Litre', 'Pocket']:
            return {"message" : "Invalid unit"}, 401
        if not data.get('name'):
            return {"message" : "Name required"} , 400
        if not data.get('category'):
            return {"message" : "Category required"} , 400
        if not data.get('stock'):
            return {"message" : "Stock required"} , 400
        if not data.get('price'):
            return {"message" : "Price requried"} , 400
        product = Product(
            name=data['name'],
            category=data['category'],
            unit=data['unit'],
            stock=data['stock'],
            price=data['price'],
            expiry_date=expiry_date,
            owner=manager.manager_id
        )
        db.session.add(product)
        db.session.commit()
        return {
            'id': product.id,
            'owner': product.owner,
            'name': product.name,
            'category': product.category,
            'unit': product.unit,
            'stock': product.stock,
            'price': product.price,
            'expiry_date': product.expiry_date.isoformat()
        }, 201

    def put(self, product_id):
        # Check if the manager is authenticated
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        manager = Manager.query.filter_by(manager_email=email).first()
        if not manager:
            return {"message": "Manager Email not found"}, 401

        if not passhash.verify(password, manager.password):
            return {"message": "Authentication Failed"}, 401

        product = Product.query.get(product_id)
        if product:
            # Update product attributes with values from the JSON
            if 'name' in data:
                product.name = data['name']
            if 'category' in data:
                product.category = data['category']
            if 'unit' in data:
                if data['unit'] in ['Kg', 'Litre', 'Pocket']:
                    product.unit = data['unit']
                else:
                    return {"message": "Invalid unit"}, 400
            if 'stock' in data:
                product.stock = data['stock']
            if 'price' in data:
                product.price = data['price']
            if 'expiry_date' in data:
                expiry_date_str = data['expiry_date']
                try:
                    expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d').date()
                    product.expiry_date = expiry_date
                except ValueError:
                    return {"message": "Invalid date format"}, 400

            db.session.commit()
            return {
                'id': product.id,
                'owner': product.owner,
                'name': product.name,
                'category': product.category,
                'unit': product.unit,
                'stock': product.stock,
                'price': product.price,
                'expiry_date': product.expiry_date.isoformat()
            }, 200
        return {"message": "Product not found"}, 404

    def delete(self, product_id):
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        manager = Manager.query.filter_by(manager_email=email).first()
        if not manager:
            return {"message": "Manager Email not found"}, 401

        if not passhash.verify(password , manager.password):
            return {"message": "Authentication Failed"}, 401

        product = Product.query.get(product_id)
        if product:
            db.session.delete(product)
            db.session.commit()
            return {"message": "Product deleted"}, 200
        return {"message": "Product not found"}, 404
class ProductDetail(Resource):
    def get(self):
        products = Product.query.all()
        serialized_products = []

        for product in products:
            product_data = {
                'id': product.id,
                'owner': product.owner,
                'name': product.name,
                'category': product.category,
                'unit': product.unit,
                'stock': product.stock,
                'price': product.price,
                'expiry_date': product.expiry_date.strftime('%Y-%m-%d')  # Format date as 'YYYY-MM-DD'
            }
            serialized_products.append(product_data)

        return serialized_products, 200

