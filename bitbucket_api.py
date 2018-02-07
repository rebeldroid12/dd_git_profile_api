import os

import requests
from flask_restful import Resource

from util import flatten_list, count_items_in_list, get_specific_count_to_sum


class BitbucketAPI(Resource):       # used to hit bitbucket stats endpoint
    def get(self, bb_user):
        """
        Given the bitbucket user pull all the bitbucket stats
        :param bb_user: bitbucket user
        :return: stats
        """
        result = {
            'data': get_bitbucket_stats(bb_user)
        }

        return result


def get_bitbucket_data(path):
    """
    Given path extract the endpoint data, return json data
    :param path: endpoint
    :return: json data
    """

    # base bitbucket url
    bitbucket_api = "https://api.bitbucket.org/2.0/"

    # construct url
    if 'api.bitbucket.org' not in path:
        url = os.path.join(bitbucket_api, path)

    # go to url directly
    else:
        url = path

    # request
    r = requests.get(url)

    # check it's good to go if so return the json data
    if r.status_code == 200:
        result = {"result": r.json()}
    else:
        result = None

    return result


def page_thru_bitbucket_data_json(path):
    """
    Parse through all bitbucket data, grab all data from all pages
    :param path: endpoint
    :return: all data for given endpoint
    """

    # grab all the data
    all_data = []

    # first time call
    data = get_bitbucket_data(path)['result']

    # next only appears if there is a next page
    while 'next' in data.keys():
        all_data.append(data['values'])     # get just the values node (all data we care about is in there)
        data = get_bitbucket_data(data['next'])['result']   # get the data from the next page

    # grab data - in cases where there is no next ex: first item with no next, last time with no next
    all_data.append(data['values'])

    # flatten if necessary (list of lists of dicts) - in case where there was a next
    if len(all_data) > 1:
        r = flatten_list(all_data)

    else:
        r = all_data[0]

    result = {'result': r}

    return result


def get_bitbucket_stats(user):
    """
    Given a user (or team), grab all desired stats
    :param user: bitbucket user or team
    :return: aggregated bitbucket stats
    """

    # users endpoint
    user_data = get_bitbucket_data('users/{}'.format(user))

    # if you cannot get from users endpoint then teams
    if not user_data:
        user_data = get_bitbucket_data('teams/{}'.format(user))

    # could not get from users or teams
    if not user_data:
        # raise ValueError("Given user is not of type 'teams' or type 'user, please check again")

        result = {"message": "Given user is not of type 'teams' or type 'user, please check user is a valid bitbucket user."}

    else:
        # get results of data
        data = user_data['result']

        # links holds all the endpoints/links we will need to go through
        user_data_links = data['links']

        # go through all of the repos for the user
        parse_thru_repos = page_thru_bitbucket_data_json(user_data_links['repositories']['href'])['result']

        commits = []
        watchers = []
        size = []
        language = []
        issues = []
        repo_types = []

        for repo in parse_thru_repos:

            # differentiate between original & forked repos
            if 'parent' not in repo.keys():     # parent only appears in forked repos
                repo_type = 'original'

                # get commits per repo - only for original
                commits += get_bitbucket_data(repo['links']['commits']['href'])['result']['values']

            else:
                repo_type = 'forked'

            # add repo types to list - counted later
            repo_types.append(repo_type)

            # get sizes of repo - add repo size to list
            size.append(repo['size'])

            # get languages - add language to list
            if 'language' in repo.keys():
                if repo['language'] == '':
                    repo['language'] = 'Not Specified'

                language.append(repo['language'])

            # get watchers per repo - add watchers to list
            watchers.append(get_bitbucket_data(repo['links']['watchers']['href'])['result']['size'])

            # get all issues - if it has (not all repos have issues)
            if 'issues' in repo['links']:

                # hit issues endpoint
                issues_link = get_bitbucket_data(repo['links']['issues']['href'])

                # if data in issues endpoint then grab the values
                if issues_link:
                    all_issues = issues_link['result']['values']

                # create list/count of issues
                issues.append(count_items_in_list(all_issues, 'state'))

        # get followers info
        followers = get_bitbucket_data(user_data_links['followers']['href'])

        # get following info
        following = get_bitbucket_data(user_data_links['following']['href'])

        result = {

            # user/team
            "user": data['username'],

            # total follower count
            "followers": followers['result']['size'],

            # total following count
            "following": following['result']['size'],

            # total number of stars given - NA

            # total number of stars received - NA

            # list/count of repo topics - NA

            # list/count of languages used
            "languages": count_items_in_list(language),

            # total number of public repos (original vs forked)
            "repos": count_items_in_list(repo_types),

            # total number of open issues
            "total_open_issues": get_specific_count_to_sum(issues, 'new'),

            # total number of commits to their repos (not forks)
            "total_commits": len(commits),

            # total size of their account
            "total_account_size": sum(size)

        }

    return result
