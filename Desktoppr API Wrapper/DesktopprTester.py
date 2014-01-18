'''
Created on Jan 15, 2014

@author: Mgamerz
'''
import unittest
import time
import logging
import random
import DesktopprApi
import requests

testing_apikey = 'HCsYzq284U11q7ZfiH-s'
class Test(unittest.TestCase):


    def testNoauth(self):
        api = DesktopprApi.DesktopprAPI()
        self.assertEqual(api.like_wallpaper(200), None)
        self.assertEqual(api.unlike_wallpaper(201), None)
        self.assertEqual(api.sync_wallpaper(202), None)
        self.assertEqual(api.unsync_wallpaper(203), None)
        
    def testUserCollection(self):
        api = DesktopprApi.DesktopprAPI()
        wallpapers = api.get_user_collection('keithpitt') #He is sure to have a collection.
        self.assertFalse(isinstance(wallpapers, type(None)))
    
    def testLikes(self):
        api = DesktopprApi.DesktopprAPI()
        api.authorize_API(testing_apikey)
        liked = []
        for _ in range(6):
            paper = api.get_random_wallpaper()
            api.like_wallpaper(paper.id)
            liked.append(paper.id)
        for like in liked:
            self.assertTrue(api.check_if_liked(api.authed_user, like))
        
    def testSyncStatus(self):
        api = DesktopprApi.DesktopprAPI()
        api.authorize_API(testing_apikey)
        synced = []
        for _ in range(6):
            paper = api.get_random_wallpaper()
            api.sync_wallpaper(paper.id)
            synced.append(paper.id)

        logging.warning('Waiting for Dropbox transfer wallpapers for sync test.')
        time.sleep(7) #let dropbox sync
        for sync in synced:
            self.assertTrue(api.check_if_synced(api.authed_user, sync))
            self.assertTrue(api.unsync_wallpaper(sync))

        logging.warning('Waiting for Dropbox to remove wallpapers.')
        time.sleep(5)
        for sync in synced:
            self.assertFalse(api.check_if_synced(api.authed_user, sync))
        self.assertFalse(api.check_if_synced('mgamerz', 26167))
        self.assertFalse(api.check_if_synced('mgamerz', 124089))
        self.assertFalse(api.check_if_synced('mgamerz', 1240890000))
        #More tests to be written.
        
    def testLikeStatus(self):
        api = DesktopprApi.DesktopprAPI()
        self.assertTrue(api.check_if_liked('mgamerz', 418047))
        self.assertFalse(api.check_if_liked('mgamerz', 41804700))
        
    def testUserinfo(self):
        api = DesktopprApi.DesktopprAPI()
        for _ in range(6):
            wp = api.get_random_wallpaper()
            user = wp.uploader
            if not user:
                logging.info('Uploaded image has no user account associated with it. It likely was deleted. Skipping this round.')
                continue
            userinfo = api.get_user_info(user)
            self.assertTrue(isinstance(userinfo, DesktopprApi.User))

        #Check for bad usernames.
        userlist = ['assert_fails_test', 'assert_fails_test2', 'Check out my github its a python wrapper for this site!']
        for user in userlist:
            self.assertFalse(isinstance(api.get_user_info(user), DesktopprApi.User))
    
    def testFollowing(self):
        api = DesktopprApi.DesktopprAPI()
        for _ in range(6):
            wp = api.get_random_wallpaper()
            user = wp.uploader
            if not user:
                #Null checking
                print(wp)
            users = api.get_followed_users(user)
            if users:
                for user in users:
                    self.assertTrue(isinstance(user, DesktopprApi.User))

    def testAuthorization(self):
        #It's not really safe to put in my real username and password here.
        api = DesktopprApi.DesktopprAPI()
        self.assertFalse(api.authorize_API('TESTING_API_AUTHORIZATION'))
        self.assertFalse(api.authorize_user_pass('API_ASSERT_FAIL', '1234567890'))

        #Now we shall authorize.
        self.assertTrue(api.authorize_API(testing_apikey)) #this is for a testing account. Nothing is linked to it.

    def testRandomUserwallpaper(self):
        api = DesktopprApi.DesktopprAPI()
        for _ in range(6):
            wp = api.get_user_randomwallpaper('keithpitt')
            self.assertTrue(isinstance(wp, DesktopprApi.Wallpaper))
            self.assertTrue(isinstance(wp.image, DesktopprApi.Image))
            self.assertTrue(isinstance(wp.image.thumb, DesktopprApi.Image))
            self.assertTrue(isinstance(wp.image.preview, DesktopprApi.Image))

    def testWallpaperUrls(self):
        api = DesktopprApi.DesktopprAPI()
        urls = api.get_wallpaper_urls()
        for url in urls:
            r = requests.head(url, headers={'Connection': 'close'})
            self.assertTrue(r.status_code == 200)

    def testFlagging(self):
        '''This test uses hard coded values, as I don't want to flag random wallpapers as safe/unsafe
        if they were accidentally flagged.'''
        api = DesktopprApi.DesktopprAPI()
        #Test if we can get a response if we aren't authorized yet.
        self.assertTrue(isinstance(api.flag_wallpaper(418618, 'flag_safe'), type(None)))

        api.authorize_API(testing_apikey)
        known_safe_wallpapers = (418618, 418644)
        known_nsfw_wallpapers = (418997, 418304)

        #Test real flags
        for safe in known_safe_wallpapers:
            self.assertTrue(api.flag_wallpaper(safe, 'flag_safe'))

        for nsfw in known_nsfw_wallpapers:
            self.assertTrue(api.flag_wallpaper(nsfw, 'flag_not_safe'))

        #Test flags on wallpapers that don't exist
        for _ in range(6):
            #these wallpapers don't exist. Should return false.
            self.assertFalse(api.flag_wallpaper(random.randint(9000000, 90000000), 'flag_safe'))

    def testPagination(self):
        api = DesktopprApi.DesktopprAPI()
        api.authorize_API(testing_apikey)
        #First, we will randomly like lots of wallpapers.
        logging.info('Liking wallpapers to create pages on the server.')
        liked = 0
        loops = 45
        for _ in range(loops):
            logging.info('Liking wallpaper {} in loop of {}'.format(liked, loops))
            wp = api.get_random_wallpaper()
            self.assertTrue(api.like_wallpaper(wp.id))
            liked += 1

        likes_page = api.get_userlikes(api.authed_user)
        print(likes_page)

        test_numlikes = 0
        if likes_page:
            while likes_page.items_on_page > 0:
                print(likes_page)
                test_numlikes += likes_page.items_on_page #I think this is how many items are on this page...
                likes_page = api.get_userlikes(api.authed_user, likes_page.current_page+1)
        else:
            self.fail('Likes page should not be None')
        logging.info('Number liked vs known number: {}:{}'.format(liked, test_numlikes))
        self.assertTrue(liked == test_numlikes)

    @classmethod
    def tearDownClass(cls):
        logging.warning('Finishing tests: Removing all wallpapers in dropbox.')
        api = DesktopprApi.DesktopprAPI()
        api.authorize_API(testing_apikey)
        page = api.get_user_collection(api.authed_user)
        while page:
            print(page)
            for paper in page.wallpapers:
                api.unsync_wallpaper(paper.id)
            page = api.get_user_collection(api.authed_user) #Results will slowly crawl to page 1 as we delete them

        page = api.get_userlikes(api.authed_user)
        if page:
            while page.items_on_page > 0:
                print(page)
                for paper in page.wallpapers:
                    api.unlike_wallpaper(paper.id)
                page = api.get_userlikes(api.authed_user)

        #If wallpapers was false, there are no wallpapers in the collection.

if __name__ == "__main__":
    unittest.main()