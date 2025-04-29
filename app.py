from flask import Flask, render_template, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#Routing
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/base")
def base():
    return render_template("base.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/cart")
def cart():
    return render_template("cart.html")

@app.route("/loggedin")
def loggedin():
    return render_template("loggedin.html")

@app.route("/loggedout")
def loggedout():
    return render_template("loggedout.html")

@app.route("/manga_detail")
def manga_detail():
    return render_template("manga_detail.html")

@app.route("/checkout")
def checkout():
    return render_template("checkout.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/manga")
def manga():
    return render_template("manga.html")

@app.route("/create_manga")
def create_manga():
    return render_template("create_manga.html")

@app.route("/login")
def login():
    return render_template("login.html")

# Database Connection



#Database Objects

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)

class Manga(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(500), nullable=True)
    author = db.Column(db.String(150), nullable=False)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('manga.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('manga.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

class Login(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)

#CRUD Methods

@app.route("/submit_product", methods=["POST"])
def create_product():
    mangaName = request.form.get("mangaName")
    price = request.form.get("price")
    description = request.form.get("description")

    new_manga = Manga(name=mangaName, price=price, description=description)
    db.session.add(new_manga)
    db.session.commit()

    return redirect(url_for('products'))

    



if __name__ == '__main__':
    app.run(debug = True)