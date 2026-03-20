from flask import Flask, render_template, request, redirect, send_file
import sqlite3
import pandas as pd
import os

app = Flask(__name__)

DB_FILE = "data.db"

# -----------------------------
# Initialize SQLite database
# -----------------------------
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        typing_speed REAL,
        errors INTEGER,
        backspaces INTEGER,
        time_taken REAL,
        label TEXT,
        reaction_time REAL,
        missed_targets INTEGER,
        accuracy REAL
    )
    ''')
    conn.commit()
    conn.close()

init_db()

# -----------------------------
# Homepage: Questionnaire
# -----------------------------
@app.route('/')
def index():
    return render_template("index.html")

# -----------------------------
# Process Questionnaire
# -----------------------------
@app.route('/submit_questionnaire', methods=['POST'])
def questionnaire():
    answers = [int(request.form.get(f"q{i}")) for i in range(1,11)]
    score = sum(answers)

    if score <= 10:
        label = "Low"
    elif score <= 15:
        label = "Medium"
    else:
        label = "High"

    return redirect(f"/typing?score={score}&label={label}")

# -----------------------------
# Typing test page
# -----------------------------
@app.route('/typing')
def typing():
    return render_template("typing.html",
                           score=request.args.get("score"),
                           label=request.args.get("label"))

# -----------------------------
# ADHD reaction page
# -----------------------------
@app.route('/adhd')
def adhd():
    return render_template("adhd.html",
                           score=request.args.get("score"),
                           label=request.args.get("label"),
                           typing_speed=request.args.get("typing_speed"),
                           errors=request.args.get("errors"),
                           backspaces=request.args.get("backspaces"),
                           time_taken=request.args.get("time_taken"))

# -----------------------------
# Save all data: SQLite + CSV
# -----------------------------
@app.route('/submit_all', methods=['POST'])
def submit_all():
    data = {
        "typing_speed": float(request.form['typing_speed']),
        "errors": int(request.form['errors']),
        "backspaces": int(request.form['backspaces']),
        "time_taken": float(request.form['time_taken']),
        "label": request.form['label'],
        "reaction_time": float(request.form['reaction_time']),
        "missed_targets": int(request.form['missed_targets']),
        "accuracy": float(request.form['accuracy'])
    }

    # --- SQLite ---
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        INSERT INTO results 
        (typing_speed, errors, backspaces, time_taken, label, reaction_time, missed_targets, accuracy)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', tuple(data.values()))
    conn.commit()
    conn.close()

    # --- CSV backup ---
    csv_file = "data.csv"
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
        df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    else:
        df = pd.DataFrame([data])

    df.to_csv(csv_file, index=False)

    return "✅ Data Saved Successfully!"

# -----------------------------
# Export CSV route
# -----------------------------
@app.route('/export_csv')
def export_csv():
    csv_file = "data.csv"
    if os.path.exists(csv_file):
        return send_file(csv_file, as_attachment=True)
    else:
        return "No CSV found yet!"

# -----------------------------
# Run the app
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)