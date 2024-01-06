from flask import Flask, session, render_template, request, redirect
from flask_session import Session
import sqlite3
from helpers import login_required, save_yt, search_yt_films
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


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method =="POST":
        ids = request.form.get("id")
        cur.execute("""
            DELETE FROM films
            WHERE id=?
        """, (ids,))
        con.commit()

    row = cur.execute("""
        SELECT id, embed_link FROM films
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
        url = request.form.get("link")
        search = request.form.get("search")
        id_to_add = request.form.get("to_add")
        if url:
            save_yt(request.form.get("link"), cur, con)
        if search:
            films = search_yt_films(search)
            return render_template("chose_film.html", films=films)
        if id_to_add:
            save_yt(f"https://www.youtube.com/watch?v={id_to_add}", cur, con)

    return render_template("add.html")


if __name__ == '__main__':
    app.run(debug=True, port=8000)

