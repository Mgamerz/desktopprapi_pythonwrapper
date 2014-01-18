Getting Started
***********************************

*************
Prerequesites
*************
Getting started with the Desktoppr API wrapper is easy. All you need is Python3 and the requests library.

If you aren't sure if you have requests, you can check by starting the python interpreter you're going to use and importing the requests module. If you get the following error below, you don't have the requests module installed::

    $ python3
    Python 3.2.3 (default, Sep 25 2013, 18:22:43) 
    [GCC 4.6.3] on linux2
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import requests
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    ImportError: No module named requests
    >>> 

You can install requests like this if you don't have it::

   $ pip install requests

You may need to use your specific python's pip version if it defaults to a different version than the one you want::

   $ pip3.3 install requests

API Authorization
=================
To interact with the site as a user you will need to to make an account on the Desktoppr.co website. This will allow you to like and sync wallpapers, flag wallpapers, as well as other user-based tasks. If you aren't going to interact as a user, you won't need to authorize.s