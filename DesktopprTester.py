'''
Created on Jan 15, 2014

@author: Mgamerz
'''
import unittest
import time
import sys
import logging
import random
import DesktopprApi
import requests

testing_apikey = 'HCsYzq284U11q7ZfiH-s'
test_logger = logging.getLogger('DesktopprTester')
print(test_logger.getEffectiveLevel())
test_logger.setLevel(logging.INFO)
print(test_logger.getEffectiveLevel())
hdlr = logging.StreamHandler()
test_logger.addHandler(hdlr)

class Test(unittest.TestCase):


    def testNoauth(self):
        api = DesktopprApi.DesktopprAPI()
        api.logger.setLevel(logging.INFO)
        self.assertEqual(api.like_wallpaper(200), None)
        self.assertEqual(api.unlike_wallpaper(201), None)
        self.assertEqual(api.sync_wallpaper(202), None)
        self.assertEqual(api.unsync_wallpaper(203), None)
        
    def testUserCollection(self):
        api = DesktopprApi.DesktopprAPI()
        api.logger.setLevel(logging.INFO)
        test_logger.info('Testing KeithPitts collection.')
        page = api.get_user_collection('keithpitt') #He is sure to have a collection.
        self.assertFalse(isinstance(page, type(None)))
        self.assertTrue(isinstance(page, DesktopprApi.Page))
        self.assertFalse(page.users)
        self.assertTrue(page.wallpapers)
    
    def testLikes(self):
        api = DesktopprApi.DesktopprAPI()
        api.logger.setLevel(logging.INFO)
        #Test invalid user
        self.assertTrue(api.get_userlikes(isinstance('alsgkhaasdfa', 100), type(None)))

        for i in range(6):
            test_logger.info('Pass {} [test type 1] in likes test'.format(i))
            wp = api.get_random_wallpaper()
            user = wp.uploader
            if not user:
                test_logger.info('Uploaded image has no user account associated with it. It likely was deleted. Skipping this round.')
                continue
            test_logger.info('Wallpaper uploader is: {}'.format(user))
            test_logger.info('Getting {} liked wallpapers page'.format(user))
            userlikespage = api.get_userlikes(user)
            self.assertFalse(userlikespage.users)
            if userlikespage.wallpapers:
                for paper in userlikespage.wallpapers:
                    test_logger.info('Testing {} likes wallpaper {}'.format(user, paper.id))
                    self.assertTrue(api.check_if_liked(user, paper.id))

        api.authorize_API(testing_apikey)
        liked = []
        for i in range(6):
            test_logger.info('Pass {} [test type 2] in likes test'.format(i))
            paper = api.get_random_wallpaper()
            api.like_wallpaper(paper.id)
            test_logger.info('Liking wallpaper {}'.format(i))
            liked.append(paper.id)
        for like in liked:
            test_logger.info('Testing like status {}'.format(i))
            self.assertTrue(api.check_if_liked(api.authed_user, like))
        
    def testSyncStatus(self):
        api = DesktopprApi.DesktopprAPI()
        api.logger.setLevel(logging.INFO)
        api.authorize_API(testing_apikey)
        synced = []
        for i in range(6):
            test_logger.info('Syncing random wallpaper {}'.format(i))
            paper = api.get_random_wallpaper()
            api.sync_wallpaper(paper.id)
            synced.append(paper.id)

        test_logger.warning('Waiting for Dropbox transfer wallpapers for sync test.')
        time.sleep(7) #let dropbox sync
        test_logger.info('Validating wallpapers were synced')
        for sync in synced:
            self.assertTrue(api.check_if_synced(api.authed_user, sync))
            test_logger.info('Removing wallpaper.')
            self.assertTrue(api.unsync_wallpaper(sync))

        test_logger.warning('Waiting for Dropbox to remove wallpapers.')
        time.sleep(5)
        test_logger.info('Validating wallpaper was unsynced')
        for sync in synced:
            self.assertFalse(api.check_if_synced(api.authed_user, sync))
        self.assertFalse(api.check_if_synced('mgamerz', 26167))
        self.assertFalse(api.check_if_synced('mgamerz', 124089))
        self.assertFalse(api.check_if_synced('mgamerz', 1240890000))

    def testStrings(self):
        api = DesktopprApi.DesktopprAPI()
        test_logger.info('Testing string representation of objects')

        page = api.get_user_collection('keithpitt')
        self.assertTrue(isinstance(str(page), str))
        for item in page.wallpapers:
            self.assertTrue(isinstance(str(item), str))
            self.assertTrue(isinstance(str(item.image), str))
            self.assertTrue(isinstance(str(item.image.preview), str))
            self.assertTrue(isinstance(str(item.image.thumb), str))

        page = api.get_followed_users('keithpitt')
        self.assertTrue(isinstance(str(page), str))
        for user in page.users:
            self.assertTrue(isinstance(str(user), str))

    def testLikeStatus(self):
        api = DesktopprApi.DesktopprAPI()
        api.logger.setLevel(logging.INFO)
        self.assertTrue(api.check_if_liked('mgamerz', 418047))
        self.assertFalse(api.check_if_liked('mgamerz', 41804700))
        self.assertTrue(api.check_if_liked(isinstance('alsgkhaasdfa', 100), type(None)))


    def testBadFilters(self):
        api = DesktopprApi.DesktopprAPI()
        api.authorize_API(testing_apikey)
        self.assertTrue(isinstance(api.flag_wallpaper(717, 'flag_failure'), type(None)))
        self.assertTrue(isinstance(api.get_wallpapers(safefilter='flag_failure'), type(None)))
        self.assertTrue(isinstance(api.get_wallpaper_urls(safefilter='flag_failure'), type(None)))
        self.assertTrue(isinstance(api.get_random_wallpaper(safefilter='flag_failure'), type(None)))

    def testUserinfo(self):
        api = DesktopprApi.DesktopprAPI()
        for i in range(6):
            test_logger.info('Pass {} in userinfo test'.format(i))
            wp = api.get_random_wallpaper()
            user = wp.uploader
            if not user:
                test_logger.info('Uploaded image has no user account associated with it. It likely was deleted. Skipping this round.')
                continue
            userinfo = api.get_user_info(user)
            self.assertTrue(isinstance(userinfo, DesktopprApi.User))

        #Check for bad usernames.
        userlist = ['assert_fails_test', 'assert_fails_test2', 'HERPA_DERPA_HERP_DERP2']
        for user in userlist:
            test_logger.info('Testing bad username {} in userinfo test'.format(user))
            self.assertFalse(isinstance(api.get_user_info(user), DesktopprApi.User))
    
    def testFollowing(self):
        api = DesktopprApi.DesktopprAPI()
        api.logger.setLevel(logging.INFO)
        for i in range(6):
            test_logger.info('Pass {} in following test'.format(i))
            wp = api.get_random_wallpaper()
            user = wp.uploader
            if not user:
                #Null checking
                continue
            userpage = api.get_followed_users(user)
            if userpage:
                self.assertTrue(isinstance(userpage, DesktopprApi.Page))
                self.assertTrue(not userpage.wallpapers)
                if userpage.users:
                    #User might not follow anyone, so we want to make sure its not None first.
                    for user in userpage.users:
                        self.assertTrue(isinstance(user, DesktopprApi.User))

    def testFollower(self):
        api = DesktopprApi.DesktopprAPI()
        api.logger.setLevel(logging.INFO)
        for i in range(6):
            test_logger.info('Pass {} in follower test'.format(i))
            wp = api.get_random_wallpaper()
            user = wp.uploader
            if not user:
                #Null checking
                continue
            userpage = api.get_user_followers(user)
            if userpage:
                self.assertTrue(isinstance(userpage, DesktopprApi.Page))
                self.assertTrue(not userpage.wallpapers)
                if userpage.users:
                    #User might not follow anyone, so we want to make sure its not None first.
                    for user in userpage.users:
                        self.assertTrue(isinstance(user, DesktopprApi.User))

    def testAuthorization(self):
        #It's not really safe to put in my real username and password here.
        api = DesktopprApi.DesktopprAPI()
        api.logger.setLevel(logging.INFO)
        self.assertFalse(api.authorize_API('TESTING_API_AUTHORIZATION'))
        self.assertFalse(api.authorize_user_pass('API_ASSERT_FAIL', '1234567890'))

        #Now we shall authorize.
        self.assertTrue(api.authorize_API(testing_apikey)) #this is for a testing account. Nothing is linked to it.

    def testRandomUserwallpaper(self):
        api = DesktopprApi.DesktopprAPI()
        api.logger.setLevel(logging.INFO)
        for i in range(6):
            test_logger.info('Pass {} in random user wallpaper [keithpitt] test'.format(i))
            wp = api.get_user_randomwallpaper('keithpitt')
            self.assertTrue(isinstance(wp, DesktopprApi.Wallpaper))
            self.assertTrue(isinstance(wp.image, DesktopprApi.Image))
            self.assertTrue(isinstance(wp.image.thumb, DesktopprApi.Image))
            self.assertTrue(isinstance(wp.image.preview, DesktopprApi.Image))

    def testWallpaperUrls(self):
        api = DesktopprApi.DesktopprAPI()
        api.logger.setLevel(logging.INFO)
        urls = api.get_wallpaper_urls()
        for url in urls:
            test_logger.info('Testing URL exists: {}'.format(url))
            r = requests.head(url, headers={'Connection': 'close'})
            self.assertTrue(r.status_code == 200)

    def testFlagging(self):
        '''This test uses hard coded values, as I don't want to flag random wallpapers as safe/unsafe
        if they were accidentally flagged.'''
        api = DesktopprApi.DesktopprAPI()
        api.logger.setLevel(logging.INFO)
        #Test if we can get a response if we aren't authorized yet.
        self.assertTrue(isinstance(api.flag_wallpaper(418618, 'flag_safe'), type(None)))
        api.authorize_API(testing_apikey)
        known_safe_wallpapers = (418618, 418644)
        known_nsfw_wallpapers = (418997, 418304)

        test_logger.info('Flagging wallpapers as safe/notsafe')
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
        #Skip if python version 3.2: Build server concurrency issues.
        if sys.version_info[1] < 3:
            #Don't do it on python 3.2.x
            return
        else:
            #make it wait so the build server doesn't overlap.
            test_logger.warning('Waiting 90 seconds for Python 3.2 testing to finish.')
            time.sleep(90)
        api = DesktopprApi.DesktopprAPI()
        api.logger.setLevel(logging.INFO)
        api.authorize_API(testing_apikey)
        #first, delete existing likes.
        page = api.get_userlikes(api.authed_user)
        if page:
            while page.items_on_page > 0:
                for paper in page.wallpapers:
                    test_logger.info('Unliking wallpaper...')
                    api.unlike_wallpaper(paper.id)
                page = api.get_userlikes(api.authed_user)

        #Second, we will randomly like lots of wallpapers.
        test_logger.info('Liking wallpapers to create pages on the server.')

        liked = 0
        loops = 45
        for _ in range(loops):
            test_logger.info('Liking wallpaper {} in loop of {}'.format(liked+1, loops))
            wp = api.get_random_wallpaper()
            self.assertTrue(api.like_wallpaper(wp.id))
            liked += 1

        likes_page = api.get_userlikes(api.authed_user)

        test_numlikes = 0
        if likes_page:
            while likes_page.items_on_page > 0:
                test_numlikes += likes_page.items_on_page #I think this is how many items are on this page...
                likes_page = api.get_userlikes(api.authed_user, likes_page.current_page+1)
        else:
            self.fail('Likes page should not be None')
        test_logger.info('Number liked vs known number: {}:{}'.format(liked, test_numlikes))
        self.assertTrue(liked == test_numlikes)

    def testAuthFollowUnFollow(self):
        api = DesktopprApi.DesktopprAPI()
        api.logger.setLevel(logging.INFO)
        test_logger.info('Testing follow user as not authorized')
        wp = api.get_random_wallpaper()
        if wp.uploader:
            self.assertTrue(isinstance(api.follow_user(wp.uploader),type(None)))
        else:
            test_logger.info('Uploaded user has deleted this account. Skipping this noauth test.')

        api.authorize_API(testing_apikey)
        for i in range(6):
            test_logger.info('Pass {} in follow user test'.format(i))
            wp = api.get_random_wallpaper()
            if not wp.uploader:
                test_logger.info('Uploaded user has deleted this account. Skipping this pass')
                continue
            self.assertTrue(api.follow_user(wp.uploader))
            self.assertTrue(api.unfollow_user(wp.uploader))

        #Test follow fails
        self.assertFalse(api.follow_user('NON_EXISTENT_ACCOUNTX'))

    @classmethod
    def tearDownClass(cls):
        logging.warning('Finishing tests: Removing all wallpapers in DropBox.')
        api = DesktopprApi.DesktopprAPI()
        api.logger.setLevel(logging.INFO)
        api.authorize_API(testing_apikey)
        page = api.get_user_collection(api.authed_user)
        while page:
            for paper in page.wallpapers:
                logging.warning('Unsyncing wallpaper...')
                api.unsync_wallpaper(paper.id)
            page = api.get_user_collection(api.authed_user) #Results will slowly crawl to page 1 as we delete them

        page = api.get_userlikes(api.authed_user)
        if page:
            while page.items_on_page > 0:
                for paper in page.wallpapers:
                    logging.warning('Unliking wallpaper...')
                    api.unlike_wallpaper(paper.id)
                page = api.get_userlikes(api.authed_user)


        page = api.get_followed_users(api.authed_user)
        if page:
            while page.items_on_page > 0:
                for user in page.users:
                    logging.warning('Unfollowing {}...'.format(user))
                    api.unfollow_wallpaper(user)
                page = api.get_userlikes(api.authed_user)



        #If wallpapers was false, there are no wallpapers in the collection.

if __name__ == "__main__":
    unittest.main()