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

from googleapiclient.discovery import build


def is_pipe_playable(service, pipe_id):
    """
    Return True if the pipe contain all the data we need
    Else return False
    """
    if not get_pipe_data(service, pipe_id):
        return False
    else:
        return True


def get_pipe_data(service, pipe_id):
    """
    Return a dict containing the Pipe title, the pipe icon and th pipe ID
    """
    response = service.videos().list(
        part="snippet,contentDetails,statistics",
        id=pipe_id
    ).execute()
    try:
        metadata = {
            "id": pipe_id,
            "title": response["items"][0]["snippet"]["title"],
            "icon": response["items"][0]["snippet"]["thumbnails"]["default"]["url"]
        }
    except:
        return None
    return metadata
