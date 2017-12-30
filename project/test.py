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

formdata = [('r3_1', '2'), ('w3_1', '14'), ('r4_1', '2'), ('w4_1', '15'), ('r4_2', '3'), ('w4_2', '16'), ('r6_1', '15'), ('w6_1', '25'), ('r6_2', '15'), ('w6_2', '20'), ('r6_3', '15'), ('w6_3', '17.5')]

workout = Workout(1)

current_exercise_id = None
current_set = None
current_reps = None
current_weight = None

for field in formdata:
    if field[0].startswith("r"):
        spliced = field[0].split('_')
        current_exercise_id = spliced[0][1:]
        current_set = spliced[1]
        current_reps = field[1]
    elif field[0].startswith("w"):
        spliced = field[0].split('_')
        if (current_exercise_id == spliced[0][1:] and current_set == spliced[1]):
            current_weight = field[1]
            workout.add_set1(current_exercise_id, current_set, current_reps, current_weight)
        else:
            print("error with weight field")
    else:
        print("error with field overall")

workout.print_all()