import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

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

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///kanban.db")

# Make sure API key is set
#if not os.environ.get("API_KEY"):
#    raise RuntimeError("API_KEY not set")


@app.route("/", methods=["GET"])
@login_required
def index():

    log_usr = session["user_id"]
    rows_todo = db.execute("SELECT priority, description, due_date, id FROM tasks WHERE responsible = :logged AND status = 'To Do' ORDER BY priority", logged = log_usr)
    rows_inp = db.execute("SELECT priority, description, due_date, id FROM tasks WHERE responsible = :logged AND status = 'In Progress' ORDER BY priority", logged = log_usr)
    rows_done = db.execute("SELECT priority, description, due_date, id FROM tasks WHERE responsible = :logged AND status = 'Done' ORDER BY priority", logged = log_usr)

    tasks_todo = []
    for row in rows_todo:
        tasks_todo.append({
            "priority": row["priority"],
            "description": row["description"],
            "due_date": row["due_date"],
            "id": row["id"],
        })

    tasks_inp = []
    for row in rows_inp:
        tasks_inp.append({
            "priority": row["priority"],
            "description": row["description"],
            "due_date": row["due_date"],
            "id": row["id"],
        })

    tasks_done = []
    for row in rows_done:
        tasks_done.append({
            "priority": row["priority"],
            "description": row["description"],
            "due_date": row["due_date"],
            "id": row["id"],
        })

    return render_template("index.html", tasks_todo = tasks_todo, tasks_inp = tasks_inp, tasks_done = tasks_done, log_usr = log_usr)


@app.route("/howto")
@login_required
def howto():
    return render_template("howto.html")

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
        flash("Login successful!")
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
    flash("Logged out!")
    return redirect("/")


@app.route("/new", methods=["GET", "POST"])
@login_required
def new():

    if request.method == "GET":
        return render_template("new.html")
    else:
        log_usr = session["user_id"]
        priority = request.form.get("priority")
        description = request.form.get("description")
        status = request.form.get("status")
        duedate = request.form.get("duedate")
        if not request.form.get("priority"):
            return apology("Priority field is mandatory", "Missing info")
        elif not request.form.get("description"):
            return apology("Description field is mandatory", "Missing info")
        elif not request.form.get("status"):
            return apology("Status field is mandatory", "Missing info")
        elif not request.form.get("duedate"):
            return apology("Due date field is mandatory", "Missing info")
        else:
            db.execute("INSERT INTO tasks (responsible, priority, description, due_date, status) VALUES (:responsible, :priority, :description, :due_date, :status)", responsible = log_usr, priority = priority, description = description, due_date = duedate, status = status)
            flash("Task created")
            return redirect("/")


@app.route("/edit", methods=["GET", "POST"])
@login_required
def edit():
    if request.method == "GET":
        log_usr = session["user_id"]

        id_edit = request.args["id_edit"]

        rows_edit = db.execute("SELECT priority, description, due_date, id, Status FROM tasks WHERE responsible = :logged AND id = :id_edit ORDER BY priority", logged = log_usr, id_edit = id_edit)
        priority = rows_edit[0]["priority"]
        description = rows_edit[0]["description"]
        due_date = rows_edit[0]["due_date"]
        status = rows_edit[0]["Status"]

        return render_template("edit.html", priority = priority, description = description, due_date = due_date, status = status, id_edit = id_edit)

    else:

        id_edit = request.form.get("id_edit")

        log_usr = session["user_id"]
        priority = request.form.get("priority")
        description = request.form.get("description")
        status = request.form.get("status")
        duedate = request.form.get("duedate")

        if not request.form.get("priority"):
            return apology("Priority field is mandatory", "Missing info")
        elif not request.form.get("description"):
            return apology("Description field is mandatory", "Missing info")
        elif not request.form.get("status"):
            return apology("Status field is mandatory", "Missing info")
        elif not request.form.get("duedate"):
            return apology("Due date field is mandatory", "Missing info")
        else:
            db.execute("UPDATE tasks SET priority = :priority, description = :description, due_date = :due_date, status = :status WHERE id = :id_edit", priority = priority, description = description, due_date = duedate, status = status, id_edit = id_edit)
            flash("Task updated")
            return redirect("/")




@app.route("/delete", methods=["GET", "POST"])
@login_required
def delete():
    if request.method == "GET":
        log_usr = session["user_id"]

        id_edit = request.args["id_edit"]

        rows_edit = db.execute("SELECT priority, description, due_date, id, Status FROM tasks WHERE responsible = :logged AND id = :id_edit ORDER BY priority", logged = log_usr, id_edit = id_edit)
        priority = rows_edit[0]["priority"]
        description = rows_edit[0]["description"]
        due_date = rows_edit[0]["due_date"]
        status = rows_edit[0]["Status"]

        return render_template("delete.html", priority = priority, description = description, due_date = due_date, status = status, id_edit = id_edit)

    else:

        id_edit = request.form.get("id_edit")

        log_usr = session["user_id"]
        priority = request.form.get("priority")
        description = request.form.get("description")
        status = request.form.get("status")
        duedate = request.form.get("duedate")

        db.execute("DELETE FROM tasks WHERE id = :id_edit", id_edit = id_edit)
        flash("Task deleted")
        return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
#    """Register user"""
    if request.method == "GET":
        return render_template("register.html")
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        rpt_pwd = request.form.get("rpt_password")
        check_usr = db.execute("SELECT * FROM users where username = :name", name = username)
        if password != rpt_pwd:
            return apology("passwords are not the same", "PWD MISSMATCH")
        elif password == "":
            return apology("must provide a password", "BLANK PWD")
        elif username == "":
            return apology("must provide username", "BLANK USR")
        else:
            if not check_usr:
                hash_pwd = generate_password_hash(password)
                db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash_pwd)", username=username, hash_pwd=hash_pwd)
                flash("Success")
                return redirect("/")
            else:
                return apology ("Username already in use", "Username Taken")

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
