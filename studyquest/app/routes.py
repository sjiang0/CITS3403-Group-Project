from app import app
from flask import render_template

@app.route("/")  # !! Change when login is properly implemented
@app.route("/dashboard")
def dashboard():
    return render_template('dashboard.html')

@app.route("/my-quests")
def my_quests():
    return render_template("my_quests.html")

@app.route("/create-quest")
def create_quest():
    return render_template("create_quest.html")