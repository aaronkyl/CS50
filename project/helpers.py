import csv
import urllib.request
from urllib.parse import urlparse

from flask import redirect, render_template, request, session, url_for
from functools import wraps

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.11/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect(url_for("login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# none of these classes are used but I'm keeping them in the code as examples for future reference
class Exercise_Set:
    def __init__(self, set_no, reps, weight):
        self.set_no = set_no
        self.reps = reps
        self.weight = weight

class Exercise:
    def __init__(self, exercise_id):
        self.id = exercise_id
        self.sets = []

    def add_set(self, set_no, reps, weight):
        #create set object, passing in set_counter
        new_set = Exercise_Set(set_no, reps, weight)
        #add set object to sets list
        self.sets.append(new_set)
        #increment set counter for this exercise

class Workout:
    """
    Class to contain each workout, composed of exercise objects which contain set objects
    """
    def __init__(self, workout_id):
        self.id = workout_id
        self.exercises = []

    def add_set1(self, exercise_id, set_no, reps, weight):
        """
        Checks if exercise id already exists in workout and adds a new set to it if so,
        or creates new exercise object and inserts the first set if not
        """
        # check to see if the exercise already exists in the workout
        for exercise in self.exercises:
            # if exercise exists, add new set and return
            if exercise.id == exercise_id:
                exercise.add_set(set_no, reps, weight)
                return
        # if exercise not already in workout, create exercise object
        exercise = Exercise(exercise_id)
        # add set to exercise
        exercise.add_set(set_no, reps, weight)
        # add new exercise to exercise list
        self.exercises.append(exercise)

    def print_all(self):
        """
        Prints all data in the workout object
        """
        print("Workout ID: " + str(self.id))
        for exercise in self.exercises:
            print("--------")
            print("Exercise ID: " + str(exercise.id))
            for set_no in exercise.sets:
                print("  set: " + str(set_no.set_no))
                print("  reps: " + str(set_no.reps))
                print("  weight: " + str(set_no.weight))

def is_float(string):
    try:
        float(string)
        return True
    except ValueError:
        return False