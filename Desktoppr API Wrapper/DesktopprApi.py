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


class DesktopprAPI:
	__version__ = '0.9'
	'''
	This class allows you to create an object that allows you to query the desktoppr site using their public api.
	'''
	baseurl = 'https://api.desktoppr.co/1/'
	apikey = None
	
	def authorize_API(self, apikey):
		'''Authorizes using a users api key. This does not require the user's 
		password or username.
		'''
		query = {'auth_token': apikey}
		requesturl = '{}user/whoami'.format(self.baseurl)
		r = requests.get(requesturl,params=query)
		if r.status_code == 200:
			logging.info('Authenticated as {}'.format(r.json()['response']['username']))
			self.apikey = apikey
			return True
		else:
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
				password))
		if r.status_code == 200:
			self.apikey = r.json()['response']['api_token']
			logging.info('Authenticated, storing API token')
			return True
		else:
			return False

	def get_user_info(self, username):
		'''Get information about a user.
		Returns None if the request did not return user information.
		Returns a User object describing a specific user if successful.'''
		query = 'users/' + username
		requesturl = self.baseurl + query
		response = None
		try:
			response = requests.get(requesturl).json()['response']
		except Exception as e:
			#Put a logging message here
			logging.info('Error retrieving information for user {}: {}'.format(username, e))
		return User(response)

	def get_user_collection(self, username):
		'''Returns a dictionary describing a specific users' collection of 
		wallpapers. The API documentation on this method is somewhat ambiguous.
		'''
		requesturl = '{}users/{}/wallpapers'.format(self.baseurl,username)
		response = None
		try:
			response = requests.get(requesturl).json()['response']
		except Exception as e:
			logging.info('Error retrieving wallpaper collection for user {}: {}'.format(username,e))
		return response

	def get_wallpapers(self, page=1, safefilter='safe'):
		'''Retrieves a list of wallpapers.
		The page parameter can query different pages of results.
		The safefilter can return different levels of images:
		safe = Safe for work
		include_pending = Images not yet marked as safe or not safe for work (NSFW)
		all = All images, including NSFW images
		
		Returns None if a bad safetyfilter is passed (if any) or there was an error getting wallpapers.
		Returns a list of Wallpaper objects if successful.
		'''
		if safefilter != 'safe' and safefilter != 'include_pending' and safefilter != 'all':
			logging.info(
				'Unknown filter:',
				safefilter,
				'Valid options are safe, include_pending, all')
			return
		query = {'page': str(page), 'safe_filter': safefilter}
		requesturl = '{}/wallpapers'.format((self.baseurl))
		response = requests.get(requesturl,params=query)
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

	def get_wallpapers_url(self, page=1, safefilter='safe'):
		'''This is a subset of get_wallpapers(), which returns a page of wallpaper URLs. The API does not document sorting options.
		It uses the same interface as get_wallpapers.
		'''
		if safefilter != 'safe' and safefilter != 'include_pending' and safefilter != 'all':
			print(
				'Unknown filter:',
				safefilter,
				'Valid options are safe, include_pending, all')
			return None

		wallpapers = self.get_wallpapers(page, safefilter)
		urls = []
		if wallpapers:
			for wallpaper in wallpapers:
				urls.append(wallpaper.image.url)
		return urls

	def get_user_followers(self, username, page=1):
		'''Fetches a list of users who follow this user.
		Returns None if the user has no followers, cannot be found, or an error occurs.
		Returns a list of User objects otherwise.'''
		requesturl = '{}users/{}/followers'.format(self.baseurl,username)
		query={'page':page}
		r = requests.get(requesturl,params=query)
		if r.status_code==200:
			users = []
			userlist = r.json()['response']
			for user in userlist:
				users.append(user)
			return users
		else:
			logging.info('Unable to retrieve followers: {}'.format(r.status_code))
			return None
	
	def get_followed_users(self,username,page=1):
		'''Gets a dictionary list of users a specific user follows.
		Returns None if the user follows noone, the user cannot be found, or an error occurs.
		Returns a list of User objects otherwise.'''
		requesturl = '{}users/{}/following'.format(self.baseurl,username)
		query={'page':page}
		r = requests.get(requesturl,params=query)
		if r.status_code==200:
			users = []
			userlist = r.json()['response']
			for user in userlist:
				users.append(user)
			return users
		else:
			logging.info('Unable to retrieve following list: {}'.format(r.status_code))
			return None
	def get_user_randomwallpaper(self, username):
		'''Fetches a random wallpaper a user has in their collection.
		Returns a Wallpaper object if successful.
		Return None if it can't retrieve a wallpaper.'''
		requesturl = '{}users/{}/wallpapers/random'.format(self.baseurl,username)
		r = requests.get(requesturl)
		if r.status_code == 500 or r.status_code == 404:
			#error occured
			print(r.url)
			print('Status code:{}',r.status_code)
			return None
		wallpaper = Wallpaper(r.json()['response'])
		return wallpaper

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
			logging.info(
				'ERROR: This is a user command. You must first authenticate as a user with authorize_user_pass() or authorize_API() method.')
			return None
		if action!='follow' and action!='unfollow':
			logging.info('Internal error: Bad command for _update_follow: {}'.format(action))
			return None
		r = None
		if action == 'follow':
			r = requests.post('{}users/{}/follow'.format(self.baseurl,username),
				params={'auth_token': self.apikey})

			# if r.status_code!=200:
			#	print('Abnormal response following user',username,':',r.status_code)
		else:
			r = requests.delete('{}users/{}/follow'.format(self.baseurl,username),
				params={'auth_token': self.apikey})
			# if r.status_code!=200:
			#	print('Abnormal response unfollowing user',username,':',r.status_code)
		if r.status_code==200:
			return True
		else:
			return False


	def like_wallpaper(self,wallpaper_id):
		'''This is a privileged method. You must authorize before you can use it.
		Likes a wallpaper.
		Returns None if the you haven't authorized against the server yet.
		Returns True if the like succeeded.
		Returns  False if the like attempt failed.'''
		return self.__update_like(wallpaper_id,'like')

	def unlike_wallpaper(self,wallpaper_id):
		'''This is a privileged method. You must authorize before you can use it.
		Unlikes a wallpaper.
		Returns None if the you haven't authorized against the server yet.
		Returns True if the like succeeded.
		Returns  False if the like attempt failed.'''
		return self.__update_like(wallpaper_id,'unlike')
	
	def __update_like(self,wallpaper_id,action):
		'''Internal method to handle like/unlike requests'''
		if action!='like' and action!='unlike':
			logging.info('Internal error: Bad command for _update_like: {}'.format(action))
			return None
		if not self.apikey:
			#print(
			#	'ERROR: This is a user command. You must first authenticate as a user with authorize_user_pass() or authorize_API() method.')
			return None
		requesturl='{}user/wallpapers/{}/like'.format(self.baseurl,wallpaper_id)
		auth={'auth_token':self.apikey}
		r = None
		if action=='like':
			r = requests.post(requesturl,params=auth)
		else:
			r = requests.delete(requesturl,params=auth)
		if action=='like' and (r.status_code==200 or r.status_code==422): #422 means its already synced
			return True
		else:
			if r.status_code==200 or r.status_code==404: #unsync checks against your dropbox folder. If it 404's, the file is already unsynced.
				return True
		return False

	def check_if_liked(self, username, wallpaper_id):
		'''Checks if a user has liked a wallpaper.
		Returns True if it is, False otherwise.'''
		query={'wallpaper_id':wallpaper_id}
		r = requests.get('{}users/{}/likes'.format(self.baseurl,username),params = query)
		print(r.url)
		if r.status_code!=200:
			logging.info('Error retrieving liked status:{}',(r.status_code))
		liked=r.json()['response']
		logging.info(liked)
		if liked:
			return True
		else:
			return False


	def sync_wallpaper(self,wallpaper_id):
		'''This is a privileged method. You must authorize before you can use it.
		Informs the server that it should start a sync of a wallpaper to a user's dropbox.
		This checks against the server for wallpapers.
		Returns None if the you haven't authorized against the server yet.
		Returns True if a wallpaper was set to sync (or was already synced).
		Returns False if the HTTP response is not 200 or 422 (already synced)'''
		
		return self.__update_sync(wallpaper_id,'sync')

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
			logging.info(
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
		Returns True if the wallpFalse otherwise.'''
		query={'wallpaper_id':wallpaper_id}
		r = requests.get('{}users/{}/wallpapers'.format(self.baseurl,username),params = query)
		if r.status_code!=200:
			#A logging message will go here.
			logging.info('Error checking for synced wallpaper: {}'.format(r.status_code))
			return None
		synced = None
		try:
			synced=r.json()['response']
		except:
			return None
		
		return True #Json has a response field. 
		

	def flag_wallpaper(self, wallpaper_id, flag):
		'''Flags a wallpaper. 
		flag must be flag_safe, flag_not_safe, and flag_deletion.
		This is a privileged method. You must first authenticate with the authorize() methods before 
		you can use this method.
		
		Returns None if the you haven't authorized against the server yet or if the flag is invalid.
		Returns True if the Wallpaper was successfully flagged.
		Returns False if the Wallpaper was not successfully flagged.
		'''
		if flag!='flag_safe' and flag!='flag_not_safe' and flag!='flag_deletion':
			logging.info('ERROR: Flag must be flag_safe, flag_not_safe, or flag_deletion')
			return None
		if not self.apikey:
			print(
				'ERROR: This is a user command. You must first authenticate as a user with authorize_user_pass() or authorize_API() method.')
			return
		requesturl = '{}wallpapers/{}/{}'.format(self.baseurl,wallpaper_id,flag)
		print(requesturl)
		r = requests.post(requesturl,params = {'auth_token': self.apikey})
		if r.status_code==200:
			return True
		else:
			return False


class Wallpaper:

	'''Items are put into this dynamically, and it has no methods.'''

	def __init__(self,info=None):
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
				if isinstance(info[attribute],dict):
					#it's an image object.
					setattr(self,attribute,Image(info[attribute]))
					continue
				setattr(self, attribute, info[attribute])

	def __str__(self):
		string = 'Wallpaper object: '
		props = []
		for attr in dir(self):
			if not callable(attr) and not attr.startswith('__'):
				props.append(attr + '=' + str(getattr(self, attr)))
		return '{}{}'.format(string,str(props))

class User:
	'''Defines a user on the site.'''
	def __init__(self,info=None):
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
				props.append(attr + '=' + str(getattr(self, attr)))
		return string + str(props)

class Image:
	'''Represents an image object (a part of a wallpaper object). It will either contain only a url or a url, width and height, and another Image object..
	Width and Height attributes signify that this is a preview or a thumbnail image.'''
	
	def __init__(self,info=None):
		for key in info:
			print('self.{} = None'.format(key))
		self.thumb = None
		self.preview = None
		self.url = None
		self.width = None
		self.height = None
		
		
		if info:
			#Parsing image package - it might be the top level one (full) or lower (preview/thumbnail)
			for attribute in info:
				if isinstance(info[attribute],dict):
					#it's an image object.
					setattr(self,attribute,Image(info[attribute]))
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
				props.append(attr + '=' + str(getattr(self, attr)))
		return string + str(props)
	
def _get_userpass():
	'''Prompt for username and password.'''

	print('Username: ', end='')
	username = input()
	password = getpass.getpass()
	return (username, password)

if __name__ == '__main__':
	api = DesktopprAPI()
	#user=api.get_user_info('mgamerz')
	users = api.get_user_followers('keithpitt')
	for user in users:
		print(user)
	exit()
	for key in user:
		print('self.{} = None'.format(key))
	#First we test privledged commands before we authenticate to make sure they fail properly.
	api.like_wallpaper(200)
	api.unlike_wallpaper(201)
	api.sync_wallpaper(202)
	api.unsync_wallpaper(203)
	
	exit()
	# test authorization techniques
	userpass = _get_userpass()
	if api.authorize_user_pass(userpass[0], userpass[1]):
		print('Username/Password Authorization successful')
	else:
		print('Username/Password Authorization failed')
	
	wallpaper = api.get_user_randomwallpaper('keithpitt')
	if wallpaper:
		print(wallpaper.image['url'])
	else:
		print('Error!')
	exit()
	#test for wallpaper sync
	if	api.check_if_synced('keithpitt',256167):
		print('User has synced wallpaper')
	else:
		print('User has not synced wallpaper 417841')
	
	if api.check_if_synced('mgamerz',418045):
		print('User has synced wallpaper')
	else:
		print('User has not synced wallpaper 417841')
		
	if api.unsync_wallpaper(256167):
		print('Wallpaper should sync shortly.')
	else:
		print('Error trying to sync wallpaper.')
	exit()
	
	if api.authorize_API('YOUR API KEY HERE'):
		print('API Authorization successful')
	else:
		print('API Authorization failed')
	
	#Test flagging
	api.flag_wallpaper(418232,'flag_not_safe')

	
	# test follow/unfollow users
	followresponse = api.follow_user('nermil')
	if followresponse == 200:
		print('Follow user succeeded')
	else:
		print('Follow user failed:', followresponse)

	# test userinfo queries
	
	print(api.get_user_collection('keithpitt'))

	# test get wallpaper info pages
	wallpapers = api.get_wallpapers(2)
	for paper in wallpapers:
		print(paper)
	print(api.get_user_random_wallpaper('keithpitt'))
	print(api.get_user_random_wallpaper('mgamerz'))
	print(api.get_user_random_wallpaper('mgamerzsg'))

	if api.follow_user('keithpittz', unfollow=True) == 200:
		print('Unfollow user succeeded')
	else:
		print('Unfollow user failed')

	# test fetching wallpaper urls
	images = api.get_wallpapers_url()
	number = 0
	# test downloading wallpapers (only a few)
	for image in images:
		if number < 5:
			g = urllib.request.urlopen(image)
			number += 1
			with open('image' + str(number) + '.jpg', 'b+w') as f:
				f.write(g.read())
