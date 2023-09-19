from flask import render_template,url_for,request, session, redirect
from flask import current_app as app
from sqlalchemy import or_
from applications.database import db
from applications.models import User, Manager , Product,Purchases
from passlib.hash import pbkdf2_sha256 as passhash
import json
import pandas as pd
from datetime import timedelta , datetime , date
import matplotlib.pyplot as plt


@app.route('/', methods=['GET','POST'])
def home():
    products = Product.query.order_by(Product.id.desc()).all()
    today = date.today()
    if "email" in session:
        if request.method == "GET":
            message = session.pop('message',None)
            message_color = session.pop('message_color', None)
            return render_template('home.html',today=today,products=products , message = message , message_color = message_color , signed = True , username=session['username'], ismanager=session['manager'])
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
                    return redirect(url_for('home'))
            else:
                current = int(count)
                if current <= int(product.stock):
                    cart[product_id] = count
            
            session['cart'] = json.dumps(cart)
            session['message'] = "Producted Added to cart"
            session['message_color'] = 'green'
            return redirect(url_for('home'))
    return render_template('home.html',today=today,products=products , singed=False)
    
@app.route('/category')
def category():
    unique_categories = db.session.query(Product.category).distinct().all()
    unique_categories = [category[0] for category in unique_categories]
    products_by_category = {}
    for category in unique_categories:
        products = Product.query.filter_by(category=category).first()
        products_by_category[category] = products.id
    if "email" in session:
        return render_template("category.html", products_by_category = products_by_category , signed=True, username=session['username'], ismanager=session['manager'])
    else :
        return render_template("category.html", signed=False , products_by_category=products_by_category)

@app.route("/category_need/<category_need>", methods=['GET','POST'])
def category_need(category_need):
    unique_categories = db.session.query(Product.category).distinct().order_by(Product.category).all()
    unique_categories =  [category[0] for category in unique_categories]
    product_need = Product.query.filter_by(category=category_need).all()
    today = date.today()
    if 'email' in session:
        if request.method == 'GET':
            message = session.pop('message',None)
            message_color = session.pop('message_color', None)
            return render_template('category_need.html',today=today,unique_categories= unique_categories , category_need=category_need , ismanager=session['manager'], signed=True , username = session['username'] , product_need = product_need , message = message , message_color = message_color)
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
                    return redirect(url_for('category_need',category_need=category_need))
            else:
                current = int(count)
                if current <= int(product.stock):
                    cart[product_id] = count
            
            session['cart'] = json.dumps(cart)
            session['message'] = "Producted Added to cart"
            session['message_color'] = 'green'
            return redirect(url_for('category_need', category_need = category_need))
    else:
        session['message'] = "Login to continue"
        session['message_color'] = 'green'
        return redirect('/login')

@app.route("/store")
def store():
    if "email" in session and session['manager']:
        today = date.today()
        manager = Manager.query.filter_by(manager_email = session['email']).first()
        manager_id = manager.manager_id
        products = Product.query.filter_by(owner = manager_id)
        message = session.pop('message',None)
        message_color = session.pop('message_color', None)
        return render_template("store.html",today=today, products=products, message=message , message_color=message_color , signed=True, username=session['username'],ismanager=session['manager'])
    else:
        session['message'] = "Login to continue"
        session['message_color'] = 'green'
        return redirect('/login')

@app.route("/delete_item/<product_id>",methods=['GET','POST'])
def delete_item(product_id):
    if "email" in session and session['manager']:
        manager = Manager.query.filter_by(manager_email=session["email"]).first()
        if manager is not None:
            if request.method == "POST":
                product = Product.query.filter_by(id = product_id).first()
                db.session.delete(product)
                db.session.commit()
                return redirect("/store")
            else:
                return redirect("/store")
    return redirect("/")

@app.route("/edit_item/<product_id>", methods=["GET", "POST"])
def edit_product(product_id):
    if "email" in session and session['manager']:
        manager = Manager.query.filter_by(manager_email=session["email"]).first()
        if manager is not None:
            product = Product.query.filter_by(id=product_id).first()
            if request.method == "GET":
                message = session.pop('message',None)
                message_color = session.pop('message_color', None)
                return render_template('edit_item.html',message = message  , message_color= message_color , signed=True, username=session['username'], ismanager=session['manager'])
            elif request.method == "POST":
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

@app.route("/add_item", methods=['GET', 'POST'])
def add_item():
    if "email" in session and session['manager']:
        manager = Manager.query.filter_by(manager_email=session['email']).first()
        if request.method == 'GET':
            if session['manager']:
                message = session.pop('message', None)
                message_color = session.pop('message_color', None)
                return render_template('add_item.html',message = message  , message_color= message_color , signed=True, username=session['username'], ismanager=session['manager'])
            else:
                return redirect(url_for('home'))
        elif request.method == 'POST' and session['manager']:
            given_name = request.form["name"].capitalize()  # Capitalize the name
            category = request.form["category"].capitalize()  # Capitalize the category
            stock = request.form["stock"]
            unit = request.form['unit'].capitalize()  # Capitalize the unit
            if unit not in ['Kg','Litre','Pocket']:
                session['message'] = 'Invalid Unit'
                session['message_color'] = 'orangered'
                return redirect('/add_item')
            price = request.form["price"]
            img = request.files["img"]

            date_str = request.form['date']
            date_obj = datetime.strptime(date_str , '%Y-%m-%d')
            today = date.today()
            if date_obj <= datetime(today.year , today.month, today.day):
                session['message'] = "Invalid Expiry Date"
                session['message_color'] = "orangered"
                return redirect(url_for('/add_item'))
            #Check whether the name is already been used by the owner
            present_product = Product.query.filter_by(owner=manager.manager_id , name = given_name).first()
            
            if present_product is None:
                product = Product(name=given_name, category=category, unit=unit, stock=stock, owner=manager.manager_id, price=price , expiry_date=date_obj)
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

@app.route('/manager_signup', methods=['GET' , 'POST'])
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
        
        manager_exist= Manager.query.filter_by(manager_email = manager_email).first()
        if manager_exist is None:
            new_manager = Manager(manager_name=manager_name,manager_email=manager_email,password=password)
            db.session.add(new_manager)
            db.session.commit()

            session['message'] = "Acccount created successfully!!"
            session['message_color'] = 'green'
            return redirect(url_for('user_login'))
        else:
            session['message'] = "Eamil already exist"
            session['message_color']  = 'orangered'
            return redirect(url_for('manager_signup'))

@app.route('/signup', methods=['GET','POST'])
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
            new_user = User(username=username,email=email,password=password)
            db.session.add(new_user)
            db.session.commit()
            
            session['message'] = "Account cerated successfully!!"
            session['message_color'] = 'green'
            return redirect(url_for('user_login'))
        else:
            session['message'] = "Eamil already exist"
            session['message_color'] = 'orangered'
            return redirect(url_for('signup'))

@app.route('/manager_login',methods=['GET','POST'])
def manager_login():
    if request.method == 'GET':
        message = session.pop('message',None)
        message_color = session.pop('message_color',None)
        return render_template('manager_login.html',message=message , message_color=message_color)
    
    elif request.method == 'POST':
        email = request.form['manager-email']
        password = request.form['manager-password']
        manager = Manager.query.filter_by(manager_email = email).first()
        if manager is None:
            session['message'] = "Invalid Email"
            session['message_color'] = 'orangered'
            return redirect(url_for('manager_login'))
        if not passhash.verify(password , manager.password):
            session['message'] = "Wrong Password"
            session['message_color'] = 'orangered'
            return redirect(url_for('manager_login'))
        session['email'] = email
        session['username'] = manager.manager_name
        session['manager'] = True
        
        return redirect("/")

@app.route('/login',methods=['GET','POST'])
def user_login():
    if request.method == 'GET':
        message = session.pop('message',None)
        message_color = session.pop('message_color',None)
        return render_template('login.html',message=message,message_color=message_color)
    
    elif request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email= email).first()
        if user is None:
            session['message'] = "Email not found"
            session['message_color'] = 'orangered'
            return redirect(url_for('user_login'))
        if not passhash.verify(password,user.password) :
            session['message'] = "Wrong Password"
            session['message_color'] = 'orangered'
            return redirect(url_for('user_login'))
        session["username"] = user.username 
        session['email'] = email
        session['manager'] = False
        session['cart'] = json.dumps(dict())
        return redirect('/')

@app.route('/logout')
def logout():
    if "email" in session:
        session.pop("email")
        session.pop("username")
        session['manager'] = False
        session['cart'] = json.dumps(dict())
    return redirect('/')

@app.route("/cart", methods = ["GET", "POST"])
def cart():
    if "email" in session and not session['manager']:
        cart = json.loads(session["cart"])
        user = User.query.filter_by(email=session["email"]).first()
        products = [[Product.query.filter_by(id = product_id).first(), cart[product_id]] for product_id in cart.keys()]
        total = sum([int(Product.query.filter_by(id = product_id).first().price) * int(cart[product_id]) for product_id in cart.keys()])
        if request.method == "GET":
            message = session.pop('message',None)
            message_color = session.pop('message_color',None)
            return render_template("cart.html", message=message , message_color = message_color,  products = products, total = total , ismanager=session['manager'],signed=True, username=user.username)
        else:
            if "remove" in request.form:
                cart.pop(request.form["remove"])
                session["cart"] = json.dumps(cart)
                return redirect("/cart")
            else:
                for product, count in products:
                    if product.stock-int(count) >= 0 :
                        product.stock -= int(count)
                        print(product.price)
                        purchase = Purchases(product=product.name, owner=product.owner, customer=user.id, count=count , price=product.price)
                        db.session.add(purchase)
                        db.session.commit()
                    else:
                        session['message'] = "Product out of stock"
                        session['message_color'] = "orangered"
                        return redirect('/cart')
                session["cart"] = json.dumps(dict())
                return redirect("/")
    else:
        session['message'] = 'Login to continue'
        session['message_color'] = 'green'
        return redirect("/login")
    
@app.route('/search',methods=['GET','POST'])
def search():
    if "email" in session and request.method == 'POST':
        query = request.form['query']
        searched_products = Product.query.filter(or_(Product.name.ilike(f"%{query}%"))).all()
        return render_template('search.html',products=searched_products , username=session['username'], ismanager = session['manager'],signed = True)
    elif request.method == 'GET' and "email" in session :
        return render_template('home.html' , username=session['username'] , ismanager = session['manager'] , singed = True)
    else:
        session['message'] = "Login to continue"
        session['message_color'] = "green"
        return redirect('/login')

@app.route('/history',methods=["GET"])
def history():
    if "email" in session and not session['manager']:
        user = User.query.filter_by(email=session['email']).first()
        history = Purchases.query.filter_by(customer = user.id).all()
        return render_template('history.html',username=session['username'],signed = True, ismanager=session['manager'],history = history)
    else:
        session['message'] = "Login to continue"
        session['message_color'] = "green"
        return redirect('/login')

@app.route('/analytics',methods=['GET'])

def analytics():
    if "email" in session and session['manager']:
        manager = Manager.query.filter_by(manager_email=session['email']).first()
        purchases = Purchases.query.filter_by(owner=manager.manager_id)

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
        plt.savefig('./static/' + str(manager.manager_id) + '1.png', format='png')
        
        plt.figure(figsize=(8,6))
        plt.pie(product_sold_counts, labels=product_names , autopct='%1.1f%%',startangle=140 )
        plt.title("Percentage of Products Sold Over 10 days")
        plt.savefig('./static/'+str(manager.manager_id) + '2.png', format='png')

        df2 = pd.DataFrame(list(category_revenue.items()) , columns = ['Category', 'Revenue'])
        plt.figure(figsize=(10,6))
        plt.bar(df2['Category'] , df2['Revenue'] , color='skyblue')
        plt.xlabel("Categories")
        plt.ylabel('Revenue')
        plt.title('Revenue by Category for 10 days')
        plt.xticks(rotation=0, ha='right')
        plt.savefig('./static/'+str(manager.manager_id) + '3.png', format='png')

        df3 = pd.DataFrame(list(daily_revenue.items()), columns=['date', 'revenue'])
        df3['date'] = pd.to_datetime(df3['date'])
        df3 = df3.sort_values(by='date')
        plt.figure(figsize=(10, 6))
        plt.bar(df3['date'], df3['revenue'], color='green')
        plt.xlabel('Date')
        plt.ylabel('Daily Revenue')
        plt.title('Daily Revenue over the last 10 days')
        plt.xticks(rotation=0, ha='right')
        plt.savefig('./static/' + str(manager.manager_id) + '4.png', format='png')

        return render_template('analytics.html', username=session['username'], ismanager=session['manager'], signed=True, id=manager.manager_id)
    else:
        session['message'] = 'Login to Continue'
        session['message_color'] = 'green'
        return redirect('/login')
