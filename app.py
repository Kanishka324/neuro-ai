from flask import Flask, render_template, request, redirect, send_file
import psycopg2
import os
import csv

app = Flask(__name__)

# -----------------------------
# Database Connection
# -----------------------------
def get_conn():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise Exception("DATABASE_URL is missing")
    return psycopg2.connect(db_url, connect_timeout=5)

# -----------------------------
# Initialize Database (ONLY WHEN NEEDED)
# -----------------------------
def init_db():
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS results (
        id SERIAL PRIMARY KEY,
        typing_speed FLOAT,
        errors INTEGER,
        backspaces INTEGER,
        time_taken FLOAT,
        label TEXT,
        reaction_time FLOAT,
        missed_targets INTEGER,
        accuracy FLOAT
    )
    """)

    conn.commit()
    conn.close()

# -----------------------------
# Homepage
# -----------------------------
@app.route('/')
def index():
    return render_template("index.html")

# -----------------------------
# Questionnaire
# -----------------------------
@app.route('/submit_questionnaire', methods=['POST'])
def questionnaire():
    answers = [int(request.form.get(f"q{i}")) for i in range(1, 11)]
    score = sum(answers)

    if score <= 10:
        label = "Low"
    elif score <= 15:
        label = "Medium"
    else:
        label = "High"

    return redirect(f"/typing?score={score}&label={label}")

# -----------------------------
# Typing Page
# -----------------------------
@app.route('/typing')
def typing():
    return render_template(
        "typing.html",
        score=request.args.get("score"),
        label=request.args.get("label")
    )

# -----------------------------
# ADHD Page
# -----------------------------
@app.route('/adhd')
def adhd():
    return render_template(
        "adhd.html",
        score=request.args.get("score"),
        label=request.args.get("label"),
        typing_speed=request.args.get("typing_speed"),
        errors=request.args.get("errors"),
        backspaces=request.args.get("backspaces"),
        time_taken=request.args.get("time_taken")
    )

# -----------------------------
# Save Data (PostgreSQL)
# -----------------------------
@app.route('/submit_all', methods=['POST'])
def submit_all():

    # 🔥 Ensure table exists (safe + runs only when needed)
    init_db()

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

    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO results 
        (typing_speed, errors, backspaces, time_taken, label, reaction_time, missed_targets, accuracy)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        data["typing_speed"],
        data["errors"],
        data["backspaces"],
        data["time_taken"],
        data["label"],
        data["reaction_time"],
        data["missed_targets"],
        data["accuracy"]
    ))

    conn.commit()
    conn.close()

    return "✅ Data Saved Successfully!"

# -----------------------------
# Export CSV
# -----------------------------
@app.route('/export_csv')
def export_csv():
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM results")
    rows = cursor.fetchall()

    file_path = "data.csv"

    with open(file_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([desc[0] for desc in cursor.description])
        writer.writerows(rows)

    conn.close()

    return send_file(file_path, as_attachment=True)

# -----------------------------
# Run App
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)