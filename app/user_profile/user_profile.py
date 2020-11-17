from ..utils.http_utils import *
from flask import current_app
import logging

LOG = logging.getLogger(current_app)

def get_user_profile_data(user, githubToken):
    """
    Get profile data from Github and Bitbucket for a given user/organization and returns merged profile data.
    """
    LOG.info("Getting bitbucket and github data for the user/owner: " + user)
    # Github user profile data
    github_profile_response = get_github_data(user, githubToken)
    # Bitbucket user profile data
    bitbucket_profile_response = get_bitbucket_data(user)
    profile_data = merge_profiles(github_profile_response, bitbucket_profile_response)
    LOG.debug("Successfully merged bitbucket and github data for the user/owner: " + user)
    return send_rest_response(200, profile_data)


def get_bitbucket_data(owner):
    """
    Get Bitbucket data for a given user/organization and returns data.
    """
    LOG.debug("Getting bitbucket data by user/owner: " + owner)
    res = get_response(f'{current_app.config["BITBUCKET_URL"]}/{current_app.config["BITBUCKET_VERSION"]}/repositories/' + owner, None, None)
    repos = res['values']
    formatted_res = {}
    repo_list = []
    total_watchers = 0
    total_forked = 0
    lang_map = {}
    for repo in repos:
        obj = {}
        obj['repo_name'] = repo['name']
        obj['repo_type'] = 'bitbucket'
        lang_list = []
        lang_list.append(repo['language'])
        obj['languages'] = lang_list
        lang_map[repo['language']] = lang_map.get(repo['language'], 0) + 1
        obj['topics'] = []
        watchers = get_response(repo["links"]['watchers']['href'], None, None)
        obj['watcher_count'] = watchers['size']
        total_watchers += obj['watcher_count']
        forks = get_response(repo["links"]["forks"]["href"], None, None)
        obj['forks_count'] = forks['size']
        total_forked += obj['forks_count']
        obj['language_count'] = 1
        repo_list.append(obj)
    formatted_res['repos'] = repo_list
    formatted_res['total_original_repos'] = len(repos)
    formatted_res['total_watchers_count'] = total_watchers
    formatted_res['total_forked_count'] = total_forked
    formatted_res['total_languages'] = lang_map
    formatted_res['total_topics'] = {}
    LOG.debug(f"Successfully retrieved bitbucket data, total repos: {len(repos)}")
    return formatted_res

def get_github_data(owner, token):
    """
    Get Github data for a given user/organization and returns data.
    """
    LOG.debug("Getting github data by user/owner: " + owner)
    custom_mimetype = f'application/vnd.github.{current_app.config["GITHUB_VERSION"]}+json'
    repos = get_response(f'{current_app.config["GITHUB_URL"]}/orgs/{owner}/repos', token, custom_mimetype )
    formatted_res = {}
    repo_list = []
    total_original_repos = 0
    total_watchers = 0
    total_forked = 0
    lang_map = {}
    topic_map = {}
    for repo in repos:
        if repo['fork'] == True:
            total_forked += 1
            continue

        total_original_repos += 1
        repo_obj = {}
        repo_obj['repo_name'] = repo['name']
        repo_obj['repo_type'] = 'github'
        repo_obj['watcher_count'] = repo['watchers']
        total_watchers += repo_obj['watcher_count']
        repo_obj['forks_count'] = repo['forks_count']
        total_forked += repo["forks_count"]
        languages = get_response(repo["languages_url"], token, custom_mimetype)
        lang_list = []
        for lang in languages.keys():
            lang_list.append(lang)
            lang_map[lang] = lang_map.get(lang, 0) + 1
        topic_url = f'{current_app.config["GITHUB_URL"]}/repos/{owner}/{repo["name"]}/topics'
        topic_mimetype = custom_mimetype + ', application/vnd.github.squirrel-girl-preview'
        topics = get_response(topic_url, token, topic_mimetype)
        topic_list = []
        if topics.get('names'):
            for topic_name in topics['names']:
                topic_list.append(topic_name)
                topic_map[topic_name] = topic_map.get(topic_name, 0) + 1
        repo_obj['topics'] = topic_list
        repo_obj['language_count'] = len(lang_list)
        repo_obj['languages'] = lang_list
        repo_list.append(repo_obj)
    formatted_res['repos'] = repo_list
    formatted_res['total_watchers_count'] = total_watchers
    formatted_res['total_forked_count'] = total_forked
    formatted_res['total_original_repos'] = total_original_repos
    formatted_res['total_languages'] = lang_map
    formatted_res['total_topics'] = topic_map
    LOG.debug(f"Successfully retrieved github data, total repos: {total_original_repos}")
    return formatted_res

def merge_profiles(githubProfile, bitbucketProfile):
    """
    Merges Github and Bitbucket profile data and returns merged data.
    """
    LOG.debug('Merging github and bitbucket profiles')
    #LOG.debug(f'Github profile data: {githubProfile}')
    #LOG.debug(f'Bitbucket profile data: {bitbucketProfile}')
    merged_response = githubProfile
    merged_response['total_original_repos'] += bitbucketProfile['total_original_repos']
    merged_response['total_forked_count'] += bitbucketProfile['total_forked_count']
    merged_response['total_watchers_count'] += bitbucketProfile['total_watchers_count']
    merged_response['total_languages'].update(bitbucketProfile['total_languages'])
    merged_response['total_topics'].update(bitbucketProfile['total_topics'])
    merged_response['repos'] += bitbucketProfile['repos']
    return merged_response