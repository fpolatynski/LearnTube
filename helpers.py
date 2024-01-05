from flask import session, redirect
from functools import wraps
from pytube import YouTube


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


def save_yt(link: str, cur, con):
    yt = YouTube(link)
    cur.execute("""
                INSERT INTO films (link, embed_link, user_id, title, length, thumbnail)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (yt.watch_url, yt.embed_url, session['user_id'], yt.title, yt.length, yt.thumbnail_url))
    con.commit()

