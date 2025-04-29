from flask import Flask, render_template
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

@app.route("/login")
def login():
    return render_template("login.html")

# Database Connection



#Database Objects

if __name__ == '__main__':
    app.run(debug = True)