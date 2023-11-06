from flask import Flask
from applications.database import db
from applications.models import Manager
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

def create_admin_manager():
    admin_manager = Manager.query.filter_by(manager_email="admin@gmail.com").first()
    if not admin_manager:
        new_admin_manager = Manager(manager_name='admin' , manager_email='admin@gmail.com', password='admin', is_admin=True)

        db.session.add(new_admin_manager)
        db.session.commit()


app = create_app()
api = Api(app)
api.add_resource(ProductResource, '/api/product/<int:product_id>' , '/api/product')
api.add_resource(ProductDetail , '/api/allproducts' )
from applications.controllers import *

if __name__ == "__main__":
    db.create_all()
    create_admin_manager()
    app.run(debug=True)
