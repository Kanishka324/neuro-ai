from flask import Flask, render_template, request, redirect
import pandas as pd
import os

app = Flask(__name__)

FILE = "data.csv"

COLUMNS = [
    "typing_speed","errors","backspaces","time_taken","label",
    "reaction_time","missed_targets","accuracy"
]

# Create CSV if not exists
if not os.path.exists(FILE) or os.stat(FILE).st_size == 0:
    df = pd.DataFrame(columns=COLUMNS)
    df.to_csv(FILE, index=False)

@app.route('/')
def index():
    return render_template("index.html")

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

@app.route('/typing')
def typing():
    return render_template("typing.html",
                           score=request.args.get("score"),
                           label=request.args.get("label"))

@app.route('/adhd')
def adhd():
    return render_template("adhd.html",
                           score=request.args.get("score"),
                           label=request.args.get("label"),
                           typing_speed=request.args.get("typing_speed"),
                           errors=request.args.get("errors"),
                           backspaces=request.args.get("backspaces"),
                           time_taken=request.args.get("time_taken"))

@app.route('/submit_all', methods=['POST'])
def submit_all():
    data = {
        "typing_speed": request.form['typing_speed'],
        "errors": request.form['errors'],
        "backspaces": request.form['backspaces'],
        "time_taken": request.form['time_taken'],
        "label": request.form['label'],
        "reaction_time": request.form['reaction_time'],
        "missed_targets": request.form['missed_targets'],
        "accuracy": request.form['accuracy']
    }

    try:
        df = pd.read_csv(FILE)
    except:
        df = pd.DataFrame(columns=COLUMNS)

    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    df.to_csv(FILE, index=False)

    return "✅ Data Saved Successfully!"

if __name__ == "__main__":
    app.run(debug=True)