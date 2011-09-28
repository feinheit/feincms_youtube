================================
Youtube feed content for FeinCMS
================================

Requirements
------------
To use this content type, you need the Gdata Python Client Library.
Download it here: http://code.google.com/p/gdata-python-client/downloads/list

Make a symlink to src/gdata and src/atom


Usage
-----
Check out http://googlesystem.blogspot.com/2008/01/youtube-feeds.html for
how to get the URL of the feeds.

Add your Youtube developer key to the settings file::

    YOUTUBE_DEV_KEY = "XXXX...........XXXX"
    YOUTUBE_CLIENT_ID = "any_string"
    

Youtube feeds are paginated after 25 objects. 
Since the content type doesn't support pagination yet you are basically limited to 25 videos per feed.