#! /bin/python3

'''
----------------------------------------------------------------------------
 "THE BEER-WARE LICENSE" (Revision 42):
 <github@thamin.ovh> wrote this file.  As long as you retain this notice you
 can do whatever you want with this stuff. If we meet some day, and you think
 this stuff is worth it, you can buy me a beer in return.
 Guillaume Gilloux
----------------------------------------------------------------------------
'''

from pymongo import MongoClient
import os
import arrow
from . import youtube

def add(db, service, username, pipe_id):
    """
    Add a entry to the user history with the current date and the pipe id
    """
    histories = db.histories
    history = get(db, username, pipe_id)
    if not history or history.count() < 1:
        metadata = youtube.get_pipe_data(service, pipe_id)
        history = {
            "username": username,
            "pipe_id": pipe_id,
            "date": arrow.utcnow().format('DD-MM-YYYY HH:mm:ss ZZ'),
            "appreciation": 0,
            "icon": metadata.get("icon", None),
            "title": metadata.get("title", None),
        }
        return histories.insert_one(history)
    else:
        return history

def delete(db, username, _id):
    """
    Delete the given pipe from the user history
    """
    histories = db.histories
    return histories.delete_one({"_id": _id})


def get(db, username, pipe_id):
    """
    Return all occurence of a pipe in the user history
    """
    histories = db.histories
    return histories.find({"username": username, "pipe_id": pipe_id})


def get_favorites(db, username):
    """
    Return the favorites pipes from the current user
    """
    history = get_all(db, username)
    res = []
    for pipe in history:
        if pipe.get("appreciation", 0) > 0:
            tmp = {}
            tmp["date"] = pipe.get("date", "")
            tmp["username"] = pipe.get("username", "")
            tmp["pipe_id"] = pipe.get("pipe_id", "")
            tmp["appreciation"] = pipe.get("appreciation", 0)
            tmp["id"] = pipe.get("_id", 0)
            tmp["icon"] = pipe.get("icon", None)
            tmp["title"] = pipe.get("title", None)
            res.append(tmp.copy())
    return sorted(res, key=lambda k: k["date"], reverse=True)


def get_all(db, username):
    """
    Return all pipes from the user history
    """
    histories = db.histories
    return histories.find({"username": username})


def upvote(db, _id):
    """
    Set the given pipe appreciation to 1
    """
    histories = db.histories
    history = histories.find_one({"_id": _id})
    history["appreciation"] = 1
    return histories.update_one({"_id":_id}, {"$set": history}, upsert=False)


def downvote(db, _id):
    """
    Set the given pipe appreciation to 0
    """
    histories = db.histories
    history = histories.find_one({"_id": _id})
    history["appreciation"] = 0
    return histories.update_one({"_id":_id}, {"$set": history}, upsert=False)
