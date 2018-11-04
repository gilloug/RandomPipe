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
import hashlib, binascii
import os
from base64 import b64encode

def create(db, username, password):
    """
    Takes a username (string) and a password (string)
    Generates a new user in the database if it does not already exist
    return the resulting document containing the status (acknowledged)
    and the new id (insertedId)
    """
    if get(db, username):
        return None
    users = db.users
    salt = b64encode(os.urandom(16))
    dk = hashlib.pbkdf2_hmac('sha512', password.encode(), salt, 100000)
    binascii.hexlify(dk)
    user = {
        'username': username,
        'password': dk,
        'salt': salt
    }
    return users.insert_one(user)


def delete(db, username):
    """
    Delete the given user if it exist
    """
    if not get(db, username):
        return None
    users = db.users
    user = get(db, username)
    return users.delete_one({"username": username})


def get(db, username, password=None):
    """
    Return the user that correspond to the username given as parameter
    """
    user = db.users.find_one({"username":username})
    if not password:
        return user
    else:
        salt = user.get("salt", None)
        if not salt:
            return None
        dk = hashlib.pbkdf2_hmac('sha512', password.encode(), salt, 100000)
        binascii.hexlify(dk)
        if dk == user.get("password", ""):
            return user
        return None


def get_all(db):
    """
    Return all users actually in the database
    """
    users = db.users
    return users.find({})
