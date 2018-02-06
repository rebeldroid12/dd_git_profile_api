import requests
import os

from flask_restful import Resource


class BitbucketAPI(Resource):
    def get(self, user):
        result = {
            'data': get_bitbucket_stats(user)
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


def flatten_list(nested_list):
    """

    :param nested_list:
    :return:
    """
    flat_last = []
    # flatten the list with all the data (each page's data = list of dicts)
    for json_list in nested_list:
        for json_obj in json_list:
            flat_last.append(json_obj)

    return flat_last


def count_in_list_of_json(list_of_json, item=None):
    """

    :return:
    """

    # counter
    counter = {}

    # check list_of_json
    if list_of_json:
        # get unique counts thru info item list
        for json_obj in list_of_json:
            if item:
                if json_obj[item] not in counter:
                    counter[json_obj[item]] = 1
                else:
                    counter[json_obj[item]] += 1
            else:
                if json_obj not in counter:
                    counter[json_obj] = 1
                else:
                    counter[json_obj] += 1

    return counter


def get_specific_count_to_sum(list_of_json, key_of_interest):
    """
    From a counter (list of json that has been counted), extract a specific count and sum
    :param list_of_json:
    :param key_of_interest:
    :return:
    """
    to_sum = []
    for json_obj in list_of_json:
        if key_of_interest in json_obj.keys():
            to_sum.append(json_obj[key_of_interest])

    return sum(to_sum)


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
            issues.append(count_in_list_of_json(all_issues, 'state'))

    result = {

        #login
        "user" : data['username'],

        # total follower count
        "followers": get_bitbucket_data(user_data_links['followers']['href'])['result']['size'],

        # total following count
        "following": get_bitbucket_data(user_data_links['following']['href'])['result']['size'],

        # total number of stars given
        "total_stars_given": 0,  # NA

        # total number of stars received
        "total_stars_received": 0,  # NA

        # list/count of repo topics

        # list/count of languages used
        "languages": count_in_list_of_json(language),

        # total number of public repos (original vs forked)
        "repos": count_in_list_of_json(repo_types),      # get_bitbucket_data(user_data_links['repositories']['href'])['result']['size'],  #TODO check orig vs forked

        # total watcher count
        "total_watchers": sum(watchers),

        # total number of open issues
        "total_open_issues": get_specific_count_to_sum(issues, 'new'),

        # total number of commits to their repos (not forks)
        "total_commits": len(commits),  # TODO only repos not forks

        # total size of their account
        "total_account_size": sum(size)

    }

    return result
