'''
Created on Jan 15, 2014

@author: Mgamerz
'''
import unittest
from DesktopprApi import DesktopprAPI

class Test(unittest.TestCase):


    def testNoauth(self):
        api=DesktopprAPI()
        self.assertEqual(api.like_wallpaper(200),None)
        self.assertEqual(api.unlike_wallpaper(201),None)
        self.assertEqual(api.sync_wallpaper(202),None)
        self.assertEqual(api.unsync_wallpaper(203),None)
        
        
    def testLikes(self):
        api=DesktopprAPI()
        
    def testSyncStatus(self):
        api = DesktopprAPI()
        self.assertTrue(api.check_if_synced('mgamerz',18028))
    #More tests to be written.


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testNoauth']
    unittest.main()