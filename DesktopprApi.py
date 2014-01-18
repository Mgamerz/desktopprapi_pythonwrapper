"""
.. :platform: Unix, Windows, Mac OSX
.. :synopsis: Contains methods for easily interacting with the Desktoppr.co public API.

.. moduleauthor:: Michael Perez (Mgamerz) <developer.mgamerzproductions@gmail.com>
.. moduleauthor:: wegry
"""
import requests
import logging

from requests.auth import HTTPBasicAuth

#Uncomment the following line to show debugging information
logging.getLogger().setLevel(logging.INFO)

class DesktopprAPI:
    """
    This class allows you to create an object that allows you to query the desktoppr site using their public api.
    """
    __version__ = '0.9'
    baseurl = 'https://api.desktoppr.co/1/'
    apikey = None #: Stored API key for the session. It is set when an authorize method succeeds.
    authed_user = None #: Stored username for the authorized user. It is set when an authorize method succeeds.

    def authorize_API(self, apikey):
        """Authorizes using a users api key. This does not require the user's
        password or username.

        :param apikey: The api key for your user account. Successfully authorizing will store this key in the field
            self.apikey.
        :type apikey: str
        :returns: * **True** -- if the authorization worked with the given apikey.
            * **False** -- if the authorization did not work with the given apikey.
        """
        query = {'auth_token': apikey}
        requesturl = '{}user/whoami'.format(self.baseurl)
        r = requests.get(requesturl, params=query, headers={'Connection': 'close'})
        if r.status_code == 200:
            self.apikey = apikey
            self.authed_user = r.json()['response']['username']
            logging.info('Authenticated as {}'.format(self.authed_user))
            return True
        else:
            logging.info('Error authorizing via API key: {}'.format(r.status_code))
            return False

    def authorize_user_pass(self, username, password):
        """Gets a users api key by authorizing to the site with a username/
        password. Stores the users API key in the field self.apikey for further privileged access in this
        object's session.

        :param username: Username to login with.
        :type username: str
        :param password: User's password. You should take steps to secure the entry of this argument.
        :type password: str

        :returns: * **True** -- if the authorization worked with the given username/password. The API key of the user is now cached.
            * **False** -- if the authorization did not work with the given username/password.

        """
        r = requests.get(
            'https://api.desktoppr.co/1/user/whoami',
            auth=HTTPBasicAuth(
                username,
                password), headers={'Connection': 'close'})
        if r.status_code == 200:
            json = r.json()['response']
            self.apikey = json['api_token']
            self.authed_user = json['username']
            logging.info('Authenticated, storing API token')
            return True
        else:
            return False

    def get_user_info(self, username):
        """Get information about a user.

        :param username: User to query for information
        :type username: str

        :returns: * **None** if the request did not return user information.
            * :class:`User` object -- if the command succeeds. The user object's attributes can be parsed for desired information.

        """
        requesturl = '{}users/{}'.format(self.baseurl, username)
        try:
            response = requests.get(requesturl, headers={'Connection': 'close'}).json()['response']
        except Exception as e:
            #Put a logging message here
            logging.info('Error retrieving information for user {}: {}'.format(username, e))
            return None
        return User(response)

    def get_user_collection(self, username, page=1):
        """Gets a page of wallpapers defining ones in a users collection. The default page is 1.

        :param username: User to query for information
        :type username: str
        :param page: *Optional*, the page number to return. The number of results per page is limited by the server.
        :type page: int

        :returns: * **None** -- if an error occurs (no wallpapers, invalid user...)
            * :class:`Page` object -- if the command succeeds. The page object's wallpapers attribute is populated \
        with the list of wallpapers the user has in their collection.
        """
        query = {'page': page}
        requesturl = '{}users/{}/wallpapers'.format(self.baseurl, username)
        r = requests.get(requesturl, params=query, headers={'Connection': 'close'})
        if r.status_code != 200:
            logging.info('Abnormal response code when retrieving user collection: {}'.format(r.status_code))
            return None
        page = Page('users', r.json())
        wallpapers = r.json()['response']
        #userpapers = []
        if wallpapers:
            return Page('wallpapers', r.json())
            #for wallpaper in wallpapers:
            #    userpapers.append(Wallpaper(wallpaper))
            #return userpapers
        else:
            logging.info('User has no wallpapers.')
            return None

    def get_wallpapers(self, page=1, safefilter='safe'):
        """Retrieves a list of wallpapers.
        The page parameter can query different pages of results.

        The safefilter can return different levels of images::

            safe = Safe for work
            include_pending = Images not yet marked as safe or not safe for work (NSFW)
            all = All images, including NSFW images

        :param page: *Optional*, page of results to retrieve.
        :type page: int
        :param safefilter: Safety filter for returned images. Valid strings are **safe**, **include_pending**, and **all**.
        :type safefilter: str


        :returns: * **None** if a bad safefilter is passed (if any) or there was an error getting wallpapers.
            * :class:`Page` object -- if the command succeeds. The page object's wallpapers attribute is populated \
        with the list of wallpapers the returned by the server.

        """
        if safefilter != 'safe' and safefilter != 'include_pending' and safefilter != 'all':
            logging.info(
                'Unknown filter:',
                safefilter,
                'Valid options are safe, include_pending, all')
            return
        query = {'page': str(page), 'safe_filter': safefilter}
        requesturl = '{}/wallpapers'.format(self.baseurl)
        response = requests.get(requesturl, params=query, headers={'Connection': 'close'})
        if response.status_code == 200:
            # Build wallpaper object
            wallpapers = []
            json = response.json()['response']
            for paperinfo in json:
                wallpapers.append(Wallpaper(paperinfo))
            return wallpapers
        else:
            logging.info('Error getting wallpapers:', response.status_code)
            return None

    def get_wallpaper_urls(self, page=1, safefilter='safe'):
        """This is a subset of get_wallpapers(), which returns a page of wallpaper URLs. The API does not document \
        sorting options.
        It uses the same interface as get_wallpapers.

        :param page: *Optional*, page number to return. The server limits how many results are returned by query, so
            pages allow you to sift through results.
        :type page: int
        :param safefilter: Safety filter for returned images. Valid strings are **safe**, **include_pending**, and **all**.
        :type safefilter: str

        :return: * :class:`Page` object -- if the command succeeds. The page object's wallpapers attribute is \
        populated with the list of wallpapers.
             * **None** -- If an error occurs trying to get wallpapers.
        """
        if safefilter != 'safe' and safefilter != 'include_pending' and safefilter != 'all':
            logging.warning(
                'Unknown filter: {}. Valid options are safe, include_pending, all'.format(safefilter))
            return None

        wallpapers = self.get_wallpapers(page, safefilter)
        urls = []
        if wallpapers:
            for wallpaper in wallpapers:
                urls.append(wallpaper.image.url)
        return urls

    def get_user_followers(self, username, page=1):
        """Gets a :class:`Page` contains a list of of :class:`User` objects representing users who follow this user.
        The pages can be iterated over to find all followers.

        :param username: Username to query.
        :type username: str
        :param page: Page of results to return
        :type page: int

        :returns: * **None** -- if the user has no followers, cannot be found, or an error occurs.
            * :class:`Page` object -- if the command succeeds. The page object's users attribute is populated \
        with the list of users.

        """
        requesturl = '{}users/{}/followers'.format(self.baseurl, username)
        query = {'page': page}
        r = requests.get(requesturl, params=query, headers={'Connection': 'close'})
        if r.status_code == 200:
            users = []
            userlist = r.json()['response']
            for user in userlist:
                users.append(user)
            return users
        else:
            logging.info('Unable to retrieve followers: {}'.format(r.status_code))
            return None

    def get_followed_users(self, username, page=1):
        """Gets a list of User objects who the specified user follows.

        :param username: Username to query.
        :type username: str

        :returns: * **None** -- if the user follows noone, the user cannot be found, or an error occurs.
            * :class:`Page` object -- if the command succeeds. The page object's username attribute is populated \
            with the list of users.

        """
        requesturl = '{}users/{}/following'.format(self.baseurl, username)
        query = {'page': page}
        r = requests.get(requesturl, params=query, headers={'Connection': 'close'})
        if r.status_code == 200:
            users = []
            userlist = r.json()['response']
            for user in userlist:
                users.append(User(user))
            return users
        else:
            logging.info('Unable to retrieve following list: {}'.format(r.status_code))
            return None

    def get_user_randomwallpaper(self, username):
        """Fetches a random wallpaper a user has in their collection.

        :param username: Username to get random wallpaper from
        :type username: str
        :returns: * **None** -- if a failure occurred trying to get a wallpaper
            * :class:`Wallpaper` object -- If successful.

        """
        requesturl = '{}users/{}/wallpapers/random'.format(self.baseurl, username)
        r = requests.get(requesturl, headers={'Connection': 'close'})
        if r.status_code == 500 or r.status_code == 404:
            #error occurred
            logging.info('Status code for URL {}: {}'.format(r.url, r.status_code))
            return None
        wallpaper = Wallpaper(r.json()['response'])
        return wallpaper

    def get_random_wallpaper(self, safefilter='safe'):
        """Retrieves a random wallpaper.

        The safefilter can return different levels of images::

            safe = Safe for work
            include_pending = Images not yet marked as safe or not safe for work (NSFW)
            all = All images, including NSFW images

        :param safefilter: Safety filter for returned images. Valid strings are **safe**, **include_pending**, and **all**.
        :type safefilter: str

        :returns: * **None** -- if a bad safefilter is passed (if any) or there was an error getting a wallpaper.
            * :class:`Wallpaper` object -- if successful.
        """
        if safefilter != 'safe' and safefilter != 'include_pending' and safefilter != 'all':
            logging.info(
                'Unknown filter:',
                safefilter,
                'Valid options are safe, include_pending, all')
            return
        requesturl = '{}/wallpapers/random'.format(self.baseurl)
        query = {'safe_filter': safefilter}
        r = requests.get(requesturl, params=query, headers={'Connection': 'close'})
        if r.status_code != 200:
            #error occurred
            logging.info('Error getting random wallpaper: {}', r.status_code)
            return None
        return Wallpaper(r.json()['response'])

        pass

    def follow_user(self, username):
        """
        Attempts to follow a user.

        .. warning::
            This is a privileged method. You must authorize with :func:`authorize_user_pass` or :func:`authorize_API`
            before you can use it.


        :param username: Username to follow
        :type username: str
        :returns: * **None** -- if the you haven't authorized against the server yet.
            * **True** -- if the follow attempt succeeded.
            * **False** -- if the follow attempt failed.

        """
        return self._update_follow(username, 'follow')

    def unfollow_user(self, username):
        """
        Attempts to unfollow a user.

        :param username: User to unfollow
        :type username: str
        :returns: * **None** -- if the you haven't authorized against the server yet.
            * **True** -- if the unfollow attempt succeeded.
            * **False** -- if the unfollow attempt failed.

        """
        return self._update_follow(username, 'unfollow')

    def _update_follow(self,username,action):
        """Internal method to handle follow/unfollow requests"""
        if not self.apikey:
            logging.warning(
                'ERROR: This is a user command. You must first authenticate as a user with authorize_user_pass() or authorize_API() method.')
            return None
        if action != 'follow' and action != 'unfollow':
            logging.info('Internal error: Bad command for _update_follow: {}'.format(action))
            return None
        r = None
        if action == 'follow':
            r = requests.post('{}users/{}/follow'.format(self.baseurl, username),
                                params={'auth_token': self.apikey}, headers={'Connection': 'close'})

            # if r.status_code!=200:
            #	print('Abnormal response following user',username,':',r.status_code)
        else:
            r = requests.delete('{}users/{}/follow'.format(self.baseurl, username),
                                params={'auth_token': self.apikey}, headers={'Connection': 'close'})
            # if r.status_code!=200:
            #	print('Abnormal response unfollowing user',username,':',r.status_code)
        if r.status_code == 200:
            return True
        else:
            return False

    def like_wallpaper(self,wallpaper_id):
        """
        .. warning::
            This is a privileged method. You must authorize with :func:`authorize_user_pass` or :func:`authorize_API`
            before you can use it.

        Likes a wallpaper.

        :param wallpaper_id: Wallpaper to like
        :type wallpaper_id: int
        :returns: * **None** -- if the you haven't authorized against the server yet.
            * **True** -- if the like succeeded.
            * **False** -- if the like attempt failed.

        """
        return self.__update_like(wallpaper_id, 'like')

    def unlike_wallpaper(self, wallpaper_id):
        """
        Unlikes a wallpaper.

        .. warning::
            This is a privileged method. You must authorize with :func:`authorize_user_pass` or :func:`authorize_API`
            before you can use it.

        :param wallpaper_id: Wallpaper to unlike
        :type wallpaper_id: int
        :returns: * **None** -- if the you haven't authorized against the server yet.
            * **True** -- if the unlike succeeded.
            * **  False** -- if the unlike attempt failed."""
        return self.__update_like(wallpaper_id, 'unlike')

    def __update_like(self, wallpaper_id, action):
        """
        Internal method to handle like/unlike requests

        You shouldn't need to call this.
        """
        if action != 'like' and action != 'unlike':
            logging.info('Internal error: Bad command for _update_like: {}'.format(action))
            return None
        if not self.apikey:
            logging.warning('ERROR: This is a user command. You must first authenticate as a user with authorize_user_pass() or authorize_API() method.')
            return None
        requesturl = '{}user/wallpapers/{}/like'.format(self.baseurl, wallpaper_id)
        auth = {'auth_token': self.apikey}
        r = None
        if action == 'like':
            r = requests.post(requesturl, params=auth, headers={'Connection': 'close'})
        else:
            r = requests.delete(requesturl, params=auth, headers={'Connection': 'close'})
        if action == 'like' and (r.status_code == 200 or r.status_code == 422): #422 means its already synced
            return True
        else:
            if r.status_code == 200 or r.status_code == 404: #unsync checks against your dropbox folder. If it 404's, the file is already unsynced.
                return True
        return False

    def check_if_liked(self, username, wallpaper_id):
        """Checks if a user has liked a wallpaper.

        :param username: Username to check for liking a wallpaper
        :type username: str
        :param wallpaper_id: Wallpaper to check if the user likes it
        :type wallpaper_id: int

        :returns: * **None** -- if an error occurs (user doesn't exist, etc).
            * **True**  -- if the user has liked the wallpaper.
            * **False** -- if the user hasn't liked the wallpaper.

        """
        query = {'wallpaper_id': wallpaper_id}
        r = requests.get('{}users/{}/likes'.format(self.baseurl, username), params=query, headers={'Connection': 'close'})
        if r.status_code != 200:
            logging.info('Error retrieving liked status:{}', r.status_code)
            return None
        liked = r.json()['response']
        #If the response content is empty, then the user doesn't like the wallpaper.
        if liked:
            return True
        else:
            return False

    def get_userlikes(self, username, page=1):
        """Gets a list of wallpapers that a user likes.

        :param username: Username to get list of liked wallpapers for
        :type username: str
        :param page: *Optional*, return different list of pages. Defaults to 1.
        :type page: int
        :returns: * **None** -- if an error occurs (not a user, etc).
            *  :class:`Page` object -- if successful. Wallpapers the user likes can be accessed via the .wallpapers attribute.
        """

        query = {'page': page}
        r = requests.get('{}users/{}/likes'.format(self.baseurl, username), params=query, headers={'Connection': 'close'})
        if r.status_code != 200:
            logging.info('Error retrieving liked status:{}', r.status_code)
            return None
        return Page('wallpapers', r.json())

    def sync_wallpaper(self, wallpaper_id):
        """
        Informs the server that it should start a sync of a wallpaper to a user's DropBox.
        This checks against the server for wallpapers.

        .. warning::
            This is a privileged method. You must authorize with :func:`authorize_user_pass` or :func:`authorize_API`
            before you can use it.

        :param wallpaper_id: The wallpaper id to sync to the authorized user's DropBox
        :type wallpaper_id: int
        :returns: * **None** -- if the you haven't authorized against the server yet.
            * **True** -- if a wallpaper was set to sync (or was already synced).
            * **False** -- if the HTTP response is not 200 or 422 (already synced)

        """
        return self.__update_sync(wallpaper_id, 'sync')

    def unsync_wallpaper(self, wallpaper_id):
        """
        Informs the server that it should remove a wallpaper from a user's DropBox.
        This checks against the user's DropBox for wallpapers, so if it doesn't exist there, it will still return **True**.

        .. warning::
            This is a privileged method. You must authorize with :func:`authorize_user_pass` or :func:`authorize_API`
            before you can use it.

        :param wallpaper_id: The wallpaper id to unsync from the authorized user's DropBox
        :type wallpaper_id: int
        :returns: * **None** if the you haven't authorized against the server yet.
            * **True** -- if a wallpaper was set to unsync (or did not exist).
            * **False** -- if the HTTP response is not 200 or 404 (Not in user's DropBox)

        """
        return self.__update_sync(wallpaper_id, 'unsync')

    def __update_sync(self, wallpaper_id, action):
        """Internal method to handle sync requests"""
        if action != 'sync' and action != 'unsync':
            logging.info('Internal error: Bad command for _update_sync: {}'.format(action))
            return None
        if not self.apikey:
            logging.warning(
                'ERROR: This is a user command. You must first authenticate as a user with authorize_user_pass() or authorize_API() method.')
            return None
        requesturl = '{}user/wallpapers/{}/selection'.format(self.baseurl, wallpaper_id)
        auth = {'auth_token': self.apikey}
        r = None
        if action == 'sync':
            r = requests.post(requesturl, params=auth, headers={'Connection': 'close'})
        else:
            r = requests.delete(requesturl, params=auth, headers={'Connection': 'close'})
        if action == 'sync' and (r.status_code == 200 or r.status_code == 422): #422 means its already synced
            return True
        else:
            if r.status_code == 200 or r.status_code == 404: #unsync checks against your dropbox folder. If it 404's, the file is already unsynced.
                return True
        return False

    def check_if_synced(self, username, wallpaper_id):
        """
        Checks if a user has a wallpaper currently synced to their personal DropBox.

        :param username: Username to check for wallpaper sync status on
        :type username: str
        :param wallpaper_id: Wallpaper to check if it is synced
        :type wallpaper_id: int


        :returns: * **True** -- if the wallpaper exists in the user's DropBox since their last relink to DropBox. \
        If a DropBox account is unlinked and relinked, all previous synced wallpapers are ignored, even if they \
        still reside in their DropBox folder.
            * **False** -- If the wallpaper is not synced, or if an error occurs.

        """
        query = {'wallpaper_id': wallpaper_id}
        r = requests.get('{}users/{}/wallpapers'.format(self.baseurl, username), params=query, headers={'Connection': 'close'})
        if r.status_code != 200:
            #A logging message will go here.
            logging.info('Error checking for synced wallpaper: {}'.format(r.status_code))
            return None
        try:
            synced = r.json()['count']
            if synced > 0:
                return True
            else:
                return False
        except:
            return None

    def flag_wallpaper(self, wallpaper_id, flag):
        """Flags a wallpaper for filtering on the site.

        .. warning::
            This is a privileged method. You must authorize with :func:`authorize_user_pass` or :func:`authorize_API`
            before you can use it.

        :param wallpaper_id: id of the wallpaper.
        :type wallpaper_id: int
        :param flag: Flag to place on a wallpaper. Valid options are **flag_safe**, **flag_not_safe**, and **flag_deletion**
        :type flag: str

        :returns: * **None** -- if the you haven't authorized against the server yet or if the flag is invalid.
            * **True** -- if the Wallpaper was successfully flagged.
            * **False** -- if the Wallpaper was not successfully flagged.

        """
        if flag != 'flag_safe' and flag != 'flag_not_safe' and flag != 'flag_deletion':
            logging.info('ERROR: Flag must be flag_safe, flag_not_safe, or flag_deletion')
            return None
        if not self.apikey:
            logging.warning(
                'ERROR: This is a user command. You must first authenticate as a user with authorize_user_pass() \
                or authorize_API() method.')
            return None
        requesturl = '{}wallpapers/{}/{}'.format(self.baseurl, wallpaper_id, flag)
        r = requests.post(requesturl, params={'auth_token': self.apikey}, headers={'Connection': 'close'})
        if r.status_code == 200:
            return True
        else:
            return False


class Page:
    """A page object represents a 'page' of information returned by the API when it involves paginated information.
    It contains either a list of :class:`Wallpaper` objects or a list of :class:`User` objects."""

    def __init__(self, infotype, info):
        self.wallpapers = None
        """List of :class:`Wallpaper` objects contained on this page. It is None if that is not what this page is \
        supposed to return."""

        self.users = None
        """List of :class:`User` objects contained on this page. It is None if that is not what this page is supposed \
            to return."""

        self.current_page = info['pagination']['current']
        """Index of the current page this object represents."""

        self.previous_page = info['pagination']['previous']
        """ The previous page of information. It can be None if there is no previous page."""

        self.next_page = info['pagination']['next']
        """ The next page of information. It can be None if there is no next page."""

        self.per_page = info['pagination']['per_page']
        """How many results this page can store. It should be the same across different page numbers from the query \
        that generated this page."""

        self.pages_count = info['pagination']['pages']
        """How many total pages of information are in the query that generated this page."""

        self.items_on_page = info['count']
        """How many pieces of information are on this page. This corresponds to the size of the :data:`wallpapers` \
         or :data:`users` list size. """


        if infotype != 'users' and infotype != 'wallpapers':
            logging.error('ERROR: Page object should have been passed either users or wallpapers indicator, \
                got: {}'.format(infotype))

        if infotype == 'users':
            userlist = []
            for user in info['response']:
                userlist.append(User(user))
            self.users = userlist
        if infotype == 'wallpapers':
            paperlist = []
            for paper in info['response']:
                paperlist.append(Wallpaper(paper))
            self.wallpapers = paperlist


    def __str__(self):
        string = 'Page Object: '
        props = []
        for attr in dir(self):
            if not callable(attr) and not attr.startswith('__'):
                props.append('{}={}'.format(attr, str(getattr(self, attr))))
        return '{}{}'.format(string, str(props))

class Wallpaper:

    """Items are put into this dynamically, and it has no methods."""

    def __init__(self, info=None):
        """Predefined wallpaper attributes. These are elements in the returned \
        json response when querying for a wallpaper."""

        #Set wallpaper defaults
        self.height = None
        """ Height of the full resolution image contained in the :attr:`image` attribute of this object."""

        self.created_at = None
        """Datestamp the file was uploaded."""

        self.image = None
        """ Image object that contains the image-file specific details, like resolution and URLs to the image."""

        self.url = None
        """URL to the Desktoppr.co page, where you can like and sync the wallpaper."""

        self.uploader = None
        """Username of uploader.

        .. warning::
            Do not assume this always exists. Users who have uploaded images but have deleted their account \
            will still have wallpapers on the site. This will cause some Wallpaper objects to have this field set \
            to None.

        """

        self.user_count = None
        """I am not sure what this field means."""

        self.likes_count = None
        """Number of likes this wallpaper currently has."""

        self.review_state = None
        """Current flag state of this wallpaper. Values in this field should be *safe*, *pending*, or *not_safe*. """

        self.bytes = None
        """Filesize of the full resolution image contained in the :data:`image` field."""

        self.palette = None
        """List of colors in the palette of the image... not exactly sure what this means."""

        self.id = None
        """ID for this wallpaper. This is the same as the one when normally browsing the site, located at the end of \
            the URL typically."""

        self.width = None
        """Width of the full resolution image contained in the :attr:`image` attribute of this object."""

        if info:
            #We are going to parse a new wallpaper json
            for attribute in info:
                if isinstance(info[attribute], dict):
                    #it's an image object.
                    setattr(self, attribute, Image(info[attribute]))
                    continue
                setattr(self, attribute, info[attribute])

    def __str__(self):
        string = 'Wallpaper object: '
        props = []
        for attr in dir(self):
            if not callable(attr) and not attr.startswith('__'):
                props.append('{}={}'.format(attr, str(getattr(self, attr))))
        return '{}{}'.format(string, str(props))

class User:
    '''Defines a user on the site.'''
    def __init__(self, info=None):
        '''Predefined user attributes. These are elements in the returned
        json response when querying for a user. If you pass an info dictionary
        (only if its a user from the site), it will automatically fill these values.'''

        self.uploaded_count = None
        self.followers_count = None
        self.username = None
        self.lifetime_member = None
        self.avatar_url = None
        self.wallpapers_count = None
        self.created_at = None
        self.following_count = None
        self.name = None

        #If an information package was included, create this user.
        if info:
            for attribute in info:
                #There are no dictionaries in the response for a user.
                setattr(self, attribute, info[attribute])

    def __str__(self):
        string = 'User object: '
        props = []
        for attr in dir(self):
            if not callable(attr) and not attr.startswith('__'):
                props.append('{}={}'.format(attr, str(getattr(self, attr))))
        return '{}{}'.format(string, str(props))

class Image(object):
    """
    Represents an image object (a part of a wallpaper object). All values are initialized to none, but are \
    set if an image dict is passed.

    An image object can contain another image object. There are only two different setups of an image object:

    * Contains thumb, preview, and url = **Full Resolution Image**
    * Contains width, height, and url = **Thumbnail or Preview Image**

    """

    def __init__(self, info=None):
        """

        :param info: Server's json representation of an image object. It is parsed and stored in this image object \
            so the user doesn't have to do try/catch with dictionaries.
        :type info: dict
        """

        self.thumb = None
        """Thumbnail version of this image object. It is None if it is a thumbnail or a preview image."""

        self.preview = None
        """Preview version of this image object. It is higher resolution than a thumbnail. It is None if it is a \
            thumbnail or a preview."""

        self.url = None
        """Direct URL to the image."""

        self.width = None
        """Width of the image. This is only supplied in the thumbnail and preview objects. The resolution of the full \
            resolution can be found in the containing :class:`Wallpaper` object. """

        self.height = None
        """Height of the image. This is only supplied in the thumbnail and preview objects. The resolution of the full \
            resolution can be found in the containing :class:`Wallpaper` object. """

        if info:
            #Parsing image package - it might be the top level one (full) or lower (preview/thumbnail)
            for attribute in info:
                if isinstance(info[attribute], dict):
                    setattr(self, attribute, Image(info[attribute]))
                    continue
                setattr(self, attribute, info[attribute])

    def __str__(self):
        string = None
        if self.width:
            string = 'Image [Thumbnail/Preview] Object: '
        if self.preview:
            string = 'Image [Full] Object: '
        props = []
        for attr in dir(self):
            if not callable(attr) and not attr.startswith('__'):
                props.append('{}={}'.format(attr, str(getattr(self, attr))))
        return '{}{}'.format(string, str(props))
