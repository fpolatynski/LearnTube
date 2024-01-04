from flask import session, redirect
from functools import wraps
import re


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def youtube_link_to_embed(link: str) -> str:
    x = re.sub("watch.v.", "embed/", link)
    return x





