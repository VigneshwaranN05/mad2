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
        elif request.method == "POST":
            product_id , count = request.form['product'], request.form['count']
            product = Product.query.filter_by(id = product_id).first()

            cart = json.loads(session['cart'])
            if product_id in cart:
                
                try :
                    current = int(count) + int(current[product_id])
                except :
                    current = {}
                    current[product_id] = 0
                finally :
                    current = int(count) + int(current[product_id])
                if current <= int(product.stock):
                    cart[product_id] = str(int(current))
                else:
                    session['message'] = "Out of stock"
                    session['message_color'] = 'orangered'
                    return redirect('/')
            else:
                current = int(count)
                if current <= int(product.stock):
                    cart[product_id] = count
            
            session['cart'] = json.dumps(cart)
            session['message'] = "Producted Added to cart"
            session['message_color'] = 'green'
            return redirect('/')
    return render_template('home.html',today=today,products=products)
    
@controllers_bp.route('/category' , methods=['GET'])
def category():
    unique_categories = db.session.query(Product.category).distinct().all()
    unique_categories = [category[0] for category in unique_categories]
    products_by_category = {}
    for category in unique_categories:
        products = Product.query.filter_by(category=category).first()
        products_by_category[category] = products.id
    if current_user.is_authenticated:
        return render_template("category.html", products_by_category = products_by_category) 
    else :
        return render_template("category.html", products_by_category=products_by_category)

@controllers_bp.route("/category_need/<category_need>", methods=['GET','POST'])
@login_required
def category_need(category_need):
    unique_categories = db.session.query(Product.category).distinct().order_by(Product.category).all()
    unique_categories =  [category[0] for category in unique_categories]
    product_need = Product.query.filter_by(category=category_need).all()
    today = date.today()
    if current_user.is_authenticated:
        if request.method == 'GET':
            message = session.pop('message',None)
            message_color = session.pop('message_color', None)
            return render_template('category_need.html',today=today,unique_categories= unique_categories , category_need=category_need , product_need = product_need , message = message , message_color = message_color)
        else:
            product_id , count = request.form['product'], request.form['count']
            product = Product.query.filter_by(id = product_id).first()

            cart = json.loads(session['cart'])
            if product_id in cart:
                
                try :
                    current = int(count) + int(current[product_id])
                except :
                    current = {}
                    current[product_id] = 0
                finally :
                    current = int(count) + int(current[product_id])
                if current <= int(product.stock):
                    cart[product_id] = str(int(current))
                else:
                    session['message'] = "Out of stock"
                    session['message_color'] = 'orangered'
                    return redirect(url_for('controllers.category_need',category_need=category_need))
            else:
                current = int(count)
                if current <= int(product.stock):
                    cart[product_id] = count
            
            session['cart'] = json.dumps(cart)
            session['message'] = "Producted Added to cart"
            session['message_color'] = 'green'
            return redirect(url_for('controllers.category_need', category_need = category_need))
    else:
        session['message'] = "Login to continue"
        session['message_color'] = 'green'
        return redirect('/login')

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

            elif request_type == "remove_product":
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

@controllers_bp.route("/delete_item/<product_id>",methods=['GET','POST'])
@login_required
def delete_item(product_id):
    if current_user.is_authenticated and current_user.role == "Manager":
        manager = User.query.filter_by(email=current_user.email).first()
        if manager is not None and manager.role == "Manager" :
            if request.method == "POST" and manager.approved:
                product = Product.query.filter_by(id = product_id).first()
                db.session.delete(product)
                db.session.commit()
                return redirect("/store")
            else:
                return redirect("/store")
    return redirect("/")

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
                name = request.form["name"]
                category = request.form.get("category", None)
                unit = request.form.get("unit", None)
                stock = request.form.get("stock", None)
                price = request.form.get("price", None)
                date_str = request.form.get('date' , None)
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
                img = request.files.get("img")
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
            managers_products= Product.query.filter(Product.owner_id == current_user.id).with_entities(Product.id , Product.name).all()
            return render_template('new_request.html', products = managers_products)
        elif request.method == "POST":
            request_type = request.form.get('request-select')
            request_message = request.form.get('request-message')
            if request_type not in ['new_category' , 'remove_product']:
                session['message'] = f"Wrong request type {request_type}"
                session['message_color'] = 'orangered'
            elif request_type == "new_category":
                request_value = request.form.get('category-name')
            elif request_type == "remove_product":
                request_value = request.form.get('product-select')

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
        return render_template("cart.html" , user_cart = user_cart)

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

@controllers_bp.route('/analytics',methods=['GET'])

def analytics():
    if current_user.is_authenticated and current_user.role == "Manager":
        manager = User.query.filter_by(email=session['email']).first()
        purchases = Purchases.query.filter_by(owner=manager.id)

        data = {}
        product_counts = {}
        category_revenue = {}
        daily_revenue = {}
        end_date = datetime.today()
        start_date = end_date - timedelta(days=10)

        # Create a list of dates within the time frame
        date_range = [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)]

        # Initialize the data dictionary with zeros for all dates in the range
        for date in date_range:
            data[date.date()] = 0
            daily_revenue[date.date()] = 0

        # Populate the data dictionary with actual purchase data
        for purchase in purchases:
            purchase_date = purchase.date_added
            
            if purchase_date >= start_date.date() :
                product_name = purchase.product
                category = Product.query.filter_by(name=product_name).first().category
                if purchase_date in data:
                    data[purchase_date] += purchase.count
            
                if product_name in product_counts:
                    product_counts[product_name] += purchase.count
                else:
                    product_counts[product_name] = purchase.count 
                if category not in category_revenue:
                    category_revenue[category] = 0
                category_revenue[category] += purchase.count * purchase.price
                daily_revenue[purchase_date] += purchase.count * purchase.price
        
        product_names = list(product_counts.keys())
        product_sold_counts = list(product_counts.values())

        df = pd.DataFrame(list(data.items()), columns=['date', 'count'])
        df['date'] = pd.to_datetime(df['date'])

        df = df.sort_values(by='date')
        plt.figure(figsize=(8, 6))
        plt.plot(df['date'], df['count'], marker='o')
        plt.xlabel('Date')
        plt.ylabel("Number of Products Sold")
        plt.title("Number of products sold over 10 days")
        plt.savefig('./static/' + str(manager.id) + '1.png', format='png')
        
        plt.figure(figsize=(8,6))
        plt.pie(product_sold_counts, labels=product_names , autopct='%1.1f%%',startangle=140 )
        plt.title("Percentage of Products Sold Over 10 days")
        plt.savefig('./static/'+str(manager.id) + '2.png', format='png')

        df2 = pd.DataFrame(list(category_revenue.items()) , columns = ['Category', 'Revenue'])
        plt.figure(figsize=(10,6))
        plt.bar(df2['Category'] , df2['Revenue'] , color='skyblue')
        plt.xlabel("Categories")
        plt.ylabel('Revenue')
        plt.title('Revenue by Category for 10 days')
        plt.xticks(rotation=0, ha='right')
        plt.savefig('./static/'+str(manager.id) + '3.png', format='png')

        df3 = pd.DataFrame(list(daily_revenue.items()), columns=['date', 'revenue'])
        df3['date'] = pd.to_datetime(df3['date'])
        df3 = df3.sort_values(by='date')
        plt.figure(figsize=(10, 6))
        plt.bar(df3['date'], df3['revenue'], color='green')
        plt.xlabel('Date')
        plt.ylabel('Daily Revenue')
        plt.title('Daily Revenue over the last 10 days')
        plt.xticks(rotation=0, ha='right')
        plt.savefig('./static/' + str(manager.id) + '4.png', format='png')

        return render_template('analytics.html', username=session['username'], ismanager=session['manager'], signed=True, id=manager.manager_id)
    else:
        session['message'] = 'Login to Continue'
        session['message_color'] = 'green'
        return redirect('/login')
