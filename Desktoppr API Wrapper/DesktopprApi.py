'''
Created on Jan 13, 2014

@author: Mgamerz
         wegry
'''
import urllib.parse
import requests
import logging
import getpass

from requests.auth import HTTPBasicAuth

#Uncomment the following line to show debugging information
logging.getLogger().setLevel(logging.INFO)

class DesktopprAPI:
    __version__ = '0.9'
    '''
    This class allows you to create an object that allows you to query the desktoppr site using their public api.
    '''
    baseurl = 'https://api.desktoppr.co/1/'
    apikey = None
    authed_user = None

    def authorize_API(self, apikey):
        '''Authorizes using a users api key. This does not require the user's
        password or username.
        '''
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
        '''Gets a privileged access key by authorizing to the site with a username/
        password. Stores the users API key for further privileged access in this
        session.
        '''
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
        '''Get information about a user.

        Returns None if the request did not return user information.
        Returns a User object describing a specific user if successful.

        @param username: User to query for information
        '''
        requesturl = '{}users/{}'.format(self.baseurl, username)
        try:
            response = requests.get(requesturl, headers={'Connection': 'close'}).json()['response']
        except Exception as e:
            #Put a logging message here
            logging.info('Error retrieving information for user {}: {}'.format(username, e))
            return None
        return User(response)

    def get_user_collection(self, username, page=1):
        '''Gets a list of Wallpapers defining ones in a users collection.

        This command returns a Page object, as the results of this command are paginated on the server.
        Access the list of wallpapers via result.wallpapers.

        Returns None if an error occurs (no wallpapers, invalid user...)
        Returns a list of Wallpapers if it succeeds.

        @param username: User to query for information
        '''
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
        '''Retrieves a list of wallpapers.
        The page parameter can query different pages of results.
        The safefilter can return different levels of images:
        safe = Safe for work
        include_pending = Images not yet marked as safe or not safe for work (NSFW)
        all = All images, including NSFW images

        Returns None if a bad safefilter is passed (if any) or there was an error getting wallpapers.
        Returns a Page object containing wallpaper objects in the wallpapers attribute if successful.
        '''
        if safefilter != 'safe' and safefilter != 'include_pending' and safefilter != 'all':
            logging.info(
                'Unknown filter:',
                safefilter,
                'Valid options are safe, include_pending, all')
            return
        query = {'page': str(page), 'safe_filter': safefilter}
        requesturl = '{}/wallpapers'.format((self.baseurl))
        response = requests.get(requesturl, params=query, headers={'Connection': 'close'})
        if response.status_code == 200:
            # Build wallpaper object
            wallpapers = []
            json = response.json()['response']
            for paperinfo in json:
                wallpaper = Wallpaper()
                for key in paperinfo:
                    setattr(wallpaper, key, paperinfo[key])
                wallpapers.append(wallpaper)
            return wallpapers
        else:
            logging.info('Error getting wallpapers:', response.status_code)
            return

    def get_wallpaper_urls(self, page=1, safefilter='safe'):
        '''This is a subset of get_wallpapers(), which returns a page of wallpaper URLs. The API does not document sorting options.
        It uses the same interface as get_wallpapers.

        Returns a list of wallpaper URLs as strings.
        '''
        if safefilter != 'safe' and safefilter != 'include_pending' and safefilter != 'all':
            logging.warning(
                'Unknown filter: {}. Valid options are safe, include_pending, all'.format(safefilter))
            return None

        wallpapers = self.get_wallpapers(page, safefilter)
        urls = []
        if wallpapers:
            for wallpaper in wallpapers:
                urls.append(wallpaper.url)
        return urls

    def get_user_followers(self, username, page=1):
        '''Fetches a list of users who follow this user.
        Returns None if the user has no followers, cannot be found, or an error occurs.
        Returns a list of User objects otherwise.'''
        requesturl = '{}users/{}/followers'.format(self.baseurl,username)
        query = {'page':page}
        r = requests.get(requesturl, params=query, headers={'Connection': 'close'})
        if r.status_code==200:
            users = []
            userlist = r.json()['response']
            for user in userlist:
                users.append(user)
            return users
        else:
            logging.info('Unable to retrieve followers: {}'.format(r.status_code))
            return None

    def get_followed_users(self, username, page=1):
        '''Gets a list of User objects who the specified user follows..
        Returns None if the user follows noone, the user cannot be found, or an error occurs.
        Returns a list of User objects otherwise.'''
        requesturl = '{}users/{}/following'.format(self.baseurl, username)
        query={'page': page}
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
        '''Fetches a random wallpaper a user has in their collection.
        Returns a Wallpaper object if successful.
        Return None if it can't retrieve a wallpaper.'''
        requesturl = '{}users/{}/wallpapers/random'.format(self.baseurl, username)
        r = requests.get(requesturl, headers={'Connection': 'close'})
        if r.status_code == 500 or r.status_code == 404:
            #error occurred
            logging.info('Status code:{}', r.status_code)
            return None
        wallpaper = Wallpaper(r.json()['response'])
        return wallpaper

    def get_random_wallpaper(self, safefilter='safe'):
        '''Retrieves a random wallpaper.

        The safefilter parameter can return different levels of images:
        safe = Safe for work [Default]
        include_pending = Images not yet marked as safe or not safe for work (NSFW)
        all = All images, including NSFW images

        Returns None if a bad safefilter is passed (if any) or there was an error getting a wallpaper.
        Returns a Wallpaper object if successful.
        '''
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
        '''This method is privileged. You must authorize before using it.
        Attempts to follow a user.
        Returns None if the you haven't authorized against the server yet.
        Returns True if the follow attempt succeeded.
        Returns False if the follow attempt failed.'''
        return self._update_follow(username,'follow')

    def unfollow_user(self, username):
        '''This method is privileged. You must authorize before using it.
        Attempts to unfollow a user.
        Returns None if the you haven't authorized against the server yet.
        Returns True if the unfollow attempt succeeded.
        Returns False if the unfollow attempt failed.'''
        return self._update_follow(username,'unfollow')

    def _update_follow(self,username,action):
        '''Internal method to handle follow/unfollow requests'''
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
        '''This is a privileged method. You must authorize before you can use it.
        Likes a wallpaper.
        Returns None if the you haven't authorized against the server yet.
        Returns True if the like succeeded.
        Returns  False if the like attempt failed.'''
        return self.__update_like(wallpaper_id, 'like')

    def unlike_wallpaper(self, wallpaper_id):
        '''This is a privileged method. You must authorize before you can use it.
        Unlikes a wallpaper.
        Returns None if the you haven't authorized against the server yet.
        Returns True if the like succeeded.
        Returns  False if the like attempt failed.'''
        return self.__update_like(wallpaper_id, 'unlike')

    def __update_like(self, wallpaper_id, action):
        '''Internal method to handle like/unlike requests'''
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
            if r.status_code == 200 or r.status_code==404: #unsync checks against your dropbox folder. If it 404's, the file is already unsynced.
                return True
        return False

    def check_if_liked(self, username, wallpaper_id):
        '''Checks if a user has liked a wallpaper.

        @param username: Username to check for liking a wallpaper
        @param wallpaper_id: Wallpaper to check if the user likes it

        Returns None if an error occurs (user doesn't exist, etc).
        Returns True if the user has liked the wallpaper.
        Returns False if the user hasn't liked the wallpaper.'''
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
        '''Gets a list of wallpapers that a user likes.

        @param username: Username to get list of liked wallpapers for
        @param page: Optional, return different list of pages. Defaults to 1.

        Returns None if an error occurs (not a user, etc).
        Returns a Page object if successful. Wallpapers the user likes can be accessed via the .wallpapers attribute.
        '''

        query = {'page': page}
        r = requests.get('{}users/{}/likes'.format(self.baseurl, username), params=query, headers={'Connection': 'close'})
        if r.status_code != 200:
            logging.info('Error retrieving liked status:{}', r.status_code)
            return None
        return Page('wallpapers', r.json())
        #likes = r.json()['response']
        #ret
        '''
        wallpapers = []
        for like in likes:
            wallpapers.append(Wallpaper(like))
        return wallpapers'''

    def sync_wallpaper(self,wallpaper_id):
        '''This is a privileged method. You must authorize before you can use it.
        Informs the server that it should start a sync of a wallpaper to a user's dropbox.
        This checks against the server for wallpapers.
        Returns None if the you haven't authorized against the server yet.
        Returns True if a wallpaper was set to sync (or was already synced).
        Returns False if the HTTP response is not 200 or 422 (already synced)'''
        return self.__update_sync(wallpaper_id, 'sync')

    def unsync_wallpaper(self,wallpaper_id):
        '''This is a privileged method. You must authorize before you can use it.
        Informs the server that it should remove a wallpaper from a user's DropBox.
        This checks against the users DropBox for wallpapers.
        Returns None if the you haven't authorized against the server yet.
        Returns True if a wallpaper was set to unsync (or did not exist).
        Returns False if the HTTP response is not 200 or 404 (Not in user's DropBox)'''
        return self.__update_sync(wallpaper_id,'unsync')

    def __update_sync(self,wallpaper_id,action):
        '''Internal method to handle sync requests'''
        if action!='sync' and action!='unsync':
            logging.info('Internal error: Bad command for _update_sync: {}'.format(action))
            return None
        if not self.apikey:
            logging.warning(
                'ERROR: This is a user command. You must first authenticate as a user with authorize_user_pass() or authorize_API() method.')
            return None
        requesturl='{}user/wallpapers/{}/selection'.format(self.baseurl,wallpaper_id)
        auth={'auth_token':self.apikey}
        r = None
        if action=='sync':
            r = requests.post(requesturl,params=auth)
        else:
            r = requests.delete(requesturl,params=auth)
        if action=='sync' and (r.status_code==200 or r.status_code==422): #422 means its already synced
            return True
        else:
            if r.status_code==200 or r.status_code==404: #unsync checks against your dropbox folder. If it 404's, the file is already unsynced.
                return True
        return False

    def check_if_synced(self, username, wallpaper_id):
        '''Checks if a user has a wallpaper currently synced to their personal DropBox.
        The username is the user to check against.
        The wallpaper_id is the wallpaper to check for.
        Returns True if the wallpaper exists in the user's dropbox(since they linked it -
        if they unlink it, the server won't consider those synced anymore, even though they do on the website and the dropbox folder.)
        Returns False otherwise.'''
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
        '''Flags a wallpaper for filtering on the site.
        This is a privileged method. You must first authenticate with the authorize() methods before
        you can use this method.

        Returns None if the you haven't authorized against the server yet or if the flag is invalid.
        Returns True if the Wallpaper was successfully flagged.
        Returns False if the Wallpaper was not successfully flagged.
        @param wallpaper_id: integer id of the wallpaper.
        @param flag: Flag to place on a wallpaper. Valid options are flag_safe, flag_not_safe, and flag_deletion
        '''
        if flag!='flag_safe' and flag!='flag_not_safe' and flag!='flag_deletion':
            logging.info('ERROR: Flag must be flag_safe, flag_not_safe, or flag_deletion')
            return None
        if not self.apikey:
            logging.warning(
                'ERROR: This is a user command. You must first authenticate as a user with authorize_user_pass() or authorize_API() method.')
            return None
        requesturl = '{}wallpapers/{}/{}'.format(self.baseurl, wallpaper_id, flag)
        r = requests.post(requesturl, params={'auth_token': self.apikey}, headers={'Connection': 'close'})
        if r.status_code == 200:
            return True
        else:
            return False


class Page:
    '''A page object represents a 'page' of information returned by the API when it involves paginated information.
    It contains wallpaper objects or user objects.'''

    def __init__(self, infotype, info):
        self.wallpapers = None
        self.users = None

        if infotype != 'users' and infotype != 'wallpapers':
            logging.error('ERROR: Page object should have been passed either users or wallpapers, GOT: {}'.format(infotype))

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

        self.current_page = info['pagination']['current']
        self.previous_page = info['pagination']['previous']
        self.next_page = info['pagination']['next']
        self.per_page = info['pagination']['per_page']
        self.pages_count = info['pagination']['pages']
        self.items_on_page = info['count']


    def __str__(self):
        string = 'Page Object: '
        props = []
        for attr in dir(self):
            if not callable(attr) and not attr.startswith('__'):
                props.append('{}={}'.format(attr, str(getattr(self, attr))))
        return '{}{}'.format(string, str(props))


class Wallpaper:

    '''Items are put into this dynamically, and it has no methods.'''

    def __init__(self, info=None):
        '''Predefined wallpaper attributes. These are elements in the returned
        json response when querying for a wallpaper.'''

        #Set wallpaper defaults
        self.height = None
        self.created_at = None
        self.image = None
        self.url = None
        self.uploader = None
        self.user_count = None
        self.likes_count = None
        self.review_state = None
        self.bytes = None
        self.palette = None
        self.id = None
        self.width = None

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

class Image:
    '''Represents an image object (a part of a wallpaper object). It will either contain only a url or a url, width and height, and another Image object..
    Width and Height attributes signify that this is a preview or a thumbnail image.'''

    def __init__(self,info=None):
        self.thumb = None
        self.preview = None
        self.url = None
        self.width = None
        self.height = None

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