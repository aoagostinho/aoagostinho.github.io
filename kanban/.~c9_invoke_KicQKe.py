import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    return apology("TODO PORTFOLIO")


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "GET":
        return render_template("buy.html")
    elif not request.form.get("symbol"):
        return apology("Missing Symbol", "No Symbol")
    elif not request.form.get("shares"):
        return apology("Please provide a share", "No share")
    else:
        symbol = lookup(request.form.get("symbol"))
        shares = int(request.form.get("shares"))
        if symbol == None:
            return apology("INVALID SYMBOL", "INVALID")
        elif shares < 1:
            return apology("Please provide a valid share", "At least 1 share")
        else:
            log_usr = session["user_id"]
            current_money = db.execute("SELECT cash FROM users WHERE id = :logged", logged = log_usr)
            current_money = usd(current_money[0]["cash"])
            unit_cost = usd(lookup(request.form.get("symbol"))["price"])
            if current_money < usd(unit_cost * shares):
                return apology("You don't have cash enough", "No cash")


        #    return render_template("quoted.html", symbol = log_usr, result = current_money, resultn = log_usr)


        #    return render_template("quoted.html", symbol = request.form.get("symbol"), result = usd(lookup(request.form.get("symbol"))["price"]), resultn = lookup(request.form.get("symbol"))["name"])

@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    return apology("TODO")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
#    """Get stock quote."""
    if request.method == "GET":
        return render_template("quote.html")
    else:
        symbol = lookup(request.form.get("symbol"))
        if not request.form.get("symbol"):
            return apology("Missing Symbol", "No Symbol")
        elif symbol == None:
            return apology("INVALID SYMBOL", "INVALID")
        else:
            return render_template("quoted.html", symbol = request.form.get("symbol"), result = usd(lookup(request.form.get("symbol"))["price"]), resultn = lookup(request.form.get("symbol"))["name"])

@app.route("/register", methods=["GET", "POST"])
def register():
#    """Register user"""
    if request.method == "GET":
        return render_template("register.html")
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        rpt_pwd = request.form.get("rpt_password")
        if password != rpt_pwd:
            return apology("passwords are not the same", "PWD MISSMATCH")
        elif password == "":
            return apology("must provide a password", "BLANK PWD")
        elif username == "":
            return apology("must provide username", "BLANK USR")
        else:
            hash_pwd = generate_password_hash(password)
            db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash_pwd)", username=username, hash_pwd=hash_pwd)
            return redirect("/")

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    return apology("TODO")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
