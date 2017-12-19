from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp
import datetime
import operator

from helpers import *

# configure application
app = Flask(__name__)

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configure CS50 Library to use SQLite database
db = SQL("sqlite:///cs50fitness.db")

@app.route("/")
def index():

    if session.get("user_id") is None:
        return render_template("index.html")
    else:
        return render_template("dashboard.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # clear any existing user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            return render_template("login.html", logininfo="incorrect", specifics="username missing")

        # ensure password was submitted
        elif not request.form.get("password"):
            return render_template("login.html", logininfo="incorrect", specifics="password missing")

        # query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # ensure username exists and password is correct
        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["password_hash"]):
            return render_template("login.html", logininfo="incorrect")

        # remember which user has logged in
        session["user_id"] = rows[0]["user_id"]
        session["firstname"] = rows[0]["firstname"]

        # redirect user to home page
        return redirect(url_for("dashboard"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("index"))

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user."""

    # clear any current user ID
    session.clear()

    # if user accessed via POST
    if request.method == "POST":

        # check database to see if user exists and print message if so, otherwise register user
        id_exists = db.execute("SELECT user_id FROM users WHERE username = :username", username=request.form.get("username"))

        if len(id_exists) != 0:
            return render_template("register.html", error="Username already exists")
        else:
            db.execute("INSERT INTO users (username, firstname, lastname, password_hash) VALUES (:username, :firstname, :lastname, :pwd)", username=request.form.get("username"), firstname=request.form.get("firstname"), lastname=request.form.get("lastname"), pwd=pwd_context.hash(request.form.get("password")))

       # automatically log in user
        result = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))
        session["user_id"] = result[0]["user_id"]
        session["firstname"] = result[0]["firstname"]
        # send user to dashboard
        return redirect(url_for("dashboard"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

@app.route("/reset", methods=["GET", "POST"])
@login_required
def reset():
    """Reset password"""
#### TODO

    if request.method == "POST":

        # store form entries and current user ID
        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        new_password_conf = request.form.get("new_password_confirm")
        user_id = session["user_id"]

        # confirm user entered data in all fields
        if not current_password or not new_password or not new_password_conf:
            return apology("All fields are required")
        elif not new_password == new_password_conf:
            return apology("New password and confirmation did not match")


        # compare current password entered on form to current password in database
        db_hash = db.execute("SELECT hash FROM users WHERE id = :user", user=user_id)
        if not pwd_context.verify(current_password, db_hash[0]["hash"]):
            return apology("Incorrect current password entered")
        else:
            db.execute("UPDATE users SET hash = :pwd WHERE id = :user", \
                pwd=pwd_context.hash(new_password), \
                user=user_id)
            return redirect(url_for("index"))

    else:
        return render_template("reset.html")

@app.route("/exercises")
@login_required
def exercises():

    if request.method == "POST":
        redirect(url_for("exerciseadd"))
    else:
        exercises = db.execute("SELECT e.exercise_id, exercise_name, routine_id \
            FROM exercises e \
            LEFT JOIN routine_exercises re ON re.exercise_id = e.exercise_id")
        if request.args.get("error"):
            return render_template("exercises.html", exercises=exercises, error=request.args.get("error"))
        else:
            return render_template("exercises.html", exercises=exercises)

@app.route("/exerciseadd", methods=["GET", "POST"])
@login_required
def exerciseadd():

    #TODO
    exercise_name=request.args.get('exercise_name')
    exercise_exists = db.execute("SELECT * FROM exercises where exercise_name = :name", name=exercise_name)

    if exercise_exists:
        return redirect(url_for("exercises", error="Exercise already exists"))
    elif exercise_name == "":
        return redirect(url_for("exercises", error="Name cannot be blank"))
    else:
        db.execute("INSERT INTO exercises (exercise_name) VALUES (:name)", name=exercise_name)
        return redirect(url_for("exercises"))

@app.route("/exerciseedit", methods=["GET", "POST"])
@login_required
def exerciseedit():

    #TODO
    exercise_id = request.args.get('exercise_id')

    # if user accessed via POST
    if request.method == "POST":
        db.execute("UPDATE exercises SET exercise_name = :exercise_name WHERE exercise_id = :exercise_id", exercise_name=request.form.get('exercise_name'), exercise_id=exercise_id)
        return redirect(url_for("exercises"))

    else:
        exercise = db.execute("SELECT * FROM exercises WHERE exercise_id = :exercise_id", exercise_id=exercise_id)
        return render_template("exerciseedit.html", exercise=exercise)

@app.route("/exercisedelete", methods=["GET", "POST"])
@login_required
def exercisedelete():
    db.execute("DELETE FROM exercises WHERE exercise_id = :exercise_id", exercise_id=request.args.get('exercise_id'))
    return redirect(url_for("exercises"))

@app.route("/routines", methods=["GET", "POST"])
@login_required
def routines():

    if request.method == "POST":
        redirect(url_for("routineadd"))
    else:
        routines = db.execute("SELECT * FROM routines")
        if request.args.get("error"):
            return render_template("routines.html", routines=routines, error=request.args.get("error"))
        else:
            return render_template("routines.html", routines=routines)

@app.route("/routineadd", methods=["GET", "POST"])
@login_required
def routineadd():

    #TODO
    routine_name = request.args.get('routine_name')
    routine_exists = db.execute("SELECT * FROM routines where routine_name = :name", name=routine_name)

    if routine_exists:
        return redirect(url_for("routines", error="Routine already exists"))
    elif routine_name == "":
        return redirect(url_for("routines", error="Name cannot be blank"))
    else:
        db.execute("INSERT INTO routines (routine_name, user_id, active) VALUES (:name, :user_id, :active)", name=routine_name, user_id=session["user_id"], active=1)
        return redirect(url_for("routines"))

@app.route("/routineedit", methods=["GET", "POST"])
@login_required
def routineedit():

    #TODO
    routine_id = request.args.get('routine_id')

    # if user accessed via POST
    if request.method == "POST":
        if request.args.get('routine_name') == "":
            return redirect(url_for("routineedit", errortop="Name cannot be blank"))
        else:
            db.execute("UPDATE routines SET routine_name = :routine_name WHERE routine_id = :routine_id", routine_name=request.form.get('routine_name'), routine_id=routine_id)
            return redirect(url_for("routines"))

    else:
        routine = db.execute("SELECT * FROM routines WHERE routine_id = :routine_id", routine_id=routine_id)
        all_exercises = db.execute("SELECT * FROM exercises")
        exercises_in_routine = db.execute("SELECT e.exercise_name, re.no_of_reps FROM exercises e INNER JOIN routine_exercises re ON re.exercise_id = e.exercise_id WHERE re.routine_id = :routine_id", routine_id=routine_id)
        if request.args.get("errortop"):
            return render_template("routineedit.html", routine=routine, all_exercises=all_exercises, exercises_in_routine=exercises_in_routine, errortop=request.args.get("errortop"))
        if request.args.get("errorbottom"):
            return render_template("routineedit.html", routine=routine, all_exercises=all_exercises, exercises_in_routine=exercises_in_routine, errorbottom=request.args.get("errorbottom"))
        return render_template("routineedit.html", routine=routine, all_exercises=all_exercises, exercises_in_routine=exercises_in_routine)

@app.route("/routineexerciseadd", methods=["GET", "POST"])
@login_required
def routineexerciseadd():

    #TODO
    # if user accessed via POST
    if request.method == "POST":
        exercise_to_add_id = request.form.get('exercise_to_add')
        routine_id = request.args.get('routine_id')
        exercise_already_in_routine = db.execute("SELECT * FROM routine_exercises WHERE routine_id = :routine_id AND exercise_id = :exercise_id", routine_id=routine_id, exercise_id=exercise_to_add_id)
        if exercise_already_in_routine:
            return redirect(url_for("routineedit", routine_id=routine_id, errorbottom="Exercise already in routine"))
        else:
            no_of_reps = request.form.get('no_of_reps')
            if no_of_reps == "" or no_of_reps == "0":
                return redirect(url_for("routineedit", routine_id=routine_id, errorbottom="Number of reps must be 1 or more"))
            else:
                db.execute("INSERT INTO routine_exercises (routine_id, exercise_id, no_of_reps) VALUES (:routine_id, :exercise_id, :no_of_reps)", routine_id=routine_id, exercise_id=exercise_to_add_id, no_of_reps=no_of_reps)
                return redirect(url_for("routineedit", routine_id=routine_id))
    else:
        return render_template("routineedit.html")

@app.route("/routineinactivate", methods=["GET", "POST"])
@login_required
def routineinactivate():

    db.execute("UPDATE routines SET active = 0 WHERE routine_id = :routine_id", routine_id=request.args.get('routine_id'))
    return redirect(url_for("routines"))

@app.route("/routineactivate", methods=["GET", "POST"])
@login_required
def routineactivate():

    db.execute("UPDATE routines SET active = 1 WHERE routine_id = :routine_id", routine_id=request.args.get('routine_id'))
    return redirect(url_for("routines"))

@app.route("/workout", methods=["GET", "POST"])
@login_required
def workout():

    #TODO
    # if user accessed via POST
    if request.method == "POST":
        return redirect(url_for("workout"))

    else:
        return render_template("workout.html")

@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():

    #TODO
    # if user accessed via POST
    if request.method == "POST":
        return redirect(url_for("dashboard"))

    else:
        return render_template("dashboard.html")

@app.route("/account", methods=["GET", "POST"])
@login_required
def account():

    #TODO
    # if user accessed via POST
    if request.method == "POST":
        return redirect(url_for("account"))

    else:
        return render_template("account.html")