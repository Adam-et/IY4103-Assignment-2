from flask import Flask, render_template, redirect, request, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Database Objects
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    orders = db.relationship('Order', backref='user', lazy=True)
    cart_items = db.relationship('Cart', backref='user', lazy=True)

class Manga(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(500), nullable=True)
    author = db.Column(db.String(150), nullable=False)
    image = db.Column(db.String(300), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    orders = db.relationship('Order', backref='manga', lazy=True)
    cart_items = db.relationship('Cart', backref='manga', lazy=True)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('manga.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='pending')

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('manga.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

class Login(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)

# Helper functions
def is_logged_in():
    return 'user_id' in session

# Routing
@app.route("/")
def index():
    featured_manga = Manga.query.order_by(Manga.created_at.desc()).limit(4).all()
    return render_template("index.html", featured_manga=featured_manga, is_logged_in=is_logged_in())

@app.route("/base")
def base():
    return render_template("base.html", is_logged_in=is_logged_in())

@app.route("/about")
def about():
    return render_template("about.html", is_logged_in=is_logged_in())

@app.route("/cart")
def cart():
    if not is_logged_in():
        flash("Please login to view your cart", "warning")
        return redirect(url_for('login'))
    
    cart_items = Cart.query.filter_by(user_id=session['user_id']).all()
    total = 0
    cart_mangas = []
    
    for item in cart_items:
        manga = Manga.query.get(item.product_id)
        cart_mangas.append({
            'id': item.id,
            'manga_id': manga.id,
            'name': manga.name,
            'price': manga.price,
            'quantity': item.quantity,
            'subtotal': manga.price * item.quantity
        })
        total += manga.price * item.quantity
    
    return render_template("cart.html", cart_items=cart_mangas, total=total, is_logged_in=is_logged_in())

@app.route("/add_to_cart/<int:manga_id>", methods=["POST"])
def add_to_cart(manga_id):
    if not is_logged_in():
        flash("Please login to add items to your cart", "warning")
        return redirect(url_for('login'))
    
    quantity = int(request.form.get("quantity", 1))
    user_id = session['user_id']
    
    # Check if the item already exists in the cart
    existing_item = Cart.query.filter_by(user_id=user_id, product_id=manga_id).first()
    
    if existing_item:
        existing_item.quantity += quantity
    else:
        new_cart_item = Cart(user_id=user_id, product_id=manga_id, quantity=quantity)
        db.session.add(new_cart_item)
    
    db.session.commit()
    flash("Item added to cart successfully!", "success")
    return redirect(url_for('manga_detail', manga_id=manga_id))

@app.route("/remove_from_cart/<int:item_id>")
def remove_from_cart(item_id):
    if not is_logged_in():
        return redirect(url_for('login'))
    
    cart_item = Cart.query.get_or_404(item_id)
    
    # Check if the cart item belongs to the logged-in user
    if cart_item.user_id != session['user_id']:
        flash("Unauthorized action", "danger")
        return redirect(url_for('cart'))
    
    db.session.delete(cart_item)
    db.session.commit()
    flash("Item removed from cart", "success")
    return redirect(url_for('cart'))

@app.route("/update_cart", methods=["POST"])
def update_cart():
    if not is_logged_in():
        return redirect(url_for('login'))
    
    cart_items = Cart.query.filter_by(user_id=session['user_id']).all()
    
    for item in cart_items:
        quantity = request.form.get(f"quantity_{item.id}")
        if quantity:
            item.quantity = int(quantity)
    
    db.session.commit()
    flash("Cart updated successfully", "success")
    return redirect(url_for('cart'))

@app.route("/loggedin")
def loggedin():
    if not is_logged_in():
        return redirect(url_for('login'))
    return render_template("loggedin.html", is_logged_in=is_logged_in())

@app.route("/loggedout")
def loggedout():
    return render_template("loggedout.html", is_logged_in=is_logged_in())

@app.route("/manga_detail/<int:manga_id>")
def manga_detail(manga_id):
    manga = Manga.query.get_or_404(manga_id)
    return render_template("manga_detail.html", manga=manga, is_logged_in=is_logged_in())

@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    if not is_logged_in():
        flash("Please login to checkout", "warning")
        return redirect(url_for('login'))
    
    if request.method == "POST":
        cart_items = Cart.query.filter_by(user_id=session['user_id']).all()
        
        if not cart_items:
            flash("Your cart is empty", "warning")
            return redirect(url_for('cart'))
        
        # Create orders from cart items
        for item in cart_items:
            new_order = Order(
                user_id=session['user_id'],
                product_id=item.product_id,
                quantity=item.quantity,
                status='completed'
            )
            db.session.add(new_order)
            db.session.delete(item)  # Remove from cart
        
        db.session.commit()
        flash("Order placed successfully!", "success")
        return redirect(url_for('index'))
    
    cart_items = Cart.query.filter_by(user_id=session['user_id']).all()
    if not cart_items:
        flash("Your cart is empty", "warning")
        return redirect(url_for('cart'))
    
    total = 0
    checkout_items = []
    
    for item in cart_items:
        manga = Manga.query.get(item.product_id)
        checkout_items.append({
            'name': manga.name,
            'price': manga.price,
            'quantity': item.quantity,
            'subtotal': manga.price * item.quantity
        })
        total += manga.price * item.quantity
    
    return render_template("checkout.html", checkout_items=checkout_items, total=total, is_logged_in=is_logged_in())

@app.route("/register", methods=["GET", "POST"])
def register():
    if is_logged_in():
        return redirect(url_for('index'))
    
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        
        # Validation
        if not username or not email or not password or not confirm_password:
            flash("All fields are required", "danger")
            return redirect(url_for('register'))
        
        if password != confirm_password:
            flash("Passwords do not match", "danger")
            return redirect(url_for('register'))
        
        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            flash("Username already exists", "danger")
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash("Email already exists", "danger")
            return redirect(url_for('register'))
        
        # Create new user
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password)
        
        # Also create a login entry
        new_login = Login(username=username, password=hashed_password)
        
        db.session.add(new_user)
        db.session.add(new_login)
        db.session.commit()
        
        flash("Registration successful! Please login.", "success")
        return redirect(url_for('login'))
    
    return render_template("register.html", is_logged_in=is_logged_in())

@app.route("/manga")
def manga():
    all_manga = Manga.query.all()
    return render_template("manga.html", manga_list=all_manga, is_logged_in=is_logged_in())

@app.route("/create_manga", methods=["GET", "POST"])
def create_manga():
    if not is_logged_in():
        flash("Please login to add manga", "warning")
        return redirect(url_for('login'))
    
    if request.method == "POST":
        manga_name = request.form.get("manga_name")
        price = float(request.form.get("price"))
        description = request.form.get("description")
        author = request.form.get("author")
        image = request.form.get("image", "")
        
        if not manga_name or not price or not author:
            flash("Manga name, price, and author are required", "danger")
            return redirect(url_for('create_manga'))
        
        new_manga = Manga(
            name=manga_name,
            price=price,
            description=description,
            author=author,
            image=image
        )
        
        db.session.add(new_manga)
        db.session.commit()
        
        flash("Manga added successfully!", "success")
        return redirect(url_for('manga'))
    
    return render_template("create_manga.html", is_logged_in=is_logged_in())

@app.route("/edit_manga/<int:manga_id>", methods=["GET", "POST"])
def edit_manga(manga_id):
    if not is_logged_in():
        flash("Please login to edit manga", "warning")
        return redirect(url_for('login'))
    
    manga = Manga.query.get_or_404(manga_id)
    
    if request.method == "POST":
        manga.name = request.form.get("manga_name")
        manga.price = float(request.form.get("price"))
        manga.description = request.form.get("description")
        manga.author = request.form.get("author")
        manga.image = request.form.get("image")
        
        db.session.commit()
        flash("Manga updated successfully!", "success")
        return redirect(url_for('manga_detail', manga_id=manga.id))
    
    return render_template("edit_manga.html", manga=manga, is_logged_in=is_logged_in())

@app.route("/delete_manga/<int:manga_id>")
def delete_manga(manga_id):
    if not is_logged_in():
        flash("Please login to delete manga", "warning")
        return redirect(url_for('login'))
    
    manga = Manga.query.get_or_404(manga_id)
    
    # Delete related cart items and orders
    Cart.query.filter_by(product_id=manga_id).delete()
    Order.query.filter_by(product_id=manga_id).delete()
    
    db.session.delete(manga)
    db.session.commit()
    
    flash("Manga deleted successfully!", "success")
    return redirect(url_for('manga'))

@app.route("/login", methods=["GET", "POST"])
def login():
    if is_logged_in():
        return redirect(url_for('index'))
    
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash("Login successful!", "success")
            return redirect(url_for('index'))
        else:
            flash("Invalid username or password", "danger")
    
    return render_template("login.html", is_logged_in=is_logged_in())

@app.route("/logout")
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash("You have been logged out", "success")
    return redirect(url_for('loggedout'))

@app.route("/orders")
def orders():
    if not is_logged_in():
        flash("Please login to view your orders", "warning")
        return redirect(url_for('login'))
    
    user_orders = Order.query.filter_by(user_id=session['user_id']).order_by(Order.order_date.desc()).all()
    order_list = []
    
    for order in user_orders:
        manga = Manga.query.get(order.product_id)
        order_list.append({
            'id': order.id,
            'manga_name': manga.name,
            'quantity': order.quantity,
            'price': manga.price,
            'total': manga.price * order.quantity,
            'date': order.order_date,
            'status': order.status
        })
    
    return render_template("orders.html", orders=order_list, is_logged_in=is_logged_in())

if __name__ == '__main__':
    app.run(debug=True)