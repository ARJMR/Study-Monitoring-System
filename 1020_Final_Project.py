from engi1020.arduino.api import *
import time
import matplotlib.pyplot as plt
import csv
import os

# Create file and add header if it doesn't exist
if not os.path.exists("session_history.csv") or os.path.getsize("session_history.csv") == 0:
    with open("session_history.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["day", "mode", "study_time", "distracted_time"])
        
Distance_limit = 50   # cm Distance from person to sensor
STUDY_SOUND_THRESHOLD = 170   # stricter — quieter environment required
READING_SOUND_THRESHOLD = 200 # more lenient — some background noise allowed
day_name = time.strftime("%A", time.localtime())

session_history = {}
if day_name not in session_history:
    session_history[day_name] = {
        "study_mode": [],
        "reading_mode": []
    }

def format_time(seconds):
    mins, secs = divmod(seconds, 60)
    return f"{mins:02d}:{secs:02d}"

def update_lcd(study_time,distracted_time):
    rgb_lcd_clear()
    rgb_lcd_print("Study", 0, 0) #row - 0 column - 0
    rgb_lcd_print("Distract", 0, 8)
    
    rgb_lcd_print("|",0,7)
    rgb_lcd_print("|",1,7)
    # timer
    rgb_lcd_print(format_time(study_time), 1, 0)
    rgb_lcd_print(format_time(distracted_time), 1, 8)
    
def study_mode():
    rgb_lcd_colour(50, 50, 0)
    rgb_lcd_clear()
    rgb_lcd_print("Studying Mode", 0, 0)
    print("--- Studying Mode Started ---\n")
    print("Press the stop button to end the session.")
    time.sleep(1)
    run_session(sound_threshold=STUDY_SOUND_THRESHOLD,mode_name ="study_mode")    # strict threshold

def reading_mode():
    rgb_lcd_colour(0, 50, 50)
    rgb_lcd_clear()
    rgb_lcd_print("Reading Mode", 0, 0)
    print("--- Reading Mode Started ---\n")
    print("Press the stop button to end the session.")
    time.sleep(1)
    run_session(sound_threshold=READING_SOUND_THRESHOLD,mode_name = "reading_mode")# lenient threshold
    
def run_session(sound_threshold,mode_name):
    """
    sound_threshold: int
        Study mode  → lower value (stricter, less noise allowed)
        Reading mode → higher value (lenient, more noise allowed)
    """
    stop, distract_tresh, study_time, distracted_time = False,0,0,0

    while not stop:
        # --- Stop button ---
        if digital_read(6) == 1:
            stop = True
            break

        # --- Sensor readings ---
        distance = ultra_get_centimeters(6)
        sound    = analog_read(2)         

        # --- Distraction logic ---
        # Person is absent OR environment is too noisy
        is_distracted = (distance > Distance_limit) or (sound > sound_threshold)

        if not is_distracted:
            study_time += 1

        elif distract_tresh >= 5:
            print("You have been distracted! Press the button to dismiss.")
            digital_write(4, True)
            while True:
                if digital_read(6) == 1:
                    distract_tresh = 0
                    digital_write(4, False)
                    break
        else:
            distracted_time += 1
            distract_tresh += 1

        update_lcd(study_time,distracted_time)
        time.sleep(1)
        
    session_summary(study_time,distracted_time,mode_name)
    show_summary(study_time,distracted_time)
    
def session_summary(study_time,distracted_time,mode_name):
    global session_history
    
    if mode_name == "study_mode" :
        session_history[day_name]["study_mode"].append((study_time, distracted_time))
    else :
        session_history[day_name]["reading_mode"].append((study_time, distracted_time))
    save_to_csv(day_name, mode_name, study_time, distracted_time)
   
def show_summary(study_time,distracted_time):
    print("\n------- Session Summary -------")
    print(f"Study Time      : {format_time(study_time)}")
    print(f"Distracted Time : {format_time(distracted_time)}")
    total = study_time + distracted_time
    if total > 0:
        efficiency = round((study_time / total) * 100)
        print(f"Focus Efficiency: {efficiency}%")
    print("-------------------------------")
    
def plot_session_summary():
    global session_history

    study_mode_study = 0
    study_mode_distract = 0
    reading_mode_study = 0
    reading_mode_distract = 0

    # study mode totals
    for study_time, distract_time in session_history[day_name]["study_mode"]:
        study_mode_study += study_time
        study_mode_distract += distract_time

    # reading mode totals
    for study_time, distract_time in session_history[day_name]["reading_mode"]:
        reading_mode_study += study_time
        reading_mode_distract += distract_time

    modes = ["Study Mode", "Reading Mode"]

    study_times = [study_mode_study, reading_mode_study]
    distract_times = [study_mode_distract, reading_mode_distract]

    x = range(len(modes))
    width = 0.35

    plt.bar([i - width/2 for i in x], study_times, width, label="Study Time")
    plt.bar([i + width/2 for i in x], distract_times, width, label="Distracted Time")

    plt.xticks(x, modes)
    plt.ylabel("Time (seconds)")
    plt.title(f"Focus Comparison on {day_name}")
    plt.legend()
    plt.show()

def save_to_csv(day, mode, study_time, distracted_time):
    with open("session_history.csv", "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([day, mode, study_time, distracted_time])
        
def load_from_csv():
    data = []

    with open("session_history.csv", "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            data.append({
                "day": row["day"],
                "mode": row["mode"],
                "study_time": int(row["study_time"]),
                "distracted_time": int(row["distracted_time"])
            })
    return data

def plot_all_days():
    data = load_from_csv()
    
    # Initialize totals dictionaries
    day_study_totals = {}
    day_distract_totals = {}

    # Sum study and distracted times per day
    for row in data:
        day = row["day"]
        if day not in day_study_totals:
            day_study_totals[day] = 0
            day_distract_totals[day] = 0

        day_study_totals[day] += row["study_time"]
        day_distract_totals[day] += row["distracted_time"]

    # Prepare for plotting
    days = list(day_study_totals.keys())
    study_totals = [day_study_totals[day] for day in days]
    distract_totals = [day_distract_totals[day] for day in days]

    # Plot side-by-side bars
    x = range(len(days))
    width = 0.35
    plt.bar([i - width/2 for i in x], study_totals, width, label="Study Time")
    plt.bar([i + width/2 for i in x], distract_totals, width, label="Distracted Time")

    plt.xticks(x, days)
    plt.ylabel("Time (seconds)")
    plt.title("Study vs Distracted Time Across Days")
    plt.legend()
    plt.show()

while True:
    
    # -------- Main Menu --------
    choice = input(
        "____________MODES_____________\n\n"
        "Option [1] : Studying Mode\n"
        "Option [2] : Reading Mode\n"
        "Option [3] : History of Sessions\n"
        "Option [4] : History of Sessions Across a Week\n"
        "Option [5] : End Session\n"
        "Enter choice: "
    )
    if choice == "1":
        study_mode()
    elif choice == "2":
        reading_mode()
    elif choice == "3":
        if len(session_history) == 0:
            print("No sessions recorded yet.")
        else:
            plot_session_summary()
    elif choice == "4":
        plot_all_days()
    elif choice == "5":
        print("Closing program", end="", flush=True)
        for _ in range(3):
            time.sleep(0.4)
            print(".", end="", flush=True)
        print() 
        break
    else:
        print("Invalid choice.")
