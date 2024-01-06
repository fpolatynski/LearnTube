from flask import session, redirect
from functools import wraps
from pytube import YouTube
from googleapiclient.discovery import build
from key import api_key
from typing import List, Dict
import json


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
            """, (yt.watch_url, yt.embed_url+"?rel=0", session['user_id'], yt.title, yt.length, yt.thumbnail_url))
    con.commit()


def search_yt_films(que: str):
    service = build('youtube', 'v3', developerKey=api_key)
    request = service.search().list(
        part="snippet",
        q=que,
        type="video",
        videoEmbeddable='true',
        videoSyndicated='true'
    )
    response = request.execute()
    dict_films = response["items"]
    return [{'title': x['snippet']['title'],
             'thumbnails': x['snippet']['thumbnails']['default']['url'],
             'id': x['id']['videoId']} for x in dict_films]




