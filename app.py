from flask import Flask
from applications.database import db
from applications.models import User
from flask_restful import Api
from api.product_resource import ProductResource, ProductDetail
from flask_login import LoginManager
from applications.controllers import controllers_bp
from passlib.hash import pbkdf2_sha256 as passhash

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = "faklfkjiii98miepqFPU$90!nbQoioi&"

    db.init_app(app)

    login_manager = LoginManager(app)
    login_manager.login_view = 'controllers.user_login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.register_blueprint(controllers_bp)

    return app

def create_admin_manager():
    admin_manager = User.query.filter_by(email="admin@gmail.com").first()
    if not admin_manager:
        password_hased = passhash.hash('admin')
        new_admin_manager = User(name='admin' , email='admin@gmail.com', password=password_hased, role="Admin"
                                 ,approved = True)

        db.session.add(new_admin_manager)
        db.session.commit()


from applications.controllers import *

if __name__ == "__main__":
    app = create_app()
    api = Api(app)
    api.add_resource(ProductResource, '/api/product/<int:product_id>' , '/api/product')
    api.add_resource(ProductDetail , '/api/allproducts' )

    with app.app_context():
        db.create_all()
        create_admin_manager()
    
    app.run(host='0.0.0.0' , debug=True)
