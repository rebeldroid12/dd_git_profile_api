import requests
import os

from flask_restful import Resource

from util import flatten_list, count_items_in_list, get_specific_count_to_sum


class BitbucketAPI(Resource):
    def get(self, bb_user):
        result = {
            'data': get_bitbucket_stats(bb_user)
        }

        return result


def get_bitbucket_data(path):
    """
    Given path extract the endpoint, return data
    :param path:
    :return: result - request, endpoint
    """

    bitbucket_api = "https://api.bitbucket.org/2.0/"

    # construct url
    if 'api.bitbucket.org' not in path:
        url = os.path.join(bitbucket_api, path)

    # go to url directly
    else:
        url = path

    r = requests.get(url)

    if r.status_code == 200:
        result = {"result": r.json()}
    else:
        result = None

    return result


def page_thru_bitbucket_data_json(path):
    """
    Parse thru all bitbucket data
    :param path:
    :return:
    """

    all_data = []

    # first time call
    data = get_bitbucket_data(path)['result']

    # next only appears if there is a next page
    while 'next' in data.keys():
        all_data.append(data['values'])
        data = get_bitbucket_data(data['next'])['result']

    # grab data
    all_data.append(data['values'])

    # flatten if necessary (list of lists of dicts)
    if len(all_data) > 1:
        r = flatten_list(all_data)

    else:
        r = all_data[0]

    result = {'result': r}

    return result


def get_bitbucket_stats(user):
    """
    Get users info
    :param user:
    :return:
    """
    # users endpoint
    user_data = get_bitbucket_data('users/{}'.format(user))

    # if you cannot get from users endpoint then teams
    if not user_data:
        user_data = get_bitbucket_data('teams/{}'.format(user))

    # could not get from users or teams
    if not user_data:
        raise ValueError("Given user is not of type 'teams' or type 'user, please check again")

    # get results of data
    data = user_data['result']

    user_data_links = data['links']

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

        repo_types.append(repo_type)

        # get sizes of repo
        size.append(repo['size'])

        # get languages
        if 'language' in repo.keys():
            if repo['language'] == '':
                repo['language'] = 'Not Specified'

            language.append(repo['language'])

        # get watchers per repo
        watchers.append(get_bitbucket_data(repo['links']['watchers']['href'])['result']['size'])

        # get all issues - if it has
        if 'issues' in repo['links'] and get_bitbucket_data(repo['links']['issues']['href']):
            all_issues = get_bitbucket_data(repo['links']['issues']['href'])['result']['values']

            # create list/count of issues
            issues.append(count_items_in_list(all_issues, 'state'))

    result = {

        #login
        "user" : data['username'],

        # total follower count
        "followers": get_bitbucket_data(user_data_links['followers']['href'])['result']['size'],

        # total following count
        "following": get_bitbucket_data(user_data_links['following']['href'])['result']['size'],

        # # total number of stars given
        # "total_stars_given": 0,  # NA
        #
        # # total number of stars received
        # "total_stars_received": 0,  # NA

        # list/count of repo topics

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
