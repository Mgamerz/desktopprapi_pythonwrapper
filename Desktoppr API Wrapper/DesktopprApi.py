'''
Created on Jan 13, 2014

@author: Mgamerz
		 wegry
'''
import urllib.parse
import requests
import getpass

from requests.auth import HTTPBasicAuth


class DesktopprAPI:

	'''
	This class allows you to create an object that allows you to query the desktoppr site using their public api.
	'''
	baseurl = 'https://api.desktoppr.co/1/'
	apikey = None
	
	def authorize_API(self, apikey):
		'''Authorizes using a users api key. This does not require the users 
		password or username.
		'''
		query = {'auth_token': apikey}
		requesturl = '{}user/whoami'.format(self.baseurl)
		r = requests.get(requesturl,params=query)
		if r.status_code == 200:
			print('Authenticated as', r.json()['response']['username'])
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
			print('Authenticated, got API token')
			return True
		else:
			return False

	def get_user_info(self, username):
		'''Returns a dictionionary describing a specific user.'''
		query = 'users/' + username
		requesturl = self.baseurl + query
		response = None
		try:
			response = requests.get(requesturl).json()['response']
		except Exception as e:
			print('Error retrieving information for user', username, ':', e)
		return response

	def get_user_collection(self, username):
		'''Returns a dictionary describing a specific users' collection of 
		wallpapers. The API documentation on this method is somewhat ambiguous.
		'''
		query = 'users/' + username + '/wallpapers'
		requesturl = self.baseurl + query
		response = None
		try:
			response = requests.get(requesturl).json()['response']
		except Exception as e:
			print(
				'Error retreiving wallpaper collection for user',
				username,
				':',
				e)
		return response

	def get_wallpapers(self, page=1, safefilter='safe'):
		'''Retrieves a list of wallpapers, and returns a list of wallpaper 
		objects.
		'''
		if safefilter != 'safe' and safefilter != 'include_pending' and safefilter != 'all':
			print(
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
			print('Error getting wallpapers:', response.status_code)
			return

	def get_wallpapers_url(self, page=1, safefilter='safe'):
		'''This is a subset of get_wallpapers(), which returns a page of wallpaper URLs. The API does not document sorting options.'''
		if safefilter != 'safe' and safefilter != 'include_pending' and safefilter != 'all':
			print(
				'Unknown filter:',
				safefilter,
				'Valid options are safe, include_pending, all')
			return

		wallpapers = self.get_wallpapers(page, safefilter)
		urls = []
		if wallpapers:
			for wallpaper in wallpapers:
				urls.append(wallpaper.image['url'])
		return urls

	def get_user_followers(self, username):
		'''Not yet defined.'''
		query = 'users/' + username + '/followers'
		response = requests.get(self.baseurl + query)
		print(response)
		pass

	def get_user_randomwallpaper(self, username):
		'''Fetches a random wallpaper a user has in their collection.
		Returns a Wallpaper object, or None if it can't retreive a wallpaper.'''
		requesturl = '{}users/{}/wallpapers/random'.format(self.baseurl,username)
		r = requests.get(requesturl)
		if r.status_code == 500 or r.status_code == 404:
			#error occured
			print(r.url)
			print('Status code:{}',r.status_code)
			return None
		wallpaper = Wallpaper(r.json()['response'])
		return wallpaper

	def follow_user(self, username, unfollow=False):
		'''This method is privileged. You must authorize before using it.
		To reverse this method into an unfollow command, set unfollow=True

		This method returns a status code of the result.

		200 = Operation succeeded [even if you already are following and try to follow, or aren't following and try to unfollow]
		404 = User does not exist
		'''
		if not self.apikey:
			print(
				'ERROR: This is a user command. You must first authenticate as a user with authorize_user_pass() or authorize_API() method.')
			return
		r = None
		if unfollow == False:
			#,params={'auth_token': self.apikey})
			r = requests.post(
				self.baseurl + 'users/' + username + '/follow',
				params={'auth_token': self.apikey})

			# if r.status_code!=200:
			#	print('Abnormal response unfollowing user',username,':',r.status_code)
		else:
			r = requests.delete(
				self.baseurl + 'users/' + username + '/follow',
				params={'auth_token': self.apikey})
			print(r)
			print(r.json())
			# if r.status_code!=200:
			#	print('Abnormal response following user',username,':',r.status_code)
		return r.status_code


	def like_wallpaper(self,wallpaper_id):
		return self.__update_like(wallpaper_id,'like')

	def unlike_wallpaper(self,wallpaper_id):
		return self.__update_like(wallpaper_id,'unlike')
	
	def __update_like(self,wallpaper_id,action):
		'''Internal method to handle like/unlike requests'''
		if action!='like' and action!='unlike':
			print('An internal error occured trying to like or unlike a wallpaper.')
			return
		if not self.apikey:
			print(
				'ERROR: This is a user command. You must first authenticate as a user with authorize_user_pass() or authorize_API() method.')
			return False
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
			print('Error retrieving liked status:{}',(r.status_code))
		liked=r.json()['response']
		print(liked)
		if liked:
			return True
		else:
			return False


	def sync_wallpaper(self,wallpaper_id):
		return self.__update_sync(wallpaper_id,'sync')

	def unsync_wallpaper(self,wallpaper_id):
		return self.__update_sync(wallpaper_id,'unsync')
	
	def __update_sync(self,wallpaper_id,action):
		'''Internal method to handle sync requests'''
		if action!='sync' and action!='unsync':
			print('An internal error occured trying to sync or unsync a wallpaper.')
			return
		if not self.apikey:
			print(
				'ERROR: This is a user command. You must first authenticate as a user with authorize_user_pass() or authorize_API() method.')
			return False
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
		'''Checks if a user has a wallpaper currently synced to their dropbox.
		Returns True if it is, False otherwise.'''
		query={'wallpaper_id':wallpaper_id}
		r = requests.get('{}users/{}/wallpapers'.format(self.baseurl,username),params = query)
		print(r.url)
		if r.status_code!=200:
			print('Error retrieving synced status:{}',(r.status_code))
		synced=r.json()['response']
		print(synced)
		if synced:
			return True
		else:
			return False
		

	def flag_wallpaper(self, wallpaper_id, flag):
		'''Flags a wallpaper. flag is flag_safe, flag_not_safe, and flag_deletion.
		This is a privileged method. You must first authenticate with the authorize() methods before 
		you can use this method.
		
		Returns the status code of the post request:
		200 - Wallpaper successfully flagged
		404 - Wallpaper was not found
		'''
		if flag!='flag_safe' and flag!='flag_not_safe' and flag!='flag_deletion':
			print('ERROR: Flag must be flag_safe, flag_not_safe, or flag_deletion')
			return
		if not self.apikey:
			print(
				'ERROR: This is a user command. You must first authenticate as a user with authorize_user_pass() or authorize_API() method.')
			return
		requesturl = '%swallpapers/%s/%s' % (self.baseurl,wallpaper_id,flag)
		print(requesturl)
		r = requests.post(requesturl,params = {'auth_token': self.apikey})
		return r.status_code


class Wallpaper:

	'''Items are put into this dynamically, and it has no methods.'''

	def __init__(self,info=None):
		'''Predefined wallpaper attributes. These are elements in the returned
		json response when querying for an attribute.
		'''
		
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
			for key in info:
				setattr(self, key, info[key])

	def __str__(self):
		string = 'Wallpaper object: '
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
	# test authorization techniques
	'''
	userpass = _get_userpass()
	if api.authorize_user_pass(userpass[0], userpass[1]):
		print('Username/Password Authorization successful')
	else:
		print('Username/Password Authorization failed')
	'''
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
	print(api.get_user_info('keithpitt'))
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
