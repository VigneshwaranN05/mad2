from flask import Flask
from applications.database import db
from flask_restful import Api

from api.product_resource import ProductResource, ProductDetail
def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = "faklfkjiii98miepqFPU$90!nbQoioi&"

    db.init_app(app)

    app.app_context().push()

    return app

app = create_app()
api = Api(app)
api.add_resource(ProductResource, '/api/product/<int:product_id>' , '/api/product')
api.add_resource(ProductDetail , '/api/allproducts' )
from applications.controllers import *

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
