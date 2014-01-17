'''
Created on Jan 15, 2014

@author: Mgamerz
'''
import unittest
import time
import logging
import random
import DesktopprApi

testing_apikey = 'HCsYzq284U11q7ZfiH-s'
class Test(unittest.TestCase):


    def testNoauth(self):
        api=DesktopprApi.DesktopprAPI()
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
        for whocares in range(6):
            paper = api.get_random_wallpaper()
            api.like_wallpaper(paper.id)
            liked.append(paper.id)
        for like in liked:
            self.assertTrue(api.check_if_liked(api.authed_user, like))
        
    def testSyncStatus(self):
        api = DesktopprApi.DesktopprAPI()
        api.authorize_API(testing_apikey)
        synced = []
        for whocares in range(6):
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
        for whocares in range(6):
            wp = api.get_random_wallpaper()
            user = wp.uploader
            if not user:
                #Null checking
                print(wp)
            userinfo = api.get_user_info(user)
            self.assertTrue(isinstance(userinfo, DesktopprApi.User))

        #Check for bad usernames.
        userlist = ['assert_fails_test', 'assert_fails_test2', 'Check out my github its a python wrapper for this site!']
        for user in userlist:
            self.assertFalse(isinstance(api.get_user_info(user), DesktopprApi.User))
    
    def testFollowing(self):
        api = DesktopprApi.DesktopprAPI()
        #TODO: Use random wallpaper to find users instead for more strenous testing
        for whocares in range(6):
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
        for whocares in range(6):
            wp = api.get_user_randomwallpaper('keithpitt')
            self.assertTrue(isinstance(wp, DesktopprApi.Wallpaper))
            self.assertTrue(isinstance(wp.image, DesktopprApi.Image))
            self.assertTrue(isinstance(wp.image.thumb, DesktopprApi.Image))
            self.assertTrue(isinstance(wp.image.preview, DesktopprApi.Image))

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
            self.assertTrue(api.flag_wallpaper(safe, 'flag_not_safe'))

        #Test flags on wallpapers that don't exist
        for whocares in range(6):
            self.assertFalse(api.flag_wallpaper(random.randint(9000000, 90000000), 'flag_safe'))



    @classmethod
    def tearDownClass(cls):
        logging.warning('Finishing tests: Removing all wallpapers in dropbox.')
        api = DesktopprApi.DesktopprAPI()
        api.authorize_API(testing_apikey)
        wallpapers = api.get_user_collection(api.authed_user)
        if wallpapers:
            for paper in wallpapers:
                api.unsync_wallpaper(paper.id)

        #If wallpapers was false, there are no wallpapers in the collection.




if __name__ == "__main__":
    unittest.main()