import os
import csv
import smtplib

from cs50 import SQL

from flask_mail import Message, Mail
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
#from flask_session import Session

from functools import wraps
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

import pygal
from pygal.style import Style

# Configure application
app = Flask(__name__)

# Configure email service
app.config.update (

    MAIL_SERVER = "smtp.gmail.com",
    MAIL_USE_SSL = True,
    MAIL_PORT = 465,
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME'),
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD'),
    SECRET_KEY = os.environ.get('SECRET_KEY')
)

mail = Mail(app)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///learners.db")

# Set style for pygal diagrams
custom_style=Style(
    colors=('#4e5b1c', '#7c8736', '#9dae28', '#c2d33f'),
    background='transparent',
    opacity='1',
    opacity_hover='0.8',
    font_family='googlefont:Roboto',
    legend_font_size=25,
    title_font_size=35,
    tooltip_font_size=25)


# First page which user sees
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():

    reg_user = db.execute("SELECT * FROM users WHERE username = :username", username = request.form.get("username"))

    if request.method == "POST":

        # Check if imput is not empty
        if not request.form.get("username") or not request.form.get("email") or not request.form.get("password") or not request.form.get("confirmation"):
            flash("Please fill all fields")
            return render_template("register.html")

        # Check if input is correct
        if not ("@" and ".") in request.form.get("email"):
            flash("Please provide valid email address")
            return render_template("register.html")
        elif len(request.form.get("password")) < 6:
            flash("Password is too short")
            return render_template("register.html")
        elif request.form.get("confirmation") != request.form.get("password"):
            flash("Passwords do not match")
            return render_template("register.html")
        elif len(reg_user) > 0:
            flash("Such username already exists")
            return render_template("register.html")
        else:
            # Register new user
            db.execute("INSERT INTO users(username, hash, email, hm, vak) VALUES(:username, :hash, :email, 'no', 'no')",
                        username = request.form.get("username"),
                        hash = generate_password_hash(request.form.get("password")),
                        email = request.form.get("email"))
            # Start session without login
            new_user = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))
            session["user_id"] = new_user[0]["id"]
            return redirect("/home")

    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    # Forget any user_id
    session.clear()

    if request.method == "POST":

        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # Ckeck if input is correct
        if not request.form.get("username") or not request.form.get("password"):
            flash("Please fill all fields")
            return render_template("login.html")
        elif len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash("Invalid username and/or password")
            return render_template("login.html")
        else:
            session["user_id"] = rows[0]["id"]
            return redirect("/home")

    else:
        return render_template("login.html")


def login_required(f):

    # http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


@app.route("/home")
@login_required
def home():
    return render_template("home.html")


@app.route("/hm_test", methods=["GET", "POST"])
@login_required
def hm_test():

    # Questions are stored in file and rendered to the HTML template
    file_hm = open("static/hm_test.csv", "r")
    hm_questions = csv.DictReader(file_hm, delimiter=";")

    if request.method == "POST":

        # Calculate result
        a = 0
        r = 0
        t = 0
        p = 0

        data=str(request.get_data())
        hm_data=data[2:(len(data)-1)].split("&")
        for i in hm_data:
            choice=i.rstrip(".=on")
            print(choice)
            if choice == "activist":
                a+=1
            elif choice == "reflector":
                r+=1
            elif choice == "theorist":
                t+=1
            else:
                p+=1

        # Draw distribution diagram
        pie_chart = pygal.Pie(inner_radius=.4, style=custom_style)
        pie_chart.title = 'Honey-Mumford distribution'
        pie_chart.add('Activist', a)
        pie_chart.add('Pragmatist', p)
        pie_chart.add('Reflector', r)
        pie_chart.add('Theorist', t)
        pie_chart.render_to_file('static/pies/hm_pie{}.svg'.format(session['user_id']))

        # Update user data
        db.execute("UPDATE users SET hm = 'yes' WHERE id = :id", id = session["user_id"])

        return redirect("/my_results")

    else:
        return render_template("hm_test.html", hm_questions=hm_questions)


@app.route("/vak_test",  methods=["GET", "POST"])
@login_required
def vak_test():

    # Questions are stored in file and rendered to the HTML template
    file_vak = open("static/vak_test.csv", "r")
    vak_questions = csv.DictReader(file_vak, delimiter=";")

    if request.method == "POST":

        # Calculate result
        v = 0
        a = 0
        k = 0

        vak_data=str(request.get_data())

        for letter in vak_data:
            if letter == "v":
                v+=1
            elif letter == "a":
                a+=1
            elif letter == "k":
                k+=1

        # Draw distribution diagram
        pie_chart = pygal.Pie(inner_radius=.4, style=custom_style)
        pie_chart.title = 'VAK distribution'
        pie_chart.add('Auditory', a)
        pie_chart.add('Kinaesthetic', k)
        pie_chart.add('Visual', v)
        pie_chart.render_to_file('static/pies/vak_pie{}.svg'.format(session['user_id']))

        # Update user data
        db.execute("UPDATE users SET vak = 'yes' WHERE id = :id", id = session["user_id"])

        return redirect("/my_results")

    else:
        return render_template("vak_test.html", vak_questions=vak_questions)


@app.route("/my_results")
@login_required
def my_results():

    vak_type = db.execute("SELECT vak FROM users WHERE id = :id", id = session["user_id"])
    hm_type = db.execute("SELECT hm FROM users WHERE id = :id", id = session["user_id"])

    return render_template("my_results.html", id = session["user_id"], hm_type = hm_type[0]["hm"], vak_type = vak_type[0]["vak"])


@app.route("/email",  methods=["GET", "POST"])
@login_required
def email():

    adress=db.execute("SELECT email FROM users WHERE id=:id", id=session["user_id"])
    subject=adress[0]["email"]

    if request.method == 'POST':

        # Form and send email
        msg = Message(subject="Email from " + subject,
                      sender=os.environ.get('MAIL_USERNAME'),
                      recipients=["kriald@ism.lt"],
                      body=request.form.get("message"))
        mail.send(msg)

        return redirect("/home")

    else:
        return render_template("email.html")

@app.route("/logout")
def logout():

    # Forget any user_id
    session.clear()

    return redirect("/")


def errorhandler(e):
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    flash(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

if __name__ == "__application__":
    app.run(debug=True)