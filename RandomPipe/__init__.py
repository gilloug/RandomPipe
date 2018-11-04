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

import json
import urllib.request
from flask import Flask, request, session
from flask import render_template
from pymongo import MongoClient
from bson.objectid import ObjectId
from .classes import users, histories, youtube
from googleapiclient.discovery import build


with open('secrets.json', 'r') as f:
    secrets_dict = json.load(f)

API_KEY = secrets_dict["API_KEY"] #Get it at https://randomyoutube.net/api
APP_URL = secrets_dict["APP_URL"]
SERVICE = build(
    "youtube",
    "v3",
    developerKey=secrets_dict["DEVELOPER_KEY"] #Get it on the google console
)

CLIENT = MongoClient("mongodb", 27017)
DB = CLIENT.randompipe


def create_app():
    """
    Create and configure the app
    """
    app = Flask(__name__, instance_relative_config=True, static_url_path="")
    app.config.from_mapping(
        SECRET_KEY=secrets_dict["SECRET_KEY"],
    )

    @app.errorhandler(404)
    def page_not_found(error=None):
        """
        Display a Fancy 404 error to the user
        """
        return render_template('404.html'), 404


    @app.errorhandler(500)
    def page_not_found(error=None):
        """
        Display a Fancy 500 error to the user
        """
        return render_template('500.html'), 500


    @app.route('/login', methods=['POST', 'GET'])
    def login():
        """
        GET:  Display a form that the user can submit to login
        POST: Check the credentials and connect the user if they are correct
              Redirect the user to the application route "/"
        """
        if request.method == "GET":
            return render_template(
                'login.html',
                APP_URL=APP_URL,
                redirect=False,
                connected=session.get("connected", False),
            )
        elif request.method == "POST":
            message = None
            redirect = False
            user = users.get(
                DB,
                request.form["email"],
                request.form["password"]
            )
            if user:
                redirect = True
                session["connected"] = True
                session["username"] = request.form["email"]
            else:
                message = "Cannot login with this credentials"
            return render_template(
                'login.html',
                message=message,
                redirect=redirect,
                APP_URL=APP_URL,
                connected=session.get("connected", False),
            )


    @app.route('/logout', methods=['POST', 'GET'])
    def logout():
        """
        GET:  Display a button that the user can use to logout
        POST: Logout the current user
              Redirect him to the login page "/login"
        """
        if request.method == "GET":
            return render_template(
                'logout.html',
                APP_URL=APP_URL,
                redirect=False,
                connected=session.get("connected", False),
            )
        elif request.method == "POST":
            session["connected"] = False
            session["username"] = None
            return render_template(
                'logout.html',
                APP_URL=APP_URL,
                redirect=True,
                connected=session.get("connected", False),
            )


    @app.route('/sign_in', methods=['POST', 'GET'])
    def sign_in():
        """
        GET:  Display a form that the user can submit to sign in
        POST: Check the credentials and create the user if they are correct
              Redirect the user to the application login page "/login"
        """
        if request.method == "GET":
            return render_template(
                'sign_in.html',
                APP_URL=APP_URL
            )
        elif request.method == "POST":
            error = False
            message = None
            redirect = True
            username = request.form["email"]
            password = request.form["password"]
            password_check = request.form["password_check"]
            if password != password_check:
                error = True
                redirect = False
                message = "Error: passwords don't match each other."
            else:
                user = users.create(DB, username, password)
                if not user:
                    error = True
                    redirect = False
                    message = "Error: Cannot create user, maybe the email already in use."
            return render_template(
                'sign_in.html',
                APP_URL=APP_URL,
                redirect=redirect,
                error=error,
                message=message
            )


    @app.route('/')
    def index():
        """
        Play the pipe given as GET parameter if there is one,
        Play a random pipe if not
        """
        pipe_id = request.args.get("pipe_id", None)
        if not pipe_id or not youtube.is_pipe_playable(SERVICE, pipe_id):
            while True:
                url = "https://randomyoutube.net/api/getvid?api_token={}".format(API_KEY)
                opened_url = urllib.request.urlopen(url)
                data = opened_url.read()
                encoding = opened_url.info().get_content_charset('utf-8')
                json_data = json.loads(data.decode(encoding))
                pipe_id = json_data.get("vid", "")
                if youtube.is_pipe_playable(SERVICE, pipe_id):
                    if session.get("connected", None) and session.get("username", None):
                        histories.add(DB, SERVICE, session["username"], json_data.get("vid", ""))
                    break
        return render_template(
            'index.html',
            vid=pipe_id,
            autoplay=1,
            loop=1,
            APP_URL=APP_URL,
            connected=session.get("connected", False)
        )


    @app.route('/history')
    def history():
        """
        Display the list of pipes seen by the user
        Play icon: Let the user watch them again
        Trash icon: Let the user delete the pipe from his history
        Star icon: Let the user mark a pipe as favorite
        """
        if session.get("connected", None) and session.get("username", None):
            pipes = histories.get_all(DB, session["username"])
            res = []
            for pipe in pipes:
                tmp = {}
                tmp["date"] = pipe.get("date", "")
                tmp["username"] = pipe.get("username", "")
                tmp["pipe_id"] = pipe.get("pipe_id", "")
                tmp["appreciation"] = pipe.get("appreciation", 0)
                tmp["id"] = pipe.get("_id", 0)
                tmp["icon"] = pipe.get("icon", None)
                tmp["title"] = pipe.get("title", None)
                res.append(tmp.copy())
                pipes = sorted(res, key=lambda k: k["date"], reverse=True)
        else:
            pipes = None
        return render_template(
            'history.html',
            connected=session.get("connected", False),
            APP_URL=APP_URL,
            pipes=pipes
        )


    @app.route('/favorites')
    def favorites():
        """
        #TODO
        """
        if session.get("connected", None) and session.get("username", None):
            pipes = histories.get_favorites(DB, session["username"])
        else:
            pipes = None
        return render_template(
            'favorites.html',
            connected=session.get("connected", False),
            APP_URL=APP_URL,
            pipes=pipes
        )



    @app.route('/upvote', methods=['POST'])
    def upvote():
        """
        Upvote the given pipe from the current user
        by setting its appreciation to 1
        """
        _id = request.form.get("_id", "")
        res = histories.upvote(DB, ObjectId(_id))
        data = {}
        data["_id"] = _id
        if res:
            data["appreciation"] = 1
            response = app.response_class(
                response=json.dumps(data),
                status=200,
                mimetype='application/json'
            )
        else:
            data["appreciation"] = 0
            response = app.response_class(
                response=json.dumps(data),
                status=403,
                mimetype='application/json'
            )
        return response


    @app.route('/downvote', methods=['POST'])
    def downvote():
        """
        Downvote the given pipe from the current user
        by setting its appreciation to 0
        """
        _id = request.form.get("_id", "")
        res = histories.downvote(DB, ObjectId(_id))
        data = {}
        data["_id"] = _id
        if res:
            data["appreciation"] = 0
            response = app.response_class(
                response=json.dumps(data),
                status=200,
                mimetype='application/json'
            )
        else:
            data["appreciation"] = 1
            response = app.response_class(
                response=json.dumps(data),
                status=403,
                mimetype='application/json'
            )
        return response


    @app.route('/delete_pipe', methods=['POST'])
    def delete_pipe():
        """
        Delete the given pipe from the database
        """
        _id = request.form.get("_id", None)
        histories.delete(DB, session.get("username", None), ObjectId(_id))
        data = {}
        data["_id"] = _id
        response = app.response_class(
            response=json.dumps(data),
            status=200,
            mimetype='application/json'
        )
        return response


    return app
