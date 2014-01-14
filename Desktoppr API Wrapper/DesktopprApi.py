'''
Created on Jan 13, 2014

@author: Mgamerz
'''
import urllib.parse
import requests
from requests.auth import HTTPBasicAuth
import getpass
import traceback

class DesktopprApi(object):
    '''
    This class allows you to create an object that allows you to query the desktoppr site using their public api.
    '''
    baseurl='https://api.desktoppr.co/1/'
    
    def authorize_api(self, apikey):
        '''Authorizes using a users api key. This does not require the users password or username.'''
        query={'auth_token':apikey}
        requesturl=self.baseurl+'user/whoami?'+urllib.parse.urlencode(query)
        r = requests.get(requesturl)
        if r.status_code==200:
            print('Authenticated as',r.json()['response']['username'])
            self.apikey=apikey
            return True
        else:
            return False
    
    def authorize_userpass(self,username,password):
        '''Gets a privledged access key by authorizing to the site with a username/password. Stores the users API key for further privledged access in this session.'''
        r = requests.get('https://api.desktoppr.co/1/user/whoami',auth=HTTPBasicAuth(username,password))
        if r.status_code==200:
            self.apikey=r.json()['response']['api_token']
            print('Authenticated, got API token')
            return True
        else:
            return False
    
    def get_userinfo(self,username):
        '''Returns a dictionionary describing a specific user.'''
        query='users/'+username
        requesturl=self.baseurl+query
        response=None
        try:
            response=requests.get(requesturl).json()['response']
        except Exception as e:
            print('Error retrieving information for user',username,':',e)
        return response
    
    def get_usercollection(self,username):
        '''Returns a dictionary describing a specific users' collection of wallpapers.'''
        '''The API documentation on this method is somewhat ambiguous.'''
        query='users/'+username+'/wallpapers'
        requesturl=self.baseurl+query
        response=None
        try:
            response=requests.get(requesturl).json()['response']
        except Exception as e:
            print('Error retreiving wallpaper collection for user',username,':',e)
        return response
    
    def get_wallpapers(self,page=1,safefilter='safe'):
        '''Retrieves a list of wallpapers, and returns a list of wallpaper objects.'''
        if safefilter!='safe' and safefilter!='include_pending' and safefilter!='all':
            print('Unknown filter:',safefilter,'Valid options are safe, include_pending, all')
            return
        query={'page':str(page),'safe_filter':safefilter}
        requesturl=self.baseurl+'wallpapers?'+urllib.parse.urlencode(query)
        response=requests.get(requesturl)
        if response.status_code==200:
            #Build wallpaper object
            wallpapers=[]
            json = response.json()['response']
            for paperinfo in json:
                wallpaper=Wallpaper()
                #print('=====')
                for key in paperinfo:
                    setattr(wallpaper,key,paperinfo[key])
                wallpapers.append(wallpaper)
            return wallpapers
        else:
            print('Error getting wallpapers:',response.status_code)
            return
    
    def get_wallpapers_url(self,page=1,safefilter='safe'):
        '''This is a subset of get_wallpapers(), which returns a page of wallpaper URLs. The API does not document sorting options.'''
        if safefilter!='safe' and safefilter!='include_pending' and safefilter!='all':
            print('Unknown filter:',safefilter,'Valid options are safe, include_pending, all')
            return
        
        wallpapers=self.get_wallpapers(page,safefilter)
        urls=[]
        if wallpapers:
            for wallpaper in wallpapers:
                urls.append(wallpaper.image['url'])
        return urls
    
    def get_userfollowers(self,username):
        '''Not yet defined.'''
        pass
    
    def get_user_randomwallpaper(self,username):
        '''Gets a dictionary describing a random wallpaper in a users collection.
        Returns None if the user has no wallpapers in their collection.'''
        query='users/'+username+'/wallpapers/random'
        requesturl=self.baseurl+query
        print(requesturl)
        r = requests.get(requesturl)
        if r.status_code==500:
            print('Error: The user may not have any wallpapers, or some other error occurred: 500')
            return
        if r.status_code==404:
            print('The user',username,'does not exist: 404')
            return
        return r.json()['response']
    
    def follow_user(self,username,unfollow=False):
        '''This method is privledged. You must authorize before using it.
        To reverse this method into an unfollow command, set unfollow=True
        
        This method returns a status code of the result.
        
        200 = Operation succeeded [even if you already are following and try to follow, or aren't following and try to unfollow]
        404 = User does not exist
        '''
        if self.apikey==None:
            print('ERROR: This is a user command. You must first authenticate as a user with authorize_userpass() or authorize_api() method.')
            return
        r = None
        if unfollow:
            r = requests.get(self.baseurl+'users/'+username+'/follow',)
            #if r.status_code!=200:
            #    print('Abnormal response unfollowing user',username,':',r.status_code)
        else:
            r = requests.delete(self.baseurl+'users/'+username+'/follow', params={'auth_token': self.apikey})
            #if r.status_code!=200:
            #    print('Abnormal response following user',username,':',r.status_code)
        return r.status_code
        
class Wallpaper():
    '''Items are put into this dynamically, and it has no methods.'''
    
    def __init__(self):
        '''Predefined wallpaper attributes. These are elements in the returned json response when querying for an attribute.'''
        self.height=None
        self.created_at=None
        self.image=None
        self.url=None
        self.uploader=None
        self.user_count=None
        self.likes_count=None
        self.review_state=None
        self.bytes=None
        self.palette=None
        self.id=None
        self.width=None
        
    def __str__(self):
        string='Wallpaper object: '
        props=[]
        for attr in dir(self):
            if not callable(attr) and not attr.startswith('__'):
                props.append(attr+'='+str(getattr(self,attr)))
        return string+str(props)
        
def get_userpass():
    '''Prompt for username password. This is not part of the API, only a convenience method for this module.'''
    print('Username: ',end=" ")
    username = input()
    password = getpass.getpass()
    return (username,password)
        
if __name__=='__main__':
    api=DesktopprApi()
    
    #test get wallpaper info pages
    wallpapers=api.get_wallpapers(2)
    for paper in wallpapers:
        print(paper)
    #test authorization techniques
    userpass=get_userpass()
    if api.authorize_userpass(userpass[0],userpass[1]):
        print('Username/Password Authorization successful')
    else:
        print('Username/Password Authorization failed')
    
    if api.authorize_api('YOUR API KEY HERE'):
        print('API Authorization successful')
    else:
        print('API Authorization failed')
    

    
    print(api.get_user_randomwallpaper('keithpitt'))
    print(api.get_user_randomwallpaper('mgamerz'))
    print(api.get_user_randomwallpaper('mgamerzsg'))
    #test userinfo queries
    print(api.get_userinfo('keithpitt'))
    print(api.get_usercollection('keithpitt')) #
    
    #test follow/unfollow users
    if api.follow_user('keithpitt')==200:
        print('Follow user succeeded')
    else:
        print('Follow user failed')
    
    if api.follow_user('keithpittz',unfollow=True)==200:
        print('Unfollow user succeeded')
    else:
        print('Unfollow user failed')
    
    
    
    #test fetching wallpaper urls
    images=api.get_wallpapers_url()
    number=0
    #test downloading wallpapers (only a few)
    for image in images:
        if number<5:
            g= urllib.request.urlopen(image)
            number+=1
            with open('image'+str(number)+'.jpg', 'b+w') as f:
                f.write(g.read())
    