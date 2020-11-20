import unittest
import json
import os
from unittest.mock import patch

from app.routes import app


class MockResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data

def mocked_requests_get(*args, **kwargs):
    if "api.github" in args[0]:
        if "languages" in args[0]:
            return MockResponse({"Java": 100, "Python": 120}, 200)
        if "topics" in args[0]:
            return MockResponse({"names": ["octocat","atom","electron","api"]}, 200)
        return MockResponse(get_mock_data('github_mock_data.json'), 200)
    elif "api.bitbucket" in args[0]:
        return MockResponse(get_mock_data('bitbucket_mock_data.json'), 200)

    return MockResponse({}, 200)

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
        mock_patcher = patch('app.utils.http_utils.requests.get')
        mock_get = mock_patcher.start()
        mock_get.return_value = MockResponse({'message': 'Not found'}, 404);

        response = self.client.get('/users/dummy/profile', headers=headers)
        mock_get.assert_called_with(self.get_github_url('dummy'), headers=self.get_github_mock_headers())
        self.assertEqual(404, response.status_code)
        mock_patcher.stop()

    def test_users_profile_bad_creds(self):
        mock_patcher = patch('app.utils.http_utils.requests.get')
        mock_get = mock_patcher.start()
        mock_get.return_value = MockResponse({'message': 'Bad Credentials'}, 401);
        # When bad creds provided
        response = self.client.get('/users/mailchimp/profile', headers={'x-github-auth-token': "dummy"})
        mock_headers = self.get_github_mock_headers()
        mock_headers['Authorization'] = 'token dummy'
        mock_get.assert_called_with(self.get_github_url('mailchimp'), headers=mock_headers)
        self.assertEqual(401, response.status_code)
        mock_patcher.stop()

    def test_users_profile(self):
        mock_patcher = patch('app.utils.http_utils.requests.get')
        mock_get = mock_patcher.start()
        mock_get.side_effect = mocked_requests_get
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
        mock_patcher.stop()

    def get_github_url(self, repo):

        return f'{self.app.config.get("GITHUB_URL")}/orgs/{repo}/repos'

    def get_github_mock_headers(self):
        mock_headers = {}
        if self.app.config.get('GITHUB_TOKEN') != None and self.app.config.get('GITHUB_TOKEN') != "":
            mock_headers['Authorization'] = f'token {self.app.config.get("GITHUB_TOKEN")}'
        mock_headers['Accept'] = f'application/vnd.github.{self.app.config.get("GITHUB_VERSION")}+json'
        return mock_headers





def get_mock_data(file_name):
    with open(os.path.join(os.path.dirname(__file__), '../', file_name)) as d:
        return json.load(d)
