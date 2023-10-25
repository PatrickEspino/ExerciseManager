import tkinter as tk
from tkinter import messagebox
import sqlite3
import time

# Initialize the SQLite database
conn = sqlite3.connect('exercise_data.db')
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS exercises (
        id INTEGER PRIMARY KEY,
        exercise_name TEXT,
        sets INTEGER,
        is_timed BOOLEAN,
        value INTEGER
    )
''')
conn.commit()

root = tk.Tk()
root.title("Exercise List")

frm_form = tk.Frame(relief=tk.SUNKEN, borderwidth=3)
frm_form.pack()

#Exercise Name Entry
lbl_exercise = tk.Label(master=frm_form, text="Exercise: ")
lbl_exercise.grid(row=0, column=0, sticky="e")
ent_exercise = tk.Entry(master=frm_form, width=50)
ent_exercise.grid(row=0, column=1)

#Set Entry
lbl_sets = tk.Label(master=frm_form, text="Sets: ")
lbl_sets.grid(row=1, column=0, sticky="e")
ent_sets = tk.Entry(master=frm_form, width=50)
ent_sets.grid(row=1, column=1)

#Timed or Reps Radiobuttons
timed_or_reps = tk.BooleanVar()
timed_or_reps.set(True)
radio_frame = tk.Frame(master=frm_form)
radio_frame.grid(row=2, column=1, sticky="w")
reps_radio = tk.Radiobutton(master=radio_frame, text="Reps", variable=timed_or_reps, value=True)
timed_radio = tk.Radiobutton(master=radio_frame, text="Timed", variable=timed_or_reps, value=False)
reps_radio.pack(side="left")
timed_radio.pack(side="left")


#Timed or Reps Entry
lbl_reps = tk.Label(master=frm_form, text="Reps: ")
lbl_reps.grid(row=3, column=0, sticky="e")
ent_reps = tk.Entry(master=frm_form, width=50)
ent_reps.grid(row=3, column=1)
ent_reps.config(state=tk.NORMAL)

lbl_time = tk.Label(master=frm_form, text="Time (seconds): ")
lbl_time.grid(row=4, column=0, sticky="e")
ent_time = tk.Entry(master=frm_form, width=50)
ent_time.grid(row=4, column=1)
ent_time.config(state=tk.DISABLED)

#Toggle Time/Reps entry based on radio button
def toggle_time_reps():
    if timed_or_reps.get():
        ent_reps.config(state=tk.NORMAL)
        ent_time.config(state=tk.DISABLED)
    else:
        ent_reps.config(state=tk.DISABLED)
        ent_time.config(state=tk.NORMAL)

timed_or_reps.trace("w", lambda name, index, mode, timed_or_reps=timed_or_reps: toggle_time_reps())


def submit():
    exercise_name = ent_exercise.get()
    sets = ent_sets.get()
    is_reps = timed_or_reps.get()
    if is_reps:
        rep_value = ent_reps.get()
        lbl_result.config(text=f'Exercise: {exercise_name}, Sets: {sets}, Time: {rep_value} seconds')
        c.execute("INSERT INTO exercises (exercise_name, sets, is_timed, value) VALUES (?, ?, ?, ?)", (exercise_name, sets, 0, rep_value))
    else:
        time_value = ent_time.get()
        lbl_result.config(text=f'Exercise: {exercise_name}, Sets: {sets}, Reps: {time_value}')
        c.execute("INSERT INTO exercises (exercise_name, sets, is_timed, value) VALUES (?, ?, ?, ?)", (exercise_name, sets, 1, time_value))
    conn.commit()
    update_list()
    
#Submit button
btn_submit = tk.Button(master=frm_form, text = "Submit", command=submit)
btn_submit.grid(row=5, column=0, sticky="ew")

#Result Label
lbl_result = tk.Label(master=frm_form, text="")
lbl_result.grid(row=6, column=1, sticky="w")

#Exercise List
list_exercise = tk.Listbox(master=frm_form, width=50)
list_exercise.grid(row=7, column=1)

#Update the exercise list
def update_list():
    list_exercise.delete(0, tk.END)
    for row in c.execute("SELECT * FROM exercises"):
        exercise_type = "Timed" if row[3] == 1 else "Reps"
        list_exercise.insert(tk.END, f"Exercise: {row[1]}, Sets: {row[2]}, Type: {exercise_type}, Value: {row[4]}")

update_list()

def begin(li):
    root.withdraw()
    window2 = tk.Toplevel(root)
    window2.title("Workout")

    item_ids = []

    list_workouts = tk.Listbox(window2, width=50)
    for item in li.get(0, "end"):
        item_parts = item.split(", ")
        exercise_id = int(item_parts[-1].split(": ")[1])
        item_ids.append(exercise_id)
        list_workouts.insert("end", item)
    list_workouts.grid(row=1)

    def categorize():
        item = list_workouts.curselection()
        if item:
            selected_item = list_workouts.get(item)
            item_parts = selected_item.split(", ")
            cat = item_parts[2].split(": ")[1]
            print(cat)
            if cat == "Reps":
                open_set_count_window(item_parts)
            else:
                open_time_count_window(item_parts)

    def on_double_click(event):
        selected_index = list_workouts.nearest(event.y)
        if selected_index >= 0:
            selected_item = list_workouts.get(selected_index)
            item_parts = selected_item.split(", ")
            cat = item_parts[2].split(": ")[1]
            if cat == "Reps":
                open_set_count_window(item_parts)
            else:
                open_time_count_window(item_parts)
    
    list_workouts.bind("<Double-Button-1>", on_double_click)

    def workout_window(item):
        selected_index = list_workouts.curselection()
        set_count_window = tk.Toplevel(window2)
        set_count_window.title("Set Count")
        lbl_exercise = tk.Label(set_count_window, text="Exercise: ")
        lbl_exercise.grid(row=0, column=0)
        lbl_name = tk.Label(set_count_window, text=item[0].split(": ")[1])
        lbl_name.grid(row=0, column=1)
        lbl_set_count = tk.Label(set_count_window, text="Sets Remaining: ")
        lbl_set_count.grid(row=2, column=0)
        set_count = tk.IntVar()
        set_count.set(int(item[1].split(": ")[1]))
        ent_set_count = tk.Entry(set_count_window, textvariable=set_count)
        ent_set_count.grid(row=2, column=1)
        ent_set_count.config(state=tk.DISABLED)
        
        return selected_index, set_count, set_count_window

    def open_set_count_window(item):
        selected_index, set_count, set_count_window = workout_window(item)

        lbl_reps = tk.Label(set_count_window, text="Reps: ")
        lbl_reps.grid(row=1, column=0)
        lbl_rep_count = tk.Label(set_count_window, text=item[-1].split(": ")[1])
        lbl_rep_count.grid(row=1, column=1)


        def decrement_set_count():
            current_sets = set_count.get()
            if current_sets > 0:
                set_count.set(current_sets - 1)
                if current_sets - 1 == 0:
                    list_workouts.delete(selected_index)
                    set_count_window.destroy()
                    messagebox.showinfo("Congratulations", "Good job finishing exercise!")


        decrement_button = tk.Button(set_count_window, text="Decrement Set Count", command=decrement_set_count)
        decrement_button.grid(row=2, column=0)


    def open_time_count_window(item):
        selected_index, set_count, time_count_window = workout_window(item)

        lbl_time = tk.Label(time_count_window, text="Time: ")
        lbl_time.grid(row=3, column=0)
        time_count = tk.IntVar()
        time_count.set(int(item[3].split(": ")[1]))
        ent_time = tk.Entry(time_count_window, textvariable=time_count)
        ent_time.grid(row=3, column=1)
        ent_time.config(state=tk.DISABLED)

        def update_timer():
            total_time = int(item[3].split(": ")[1])
            temp_time = time_count.get()
            if temp_time > 0:
                time_count.set(temp_time - 1)
                time_count_window.after(1000, update_timer)
                btn_start_timer.config(state=tk.DISABLED)
            else:
                btn_start_timer.config(state=tk.NORMAL)
                current_sets = set_count.get()
                time_count.set(total_time)
                set_count.set(current_sets - 1)
                if current_sets - 1 == 0:
                    list_workouts.delete(selected_index)
                    time_count_window.destroy()
                    messagebox.showinfo("Congratulations", "Good job finishing exercise!")
        
        btn_start_timer = tk.Button(time_count_window, text="Start Timer", command=update_timer)
        btn_start_timer.grid(row=4,column=0)
                
    btn_complete = tk.Button(window2, text="Begin Item", width=25, command=categorize)
    btn_complete.grid(row=2, column=0, sticky="w")
    btn_test = tk.Button(window2, text="End workout", command=lambda: [finish(), window2.destroy()], width=25)
    btn_test.grid(row=3, column=0, sticky="w")

#Begin workout button
btn_start = tk.Button(master=frm_form, text="Begin Workout", command=lambda: begin(list_exercise))
btn_start.grid(row=9, column=1, sticky="w")


#Delete from database
def delete():
    selected_item = list_exercise.curselection()
    if selected_item:
        selected = list_exercise.get(selected_item)
        item_name = selected.split(", ")[0].split(": ")[1]
        c.execute("SELECT id FROM exercises WHERE exercise_name = ?", (item_name,))
        result = c.fetchone()
        c.execute("DELETE FROM exercises where id = ?", (result[0],))
        conn.commit()
        update_list()

btn_delete = tk.Button(master=frm_form, text="Delete Exercise", command=delete)
btn_delete.grid(row=8, column=1, sticky="w")

def finish():
    messagebox.showinfo("Congratulations", "Good job finishing workout!")    
    root.deiconify()
    
    

root.mainloop()

