from flask import Blueprint, render_template,url_for,request, session, redirect
from sqlalchemy import or_
from applications.database import db
from applications.models import *
from passlib.hash import pbkdf2_sha256 as passhash
import json
import pandas as pd
from flask import jsonify
from datetime import timedelta , datetime , date
import matplotlib.pyplot as plt
from flask_login import login_user, login_required, logout_user , current_user

controllers_bp = Blueprint('controllers' , __name__)

@controllers_bp.route('/', methods=['GET','POST'])
def home():
    products = Product.query.order_by(Product.id.desc()).all()
    today = date.today()
    
    if current_user.is_authenticated:
        if request.method == "GET":
            message = session.pop('message',None)
            message_color = session.pop('message_color', None)
            return render_template('home.html',today=today,products=products , 
                                   message = message , message_color = message_color )
    return render_template('home.html',today=today,products=products)
    
@controllers_bp.route('/category' , methods=['GET'])
def category():
    if request.method == 'GET':
        categories = Categories.query.all()
        return render_template('category.html', categories = categories)

@controllers_bp.route("/category_need/<category_need>", methods=['GET','POST'])
@login_required
def category_need(category_need):
    if current_user.is_authenticated:
        categories = Categories.query.all()
        products_need = Product.query.filter_by(category=int(category_need)).all()
        today = date.today()
        if request.method == 'GET':
            message = session.pop('message',None)
            message_color = session.pop('message_color', None)
            return render_template('category_need.html',today=today,categories= categories 
                                   , category_need=int(category_need) , products = products_need , 
                                   message = message , message_color = message_color)
    else:
        session['message'] = "Login to continue"
        session['message_color'] = 'green'
        return redirect('/login')

#id -> product_id
@controllers_bp.route('/add_to_cart/<int:product_id>' , methods=['POST'])
@login_required
def add_to_cart(product_id):
    if current_user.is_authenticated and current_user.role == "User":
        if request.method == 'POST':
            try: 
                product_requested = Product.query.get(product_id)
                quantity_requested = int(request.form.get('count'))
                user_id = current_user.id
                if quantity_requested <= product_requested.stock:
                    new_cart_entry = Cart(
                            user_id = user_id,
                            product_id = product_requested.id,
                            quantity = quantity_requested,
                            price = product_requested.price,
                            date = datetime.now()
                    )
                    
                    db.session.add(new_cart_entry)
                    db.session.commit()
                    session['message'] = f"Product {product_requested.name} added to cart"
                    session['message_color'] = '#6495ed'
                    return redirect(request.referrer or '/')

            except Exception as e:
                session['message'] = f"Unable {e}"
                session['message_color'] = 'red'
                return redirect(request.referrer or '/')

            return redirect(request.referrer or '/')
        else:
            return redirect(request.referrer or '/')

#getting the request id from GET method
@controllers_bp.route('/approve/<int:id>')
@login_required
def approve(id):
    if current_user.is_authenticated and current_user.role == "Admin":
        try:
            request_made = Request.query.get(id)
        except Exception as e:
            session['message'] = f"Error finding request {id}: {str(e)}"
            session['message_color'] = 'orangered'
            return redirect('/')

        if request_made is not None:
            request_type = request_made.request_type
            
            if request_type not in ["new_manager" , "new_category" , "remove_item"]:
                session['message'] = f"Wrong request_type {request_type}"
                session['message_color'] = "red"
                return redirect('/request')
            if request_type == "new_manager":
                try:
                    manager_id = int(request_made.request_value)
                    managerToUpdate = User.query.get(manager_id)
                    managerToUpdate.approved = True
                    request_made.took_action = True
                    db.session.commit()
                    session['message'] = f"Updated manager {manager_id}"
                    session['message_color'] = "green"
                    return redirect('/requests')
                except (ValueError , TypeError):
                    session['message'] = f'Error getting the id f{request_made.request_value}'
                    session['message_color'] = 'orangered'
                except Exception as e:
                    session['message'] = f'Error finding manager {manager_id}: {str(e)}'
                    session['message_color'] = 'orangered'
                    return redirect('/')


            elif request_type == "new_category":
                try:
                    category_name = request_made.request_value
                    new_category = Categories(name = category_name)
                    db.session.add(new_category)
                    request_made.took_action = True
                    db.session.commit()
                    session['message'] = f'New Category {category_name} created'
                    session['message_color'] = 'green'
                    return redirect('/requests')
                except Exception as e:
                    session['message'] = f'Error creating a category {category_name}: {str(e)}'
                    session['message_color'] = 'orangered'
                    return redirect('/requests')

            elif request_type == "remove_item":
                try:
                    product_id = int(request_made.request_value)
                    productToRemove = Product.query.filter(Product.id == product_id).first()

                    if productToRemove:
                        db.session.delete(productToRemove)
                        request_made.took_action = True
                        db.session.commit()
                        session['message'] = f"Product {product_id} deleted successfully."
                        session['message_color'] = "green"
                        return redirect('/requests')
                    else:
                        session['message'] = f"Product with id {product_id} not found."
                        session['message_color'] = 'orangered'
                        return redirect('/requests')

                except (ValueError , TypeError):
                    session['message'] = f'Error getting the Product id {request_made.request_value}'
                    session['message_color'] = 'orangered'
                    return redirect('/requests')
                except Exception as e:
                    session['message'] = f"Error deleting Product {product_id}: {str(e)}"
                    session['message_color'] = 'orangered'
                    return redirect('/requests')
        else:
            session['message'] = f"Request with id {id} not found."
            session['message_color'] = 'orangered'
            return redirect('/')
    else:
        session['message'] = "Login to Continue"
        session['message_color'] = 'orange'
        return redirect('/login')

@login_required
@controllers_bp.route('/decline/<int:id>')
def decline(id):
    if current_user.is_authenticated and current_user.role == "Admin":
        if request.method == 'GET' and id is not None:
            requested = Request.query.get(id)
            decline_user = User.query.get(requested.request_by)
            if not decline_user:
                session['message'] = f'Manager id {requested.request_by} not Found'
                session['messages_color'] = 'orangered'
                return redirect('/requests')
            else:
                decline_user.approved = 0
                requested.took_action = True 
                db.session.commit()
                session['message'] = f'Updated Manager with id {requested.request_by}'
                session['message_color'] = 'green'
                return redirect('/requests')
    else:
        session['message'] = "Login to Continue"
        session['message_color'] = 'orange'
        return redirect('/login')
@controllers_bp.route('/requests')
@login_required
def requests():
    if current_user.is_authenticated and current_user.role == "Admin":
        if request.method == "GET":
            message = session.pop('message',None)
            message_color = session.pop('message_color', None)
            admin_request = Request.query.filter_by(took_action= False).all()
            return render_template('requests.html' , admin_request = admin_request,
                                   message = message , message_color = message_color) 
    else:
        session['message'] = "Login to Continue"
        session['message_color'] = 'orange'
        return redirect('/login')
@controllers_bp.route("/store")
@login_required
def store():
    if current_user.is_authenticated: 
        today = date.today()
        manager = User.query.filter_by(email = current_user.email).first()
        if manager is not None and manager.role != "Manager": 
            session['message'] = "Login to continue"
            session["message_color"]  = "orange"
            return redirect('/login')
        else:
            request_state = Request.query.filter_by(request_by = manager.id).first()
        if  not current_user.approved :
            if not request_state.took_action:
                session['message'] = "Not Yet Approved by Admin"
                session['message_color'] = "orangered"
                return redirect('/')
            else:
                session['message'] = "Request for Creating a Store is Declined"
                session["message_color"] = 'orangered'
                return redirect('/')
        manager_id = manager.id
        products = Product.query.filter_by(owner_id = manager_id)
        message = session.pop('message',None)
        message_color = session.pop('message_color', None)
        return render_template("store.html",today=today, products=products, message=message , 
                               message_color=message_color) 
    else:
        session['message'] = "Login to continue"
        session['message_color'] = 'green'
        return redirect('/login')

@controllers_bp.route("/edit_item/<product_id>", methods=["GET", "POST"])
@login_required
def edit_product(product_id):
    if current_user.is_authenticated and current_user.role == "Manager":
        manager = User.query.filter_by(email=current_user.email).first()
        if manager is not None and manager.approved:
            product = Product.query.filter_by(id=product_id).first()
            categories = Categories.query.all()
            if request.method == "GET": 
                message = session.pop('message',None)
                message_color = session.pop('message_color', None)
                return render_template('edit_item.html',message = message  , message_color= message_color,
                                       product = product , categories = categories)
            elif request.method == "POST" and manager.approved:
                name = request.form["product-name"]
                category = request.form.get("product-category", None)
                unit = request.form.get("unit", None)
                stock = request.form.get("stock", None)
                price = request.form.get("price", None)
                date_str = request.form.get('expire-date' , None)
                if name:
                    name = name.capitalize()
                    product.name = name
                if category:
                    category = category.capitalize()
                    product.category = category
                if unit:
                    unit = unit.capitalize()
                    product.unit = unit
                if stock:
                    stock = stock.capitalize()
                    product.stock = stock
                if price:
                    price = price.capitalize()
                    product.price = price
                if date_str:
                    date_obj = datetime.strptime(date_str , '%Y-%m-%d')
                    today = date.today()
                    if date_obj <= datetime(today.year , today.month, today.day):
                        session['message'] = "Invalid Expiry Date"
                        session['message_color'] = "orangered"
                        return redirect('/edit_item/{{product_id}}')
                    else:
                        product.expiry_date = date_obj

                db.session.commit()

                # Handle image upload separately
                img = request.files["file"]
                if img:
                    img.save("./static/products/" + str(product.id) + ".png")

                return redirect("/store")
    return redirect("/")

@controllers_bp.route("/add_item", methods=['GET', 'POST'])
@login_required
def add_item():
    if current_user.is_authenticated and current_user.role == "Manager":
        manager = User.query.filter_by(email=current_user.email).first()
        if request.method == 'GET' and manager.approved:
            categories = Categories.query.all()
            message = session.pop('message', None)
            message_color = session.pop('message_color', None)
            return render_template('add_item.html', categories = categories,
                                   message = message  , message_color= message_color) 
        elif request.method == 'POST' and manager.approved: 
            given_name = request.form["product-name"].capitalize()  # Capitalize the name
            category = request.form["product-category"].capitalize()  # Capitalize the category
            stock = request.form["stock"]
            unit = request.form['unit'].capitalize()  # Capitalize the unit
            if unit not in ['Kg','Liter','Pocket']:
                session['message'] = 'Invalid Unit'
                session['message_color'] = 'orangered'
                return redirect('/add_item')
            price = request.form["price"]
            img = request.files["file"]

            date_str = request.form['expire-date']
            date_obj = datetime.strptime(date_str , '%Y-%m-%d')
            today = date.today()
            if date_obj <= datetime(today.year , today.month, today.day):
                session['message'] = "Invalid Expiry Date"
                session['message_color'] = "orangered"
                return redirect('/add_item')
            #Check whether the name is already been used by the owner
            present_product = Product.query.filter_by(owner_id=manager.id, name = given_name).first()
            
            if present_product is None:
                product = Product(owner_id = manager.id , name = given_name , stock=stock,
                                  category = category , unit = unit , price = price,
                                  expiry_date = date_obj)
                db.session.add(product)
                db.session.commit()
                img.save("./static/products/" + str(product.id) + ".png")
                return redirect("/store")
            else:
                session['message'] = "The Item already exist"
                session['message_color'] = "green"
                return redirect('/store')
        else:
            return redirect('/home')
    else:
        return redirect('/home')

@controllers_bp.route('/new_request',methods=['GET' ,'POST'])
def new_request():
    if current_user.is_authenticated and current_user.role == "Manager" and current_user.approved:
        if request.method == 'GET':
            select_args = request.args.get('request-select')
            input_args = request.args.get('request-input')
            if select_args not in ["new_category" , "remove_item"]:
                select_args = None

            message = session.pop('message',None)
            message_color = session.pop('message_color',None)
            managers_products= Product.query.filter(Product.owner_id == current_user.id).with_entities(Product.id , Product.name).all()
            return render_template('new_request.html', products = managers_products, select_args = select_args,
                                   input_args=input_args, message = message , message_color = message_color)
        elif request.method == "POST":
            request_type = request.form.get('request-select')
            request_message = request.form.get('request-message')
            request_value = None
            if request_type not in ['new_category' , 'remove_item']:
                session['message'] = f"Wrong request type {request_type}"
                session['message_color'] = 'orangered'
            elif request_type == "new_category":
                request_value = request.form.get('category-name')
            elif request_type == "remove_item":
                request_value = request.form.get('product-select')

            if request_value is not None:
                newRequest = Request(request_by = current_user.id , request_type = request_type,
                                 request_value = request_value , took_action = False, 
                                 request_message = request_message)
                db.session.add(newRequest)
                db.session.commit()
                session['message'] = "Request is sent to admin"
                session['message_color'] = "green"
            return redirect('/new_request')
    else:
        return redirect('/login')







@controllers_bp.route('/manager_signup', methods=['GET' , 'POST'])
def manager_signup():
    if request.method == "GET":
        message = session.pop('message',None)
        message_color = session.pop('message_color',None)
        return render_template('manager_signup.html',message=message , message_color = message_color)
    elif request.method == 'POST':
        manager_name = request.form['manager-name']
        manager_email = request.form['manager-email'] 
        password = request.form['manager-password']
        password = passhash.hash(password)
        
        manager_exist= User.query.filter_by(email = manager_email).first()
        if manager_exist is None:
            new_manager = User(name=manager_name,email=manager_email,password=password, role="Manager" , approved = 0)
            db.session.add(new_manager)
            db.session.commit()
            new_request = Request(request_by = new_manager.id ,request_type= "new_manager", took_action = False, request_message = "New Manager signed up" , request_value = new_manager.id )
            db.session.add(new_request)
            db.session.commit()
            session['message'] = "Acccount created successfully!!"
            session['message_color'] = 'green'
            return redirect('/login')
        else:
            session['message'] = "Eamil already exist"
            session['message_color']  = 'orangered'
            return redirect('/signup')

@controllers_bp.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'GET':
        message = session.pop('message',None)
        message_color = session.pop('message_color',None)
        return render_template('signup.html',message=message,message_color=message_color)
    elif request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password=request.form['password']
        password = passhash.hash(password)
        user_exist = User.query.filter_by(email=email).first()
        if user_exist is None:        
            new_user = User(name=username,email=email,password=password , role="User", approved = 1)
            db.session.add(new_user)
            db.session.commit()
            
            session['message'] = "Account cerated successfully!!"
            session['message_color'] = 'green'
            return redirect('/login')
        else:
            session['message'] = "Eamil already exist"
            session['message_color'] = 'orangered'
            return redirect('/signup')

@controllers_bp.route('/manager_login',methods=['POST'])
def manager_login():
    if request.method == 'POST':
        email = request.form['manager-email']
        password = request.form['manager-password']
        manager = User.query.filter_by(email = email).first()
        if manager is None or manager.role == "User":
            session['message'] = "Invalid Email"
            session['message_color'] = 'orangered'
            return redirect('/login')
        if not passhash.verify(password , manager.password):
            session['message'] = "Wrong Password"
            session['message_color'] = 'orangered'
            return redirect('/login')
        else : 
            session['message'] = "Logged In successfully"
            session['message_color'] = "Green"
            login_user(manager)
            return redirect("/")

@controllers_bp.route('/login',methods=['GET','POST'])
def user_login():
    if request.method == 'GET':
        message = session.pop('message',None)
        message_color = session.pop('message_color',None)
        return render_template('login.html',message=message,message_color=message_color)
    
    elif request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email= email).first()
        if user is None or user.role != "User":
            session['message'] = "User Email not found"
            session['message_color'] = 'orangered'
            return redirect('/login')
        elif not passhash.verify(password,user.password) :
            session['message'] = "Wrong Password"
            session['message_color'] = 'orangered'
            return redirect('/login')
        else:
            login_user(user)
            return redirect('/')

@controllers_bp.route('/logout')
@login_required 
def logout():
    logout_user()
    return redirect('/')

@controllers_bp.route("/cart", methods = ["GET", "POST"])
@login_required
def cart():
    if current_user.is_authenticated and current_user.role == "User":
        user_cart = Cart.query.filter_by(user_id = current_user.id).all()
        userCartByDate = {}
        for product in user_cart :
            cart_date = product.date
            if cart_date not in userCartByDate :
                userCartByDate[cart_date] = []
            userCartByDate[cart_date].append(product) 
        print(f"userCartByDate : {userCartByDate}")
        return render_template("cart.html" ,userCartByDate = userCartByDate)

@controllers_bp.route('/search',methods=['GET','POST'])
def search():
    if current_user.is_authenticated and request.method == 'POST':
        query = request.form['query']
        searched_products = Product.query.filter(or_(Product.name.ilike(f"%{query}%"))).all()
        return render_template('search.html',products=searched_products )
    elif request.method == 'GET' :
        return redirect('/')

@controllers_bp.route('/history',methods=["GET"])
@login_required
def history():
    if current_user.is_authenticated and current_user.role == "User": 
        user = User.query.filter_by(email=session['email']).first()
        history = Purchases.query.filter_by(customer = user.id).all()
        return render_template('history.html',username=session['username'],signed = True, ismanager=session['manager'],history = history)
    else:
        session['message'] = "Login to continue"
        session['message_color'] = "green"
        return redirect('/login')

