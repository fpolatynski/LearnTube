from flask import Flask, session, render_template, request, redirect
from flask_session import Session
import sqlite3
from helpers import login_required, save_yt
from werkzeug.security import check_password_hash, generate_password_hash

# initiate app
app = Flask(__name__)

# Configure session to filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# CONFIGURE DB
# set conection
con = sqlite3.connect("learnTube.db", check_same_thread=False)
# set cursor
cur = con.cursor()
# create users db
cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT,
        hash TEXT
    );
""")
# create films db
cur.execute("""
    CREATE TABLE IF NOT EXISTS films (
        id INTEGER PRIMARY KEY,
        link TEXT,
        embed_link TEXT,
        user_id INTEGER,
        title TEXT,
        length INTEGER,/* in seconds*/
        thumbnail TEXT,
        FOREIGN KEY (user_id) REFERENCES  users(id)
    );
""")


@app.route("/")
@login_required
def index():
    row = cur.execute("""
        SELECT embed_link FROM films
        WHERE user_id=?
    """, (session['user_id'],))
    films = row.fetchall()
    print(films)
    return render_template("index.html", films=films)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form.get("username")
        password = request.form.get("password")
        # TODO: Check if user provides valid inputs
        # select username and password from db
        rows = cur.execute("""
            SELECT id, username, hash FROM users
            WHERE username=?;
        """, (name,))
        row = rows.fetchone()
        if check_password_hash(row[2], password):
            session["user_id"] = row[0]
            return redirect("/")
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("username")
        password = request.form.get("password")
        # TODO: check for inputs
        cur.execute("""
            INSERT INTO users (username, hash)
            VALUES (?, ?)
        """, (name, generate_password_hash(password)))
        con.commit()
        return redirect("/login")
    return render_template("register.html")


@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect("/login")


@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    if request.method == "POST":
        # TODO: check if input is valid
        save_yt(request.form.get("link"), cur, con)

        return redirect("/")
    return render_template("add.html")


if __name__ == '__main__':
    app.run(debug=True, port=8000)

