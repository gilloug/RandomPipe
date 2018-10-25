#! /bin/python

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
from flask import Flask
from flask import render_template

# Get your APIKEY at https://randomyoutube.net/api
API_KEY = "XXX" #TODO Put here yout api key
APP_URL = "XXX" #TODO Put here your app url

def create_app():
    """
    Create and configure the app
    """
    app = Flask(__name__, instance_relative_config=True, static_url_path='')
    app.config.from_mapping(
        SECRET_KEY='XXX', #TODO Put here your app secret key
    )

    @app.route('/')
    def index():
        """
        Render our index page
        This is our only page, it contain:
        - The iframe with the random youtube video
        - A next button which reload the page
        """
        url = "https://randomyoutube.net/api/getvid?api_token={}".format(API_KEY)
        opened_url = urllib.request.urlopen(url)
        data = opened_url.read()
        encoding = opened_url.info().get_content_charset('utf-8')
        json_data = json.loads(data.decode(encoding))
        return render_template(
            'index.html',
            vid=json_data.get("vid", ""),
            autoplay="1", # When set to "1", the video autoplay
            loop="1", # When set to "1" the vido restart at the end
            app_url=APP_URL # URL used to reload the page
        )

    return app
