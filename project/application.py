# add explanation of flow to dashboard
#   maybe a Help section on the top next to Account?
# add Order field for exercises in routine?

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp
from urllib import request

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
        return redirect(url_for("dashboard"))

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
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username").lower())

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
        id_exists = db.execute("SELECT user_id FROM users WHERE username = :username", username=request.form.get("username").lower())

        if len(id_exists) != 0:
            return render_template("register.html", error="Username already exists")
        else:
            db.execute("INSERT INTO users (username, firstname, lastname, password_hash) VALUES (:username, :firstname, :lastname, :pwd)", username=request.form.get("username").lower(), firstname=request.form.get("firstname"), lastname=request.form.get("lastname"), pwd=pwd_context.hash(request.form.get("password")))

       # automatically log in user
        result = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username").lower())
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
    user_id = session["user_id"]
    if request.method == "POST":
        redirect(url_for("exerciseadd"))
    else:
        exercises = db.execute("SELECT DISTINCT e.exercise_id, e.exercise_name, routine_id \
            FROM exercises e \
            LEFT JOIN routine_exercises re ON re.exercise_id = e.exercise_id \
            WHERE e.user_id = :user_id \
            GROUP BY e.exercise_id \
            ORDER BY exercise_name",
            user_id=user_id)
        if request.args.get("error"):
            return render_template("exercises.html", exercises=exercises, error=request.args.get("error"))
        else:
            return render_template("exercises.html", exercises=exercises)

@app.route("/exerciseadd", methods=["GET", "POST"])
@login_required
def exerciseadd():
    user_id = session["user_id"]
    exercise_name=request.args.get('exercise_name').title()
    exercise_exists = db.execute("SELECT * FROM exercises WHERE exercise_name = :name AND user_id = :user_id", name=exercise_name, user_id=user_id)
    if exercise_exists:
        return redirect(url_for("exercises", error="Exercise already exists"))
    elif exercise_name == "":
        return redirect(url_for("exercises", error="Name cannot be blank"))
    else:
        db.execute("INSERT INTO exercises (exercise_name, user_id) VALUES (:name, :user_id)", name=exercise_name, user_id=user_id)
        return redirect(url_for("exercises"))

@app.route("/exerciseedit", methods=["GET", "POST"])
@login_required
def exerciseedit():
    user_id = session["user_id"]
    exercise_id = request.args.get('exercise_id')
    if request.method == "POST":
        db.execute("UPDATE exercises SET exercise_name = :exercise_name WHERE exercise_id = :exercise_id", exercise_name=request.form.get('exercise_name').title(), exercise_id=exercise_id)
        return redirect(url_for("exercises"))
    else:
        exercise = db.execute("SELECT * FROM exercises WHERE exercise_id = :exercise_id AND user_id = :user_id", exercise_id=exercise_id, user_id=user_id)
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
        routines = db.execute("SELECT * FROM routines WHERE user_id = :user_id ORDER BY routine_name", user_id=session.get('user_id'))
        if request.args.get("error"):
            return render_template("routines.html", routines=routines, error=request.args.get("error"))
        else:
            return render_template("routines.html", routines=routines)

@app.route("/routineadd", methods=["GET", "POST"])
@login_required
def routineadd():
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
    routine_id = request.args.get('routine_id')
    user_id = session["user_id"]
    if request.method == "POST":
        if request.args.get('routine_name') == "":
            return redirect(url_for("routineedit", errortop="Name cannot be blank"))
        else:
            db.execute("UPDATE routines SET routine_name = :routine_name WHERE routine_id = :routine_id", routine_name=request.form.get('routine_name'), routine_id=routine_id)
            return redirect(url_for("routines"))
    else:
        routine = db.execute("SELECT * FROM routines WHERE routine_id = :routine_id", routine_id=routine_id)
        all_exercises = db.execute("SELECT * FROM exercises WHERE user_id = :user_id ORDER BY exercise_name", user_id=user_id)
        exercises_in_routine = db.execute("SELECT e.exercise_id, e.exercise_name, re.no_of_sets FROM exercises e INNER JOIN routine_exercises re ON re.exercise_id = e.exercise_id WHERE re.routine_id = :routine_id", routine_id=routine_id)
        routine_has_been_used = db.execute("SELECT * FROM workouts WHERE routine_id = :routine_id LIMIT 1", routine_id=routine_id)
        if request.args.get("errortop"):
            return render_template("routineedit.html", routine=routine, used=routine_has_been_used, all_exercises=all_exercises, exercises_in_routine=exercises_in_routine, errortop=request.args.get("errortop"))
        if request.args.get("errorbottom"):
            return render_template("routineedit.html", routine=routine, used=routine_has_been_used, all_exercises=all_exercises, exercises_in_routine=exercises_in_routine, errorbottom=request.args.get("errorbottom"))
        return render_template("routineedit.html", routine=routine, used=routine_has_been_used, all_exercises=all_exercises, exercises_in_routine=exercises_in_routine)

@app.route("/routineexerciseadd", methods=["GET", "POST"])
@login_required
def routineexerciseadd():
    if request.method == "POST":
        exercise_to_add_id = request.form.get('exercise_to_add')
        routine_id = request.args.get('routine_id')
        exercise_already_in_routine = db.execute("SELECT * FROM routine_exercises WHERE routine_id = :routine_id AND exercise_id = :exercise_id", routine_id=routine_id, exercise_id=exercise_to_add_id)
        if exercise_already_in_routine:
            return redirect(url_for("routineedit", routine_id=routine_id, errorbottom="Exercise already in routine"))
        else:
            no_of_sets = request.form.get('no_of_sets')
            if no_of_sets == "" or no_of_sets <= "0":
                return redirect(url_for("routineedit", routine_id=routine_id, errorbottom="Number of sets must be greater than 0"))
            elif not no_of_sets.isdigit():
                return redirect(url_for("routineedit", routine_id=routine_id, errorbottom="Number of sets must be a number, you goof"))
            else:
                db.execute("INSERT INTO routine_exercises (routine_id, exercise_id, no_of_sets) VALUES (:routine_id, :exercise_id, :no_of_sets)", routine_id=routine_id, exercise_id=exercise_to_add_id, no_of_sets=no_of_sets)
                return redirect(url_for("routineedit", routine_id=routine_id))
    else:
        return render_template("routineedit.html")

@app.route("/routineexercisedelete", methods=["GET", "POST"])
@login_required
def routineexercisedelete():
    routine_id = request.args.get('routine_id')
    exercise_to_delete_id = request.args.get('exercise_id')
    routine_already_used = db.execute("SELECT * FROM workouts WHERE routine_id = :routine_id LIMIT 1", routine_id=routine_id)
    if routine_already_used:
        return redirect(url_for("routineedit", routine_id=routine_id, errorbottom="Cannot remove exercises from routines which have been used"))
    else:
        db.execute("DELETE FROM routine_exercises WHERE routine_id = :routine_id AND exercise_id = :exercise_id", routine_id=routine_id, exercise_id=exercise_to_delete_id)
        return redirect(url_for("routineedit", routine_id=routine_id))

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
    user_id = session["user_id"]
    if request.method == "POST":
        if request.form.get('workout_routine'):
            routine_id = request.form.get('workout_routine')
            routine_exercises = db.execute("SELECT r.routine_name, e.exercise_name, e.exercise_id, re.no_of_sets \
                FROM exercises e \
                INNER JOIN routine_exercises re ON re.exercise_id = e.exercise_id \
                INNER JOIN routines r ON r.routine_id = re.routine_id \
                WHERE r.user_id = :user_id \
                AND r.routine_id = :routine_id",
                user_id=session["user_id"],
                routine_id=routine_id)
            return render_template("workout.html", routine_id=routine_id, routine_exercises=routine_exercises)
    else:
        all_routines = db.execute("SELECT DISTINCT r.routine_id, r.routine_name FROM routines r INNER JOIN routine_exercises re ON re.routine_id = r.routine_id WHERE r.user_id = :user_id AND r.active = 1", user_id=user_id)
        return render_template("workout.html", all_routines=all_routines)

@app.route("/workoutroutineselected", methods=["GET", "POST"])
@login_required
def workoutroutineselected():
    routine_id = request.form.get('workout_routine')
    routine_exercises = db.execute("SELECT e.exercise_name, e.exercise_id, re.no_of_sets \
        FROM exercises e \
        INNER JOIN routine_exercises re ON re.exercise_id = e.exercise_id \
        INNER JOIN routines r ON r.routine_id = re.routine_id \
        WHERE r.user_id = :user_id \
        AND r.routine_id = :routine_id",
        user_id=session["user_id"],
        routine_id=routine_id)
    return render_template("workout.html", routine_id=routine_id, routine_exercises=routine_exercises)

@app.route("/workoutsubmit", methods=["GET", "POST"])
@login_required
def workoutsubmit():
    workout_id = None;
    routine_id = request.args.get('routine_id')
    ## need to confirm all fields contain numbers ##
    if request.method == "POST":
        # find current highest workout_id (better ways to accomplish what this is doing, especially when more
        # than one person is using the app at a time, but this workaround works for now)
        current_highest_workout_id = db.execute("SELECT MAX(workout_id) FROM workouts")
        current_highest_workout_id = current_highest_workout_id[0]['MAX(workout_id)']
        # determine next record's id
        if current_highest_workout_id:
            workout_id = current_highest_workout_id + 1
        else:
            workout_id = 1
        #insert in workouts table
        now = datetime.date.today()
        db.execute("INSERT INTO workouts (workout_id, routine_id, date) VALUES (:workout_id, :routine_id, :date)",
            workout_id=workout_id,
            routine_id=routine_id,
            date=now)
        # get form data
        formdata = request.form
        # variables to store form data
        current_exercise_id = None
        current_set = None
        current_reps = None
        current_weight = None
        # iterate through each field from the form
        for key in formdata.keys():
            if key.startswith("r"):
                spliced = key.split('_')
                current_exercise_id = spliced[0][1:]
                if ((spliced[1].isdigit() or is_float(spliced[1])) and (formdata[key].isdigit() or is_float(formdata[key]))):
                    current_set = spliced[1]
                    current_reps = formdata[key]
                else:
                    redirect(url_for("dashboard.html"))
            elif key.startswith("w"):
                spliced = key.split('_')
                if (current_exercise_id == spliced[0][1:] and current_set == spliced[1] and (formdata[key].isdigit() or is_float(formdata[key]))):
                    current_weight = formdata[key]
                    db.execute("INSERT INTO workout_details (workout_id, exercise_id, set_no, reps, weight) VALUES \
                        (:workout_id, :exercise_id, :set_no, :reps, :weight)",
                        workout_id = workout_id,
                        exercise_id = current_exercise_id,
                        set_no = current_set,
                        reps = current_reps,
                        weight = current_weight)
                else:
                    redirect(url_for("dashboard.html"))
            else:
                print("general form field error")
    return redirect(url_for('dashboard'))

@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    user_id = session["user_id"]
    #get all of user's workouts
    user_workouts = db.execute("SELECT w.workout_id, r.routine_name, w.date \
        FROM workouts w \
        INNER JOIN routines r ON r.routine_id = w.routine_id \
        WHERE r.user_id = :user_id \
        ORDER BY w.workout_id",
        user_id=user_id)
    #page will have list of workouts showing date, routine name, as links
    #link will lead to workout review page
    #page will show exercise name, sets, reps, weights
    #return button will take user back to dashboard
    return render_template("dashboard.html", workouts=user_workouts)

@app.route("/workout_review", methods=["GET", "POST"])
@login_required
def workout_review():
    workout_id = request.args.get('workout_id')
    workout_information = db.execute("SELECT r.routine_name, w.date, e.exercise_name, wd.set_no, wd.reps, wd.weight \
        FROM workouts w \
        INNER JOIN routines r ON r.routine_id = w.routine_id \
        INNER JOIN workout_details wd ON wd.workout_id = w.workout_id \
        INNER JOIN exercises e ON e.exercise_id = wd.exercise_id \
        WHERE w.workout_id = :workout_id",
        workout_id = workout_id)
    return render_template("workout_review.html", workout_information = workout_information)

@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    user_id = session["user_id"]
    # if user accessed via POST
    if request.method == "POST":
        if request.args.get('update_name'):
            db.execute("UPDATE users SET firstname = :firstname, lastname = :lastname WHERE user_id = :user_id",
                firstname = request.form.get('firstname'),
                lastname = request.form.get('lastname'),
                user_id = user_id)
            session["firstname"] = request.form.get('firstname')
        if request.args.get('change_password'):
            current_password = request.form.get("current_password")
            new_password = request.form.get("new_password")
            new_password_conf = request.form.get("new_password_confirm")
            db_hash = db.execute("SELECT password_hash FROM users WHERE user_id = :user", user=user_id)
            if not pwd_context.verify(current_password, db_hash[0]["password_hash"]):
                return redirect(url_for("account", password_error="Password incorrect"))
            else:
                db.execute("UPDATE users SET password_hash = :pwd WHERE user_id = :user_id",
                    pwd=pwd_context.hash(new_password),
                    user_id=user_id)
        return redirect(url_for("account"))

    else:
        user_info=db.execute("SELECT firstname, lastname FROM users WHERE user_id = :user_id", user_id = user_id)
        if request.args.get('password_error'):
            return render_template("account.html", user_info=user_info, password_error=request.args.get('password_error'))
        else:
            return render_template("account.html", user_info=user_info)