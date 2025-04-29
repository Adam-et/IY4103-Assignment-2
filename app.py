from flask import Flask, render_template

app = Flask(__name__)

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

if __name__ == 'main':
    app.run(debug = True)