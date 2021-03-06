import os

import requests
from flask_restful import Resource

from util import flatten_list, count_items_in_list, AUTH


class GithubAPI(Resource):      # used to hit github stats endpoint
    def get(self, gh_user):
        """
        Given the github user pull all the github stats
        :param gh_user: github user
        :return: stats
        """

        result = {
            'data': get_github_stats(gh_user)
        }

        return result


def get_github_data(path):
    """
    Given path extract the endpoint data, provide the appropriate Accept return the request and the endpoint
    :param path: endpoint
    :return: result - request, endpoint
    """

    # parse out endpoint
    endpoint = path.split('/')[-1]     # no endpoint for the user profile

    # base github api url
    github_api = "https://api.github.com"

    # construct specific url
    url = os.path.join(github_api, path)

    # topics requires a different Accept
    if endpoint == 'topics':
        headers = {'Accept': 'application/vnd.github.mercy-preview+json'}
    else:
        headers = {'Accept': 'application/vnd.github.VERSION.full+json'}

    # request, authenticated
    r = requests.get(url, headers=headers, auth=AUTH)

    # result = request and given endpoint
    result = {
        'result': r,
        'endpoint': endpoint
    }

    return result


def get_github_pagination(link_str, endpoint):
    """
    Given the Link string from the requests header and the specific endpoint determine the user (id) and the total number of pages
    :param link_str: Link string from request header
    :param endpoint: endpoint
    :return: user (id), last page number
    """
    # parse the last page info from the Link header
    last_info = link_str.split(',')[1]

    # grab user id and last page - commits is different, hits repositories endpoint
    if endpoint != 'commits':
        user, last_page = last_info.split('user/')[1].split('/{}?'.format(endpoint))[0], last_info.split('?page=')[1].split('>')[0]
    else:
        user, last_page = last_info.split('repositories/')[1].split('/{}?'.format(endpoint))[0], last_info.split('?page=')[1].split('>')[0]

    return user, last_page


def page_thru_github_data_count(path):
    """
    Given a path/endpoint, page through all of the pages and depending on the specific endpoint return the count of all of the data
    :param path: commits or starred endpoint
    :return: counts
    """

    result = 0

    # get requested data
    requested_data = get_github_data(path)

    # continue if data grabbed without errors
    if requested_data['result'].status_code == 200:

        # Link in header if there is more than one page
        if 'Link' in requested_data['result'].headers.keys():

            # grab the Link string from header
            link_str = requested_data['result'].headers['Link']

            # grab user id and last page
            user, last_page = get_github_pagination(link_str, requested_data['endpoint'])

            # each page has 30(default) so quick assumptions - number of pages (minus the last one) can be multiplied by 30
            pages = int(last_page) - 1
            current_cnt = pages * 30  # 30 per page

            # grab the data from the last page - unknown count so add to assumed count
            if requested_data['endpoint'] == 'starred':  # starred endpoint
                url = 'user/{}/{}?page={}'.format(user, requested_data['endpoint'], last_page)
            else:  # commits endpoint
                url = 'repositories/{}/{}?page={}'.format(user, requested_data['endpoint'], last_page)

            # grab last page json data
            data = get_github_data(url)['result'].json()
            result = current_cnt + len(data)  # add assumed count plus the last page

        else:   # only one page
            result = len(requested_data['result'].json())

    return result


def page_thru_github_data_json(path):
    """
    Given a path, page through all of the pages and depending on the specific endpoint return all of the data as a flattened json
    :param path: repo (not commits or starred)
    :return: flattened json
    """

    all_data = []
    result = []

    # get requested data
    requested_data = get_github_data(path)

    # continue if data grabbed without errors
    if requested_data['result'].status_code == 200:

        # Link in header if there is more than one page
        if 'Link' in requested_data['result'].headers.keys():

            # grab the Link string from header
            link_str = requested_data['result'].headers['Link']

            # grab user id and last page
            user, last_page = get_github_pagination(link_str, requested_data['endpoint'])

            # page through each - needed for more details (repos)
            for page in range(1,int(last_page)+1):

                # construct url to ping
                url = 'user/{}/{}?page={}'.format(user, requested_data['endpoint'], page)

                # add to list
                all_data.append(get_github_data(url)['result'].json())

            # flatten the list with all the data (each page's data = list of dicts)
            result = flatten_list(all_data)

        else:

            # result as json data
            result = requested_data['result'].json()

    return result


def get_repo_info(repo):
    """
    Given a specific json repo grab all the necessary data
    :param repo: specific repo
    :return: cleaned up and wanted information json data
    """

    # turn forked info into non bool
    if repo['fork']:
        forked = "forked"
    else:
        forked = "original"

    # get language - if blank rename to be Not Specified
    if repo['language']:
        language = repo['language']
    else:
        language = 'Not Specified'

    result = {
        "full_name": repo['full_name'],
        "language": language,
        "pub_repo_type": forked,
        "forks_count": repo['forks_count'],
        "watchers_count": repo['watchers_count'],
        "open_issues_count": repo['open_issues_count'],
        "star_count": repo['stargazers_count'],
        "api_url": repo['url'],
        "url": repo['html_url'],
        "size": repo['size']
    }

    return result


def cleaned_repos_data(repos):
    """
    Given the list of uncleaned/full json repos, parse only wanted information per repo
    :param repos:
    :return: cleaned information list of json repos
    """

    # cleaned repos list
    repos_data = []

    # per each repo, clean up repo and save that
    for repo in repos:
        repos_data.append(get_repo_info(repo))

    return repos_data


def get_repo_summary(repos, item, action, repo_type=None):
    """
    Given a list of json repos takes in list of dicts and either sums up or counts
    :param repos: list of repos
    :param item: info of interest - watcher_count, starred_count, etc - key found in list of json
    :param action: count, sum or list
    :param repo_type: original or forked default is None meaning do this for both original and forked repos
    :return: either a list of counts, a sum or a list
    """
    # allowable action types
    action_types = ['count', 'sum', 'list']

    # say no if not one of the actions
    if action not in action_types:
        raise ValueError("Incorrect action! Must be one of the following: {}".format(action_types))

    # get a list of the items - ex: language, open_issues_count, etc
    info_item_list = []

    # per each repo (repo type specified) only get item/feature of interest -
    for repo in repos:
        if not repo_type:   # no repo type selected - get item info for all repo types (original and forked)
            info_item_list.append(repo[item])
        else:
            if repo['pub_repo_type'] == repo_type:      # gets the item info based on repo_type (original or forked)
                info_item_list.append(repo[item])

    # check if all items are ints
    if action == 'sum':
        if all(isinstance(i, int) for i in info_item_list):     # make sure all ints so we can add
            total = sum(info_item_list)

    # to get list - return list previously made
    elif action == 'list':
        total = info_item_list

    # to get list/counts
    elif action == 'count':

        # counter - get unique counts through info item list
        counter = count_items_in_list(info_item_list)
        total = counter

    else:
        raise ValueError("Unknown situation")

    return total


def get_github_stats(user):
    """
    Given a github user get the summary stats
    :param user: github user
    :return: summary stats json
    """
    # check user is valid
    user_data = get_github_data('users/{}/repos'.format(user))['result']

    if user_data.status_code != 200:
        result = {
            "message": user_data.json()['message']
        }

    else:
        # get repo data
        repos = page_thru_github_data_json('users/{}/repos'.format(user))
        all_repos = cleaned_repos_data(repos)

        # get stars given
        starred = page_thru_github_data_count('users/{}/starred'.format(user))

        # user profile
        profile_data = page_thru_github_data_json('users/{}'.format(user))

        # construct repo topics url
        get_list_of_topics = ['repos/{}/topics'.format(user_repo)
                              for user_repo in get_repo_summary(repos=all_repos, item='full_name', action='list')]

        # construct repo commits url
        get_list_of_repo_commits = ['repos/{}/commits'.format(user_repo)
                                    for user_repo in get_repo_summary(all_repos, item='full_name', action='list', repo_type='original')]

        # list of json data - topics
        repo_topics = []
        for repo_topic in get_list_of_topics:

            repo_topics.append(get_github_data(repo_topic)['result'].json()['names'])

        # list of json data - commits
        repo_commits = []
        for commits in get_list_of_repo_commits:
            repo_commits.append(page_thru_github_data_count(commits))

        # flatten repo topics
        flat_repo_topics = flatten_list(repo_topics)

        # count/list of topics
        list_count_repo_topics = count_items_in_list(flat_repo_topics)

        result = {
            # login
            "user": profile_data['login'],

            # total follower count
            "followers": profile_data['followers'],

            # total following count
            "following": profile_data['following'],

            # total number of stars given
            "total_stars_given": starred,

            # total number of stars received
            "total_stars_received": get_repo_summary(repos=all_repos, item='star_count', action='sum'),

            # list/count of repo topics
            "repo_topics": list_count_repo_topics,

            # list/count of languages used
            "languages": get_repo_summary(repos=all_repos, item='language', action='count'),

            # total number of public repos (original vs forked)
            "repos": get_repo_summary(repos=all_repos, item='pub_repo_type', action='count'),

            # total watchers count
            "total_watchers": get_repo_summary(repos=all_repos, item='watchers_count', action='sum'),

            # total number of open issues
            "total_open_issues":  get_repo_summary(repos=all_repos, item='open_issues_count', action='sum'),

            # total number of commits to their repos (not forks)
            "total_commits": sum(repo_commits),

            # total size of their accounts
            "total_account_size": get_repo_summary(repos=all_repos, item='size', action='sum')
        }

    return result



