def flatten_list(nested_list):
    """
    Given a nested list flatten it
    :param nested_list: nested list
    :return: flattened list
    """
    flat_list = []

    # flatten the list with all the data (each page's data = list of dicts)
    for json_list in nested_list:
        for json_obj in json_list:
            flat_list.append(json_obj)

    return flat_list


def flatten_list_of_dicts(nested_list):
    """
    Flatten a list of dictionaries ex: [{k1:v1, k2:v2}, {k3:v3}]
    :param nested_list: nested list
    :return: list of [{k1:v1}, {k2:v2} {k1:v1}]
    """

    agg_dict_list = []

    for dict_obj in nested_list:
        for key, value in dict_obj.items():
            agg_dict_list.append({key:value})

    return agg_dict_list


def aggregate_list_of_dicts(list_of_dicts):
    """
    Given a list of single dictionaries: [{k1:v1}, {k2:v2} {k1:v1}] get unique counts/aggregate
    :param list_of_dicts: list of dicts
    :return: unique count/aggregate of list
    """

    agg = {}

    for dict_obj in list_of_dicts:
        for key, value in dict_obj.items():
            if key not in agg.keys():
                agg[key] = value
            else:
                agg[key] += value

    return agg


def count_items_in_list(list_of_json, item=None):
    """
    Given a list of json count the items in the list
    :param list_of_json: list of json
    :param item: give if looking for a particular item count in json
    :return: dictionary of list of items and counts
    """

    # counter
    counter = {}

    # check list_of_json
    if list_of_json:
        # get unique counts through list of json
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
    From a counted list of json, extract a specific count and sum it up in the list
    :param list_of_json: list of json - [{'new': 1, 'resolved':2, 'closed':3}, {'new':1}]
    :param key_of_interest: key -  ex: 'new'
    :return: count of key of interest - ex: 2
    """
    to_sum = []

    for json_obj in list_of_json:
        # if key found in json obj grab the value and append to list for later summation
        if key_of_interest in json_obj.keys():
            to_sum.append(json_obj[key_of_interest])

    return sum(to_sum)


def aggregate_git_accounts(github_data, bitbucket_data):
    """
    Merge/aggregate github_data and bitbucket_data
    :param github_data:
    :param bitbucket_data:
    :return:
    """
    gh_results = github_data
    bb_results = bitbucket_data

    result = {}

    # iter thru github result keys - github has all of the desired keys
    for key in gh_results.keys():
        # when key is not user
        if key not in ['user']:

            # check keys exist in both github and bitbucket
            if key in bb_results.keys():
                # check if value = int if so then easy add
                if type(gh_results[key]) == int:
                    result[key] = gh_results[key] + bb_results[key]

                else: # not int, dict - aggregate the counts
                    # make into list of dicts
                    non_int_agg_list = [gh_results[key]] + [bb_results[key]]
                    # flatten list of dicts
                    flattened_list = flatten_list_of_dicts(non_int_agg_list)
                    # aggregate list of dicts
                    result[key] = aggregate_list_of_dicts(flattened_list)
            else:
                result[key] = gh_results[key]

        else:  # key is user, provide explicit user info
            result[key] = {
                'github': gh_results[key],
                'bitbucket': bb_results[key]
            }

    return result