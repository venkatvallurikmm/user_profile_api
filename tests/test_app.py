import unittest
import json
import os

from app.routes import app

class UsersProfilesTest(unittest.TestCase):

    def setUp(self) -> None:
        self.app = app
        self.app.config.from_pyfile(os.path.join(os.path.dirname(__file__), '../', 'config.cfg'))
        #elf.app.config.from_pyfile('../config.cfg')
        #self.app.config['TESTING']=True
        self.client = self.app.test_client()

    def test_users_profile_resource_not_found(self):
        # Token should be provided to avoid rate limit on github api (It allows only 60 requests per hour)
        headers = {
            'x-github-auth-token': self.app.config.get("GITHUB_TOKEN")
        }
        response = self.client.get('/users/dummy/profile', headers=headers)
        self.assertEqual(404, response.status_code)

    def test_users_profile_bad_creds(self):
        # When bad creds provided
        response = self.client.get('/users/mailchimp/profile', headers={'x-github-auth-token': "dummy"})
        self.assertEqual(401, response.status_code)

    def test_users_profile(self):
        # When mailchimp
        # Token should be provided to avoid rate limit on github api (It allows only 60 requests per hour)
        headers = {
            'x-github-auth-token': self.app.config.get("GITHUB_TOKEN")
        }
        response = self.client.get('/users/mailchimp/profile', headers=headers)
        self.assertEqual(200, response.status_code)
        data = response.json

        self.assertGreater(data['total_original_repos'], 0, "Total original repositories must be greater than zero")
        self.assertGreater(data['total_forked_count'], 0, "Total forked count must be greater than zero")
        self.assertGreater(data['total_watchers_count'], 0, "Total watchers count must be greater than zero")
        self.assertGreater(len(data['repos']), 0, "Total repositories must be greater than zero")
        self.assertEqual(True, bool(data['total_languages']))