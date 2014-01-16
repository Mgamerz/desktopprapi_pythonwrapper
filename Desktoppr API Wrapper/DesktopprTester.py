'''
Created on Jan 15, 2014

@author: Mgamerz
'''
import unittest
import DesktopprApi

class Test(unittest.TestCase):


    def testNoauth(self):
        api=DesktopprApi.DesktopprAPI()
        self.assertEqual(api.like_wallpaper(200),None)
        self.assertEqual(api.unlike_wallpaper(201),None)
        self.assertEqual(api.sync_wallpaper(202),None)
        self.assertEqual(api.unsync_wallpaper(203),None)
        
        
    def testLikes(self):
        api=DesktopprApi.DesktopprAPI()
        
    def testSyncStatus(self):
        api=DesktopprApi.DesktopprAPI()
        self.assertTrue(api.check_if_synced('mgamerz',26167))
        self.assertFalse(api.check_if_synced('mgamerz',124089))
        self.assertFalse(api.check_if_synced('mgamerz',1240890000))
    #More tests to be written.
    def testLikeStatus(self):
        api=DesktopprApi.DesktopprAPI()
        self.assertTrue(api.check_if_liked('mgamerz',418047))
        self.assertFalse(api.check_if_liked('mgamerz',41804700))
        
    def testFollowers(self):
        api=DesktopprApi.DesktopprAPI()
        pass
    
    def testFollowing(self):
        pass
    
    def testRandomUserwallpaper(self):
        api=DesktopprApi.DesktopprAPI()
        wp = api.get_user_randomwallpaper('keithpitt')
        self.assertTrue(isinstance(wp,DesktopprApi.Wallpaper))
        self.assertTrue(isinstance(wp.image,DesktopprApi.Image))
        self.assertTrue(isinstance(wp.image.thumb,DesktopprApi.Image))
        self.assertTrue(isinstance(wp.image.preview,DesktopprApi.Image))

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testNoauth']
    unittest.main()