import unittest
import bitbucket_api
import github_api


class TestMyAPI(unittest.TestCase):

    # test all things bitbucket
    def test_BitbucketAPI(self):
        pass

    def test_get_bitbucket_data(self):
        pass

    def test_page_thru_bitbucket_data_json(self):
        pass

    def test_get_bitbucket_stats(self):
        pass

    # test all things github
    def test_GithubAPI(self):
        pass

    def test_get_github_data(self):
        pass

    def test_get_github_pagination(self):
        pass

    def test_page_thru_github_data_count(self):
        pass

    def test_page_thru_github_data_json(self):
        pass

    def test_get_repo_info(self):
        pass

    def test_cleaned_repos_data(self):
        pass

    def test_get_repo_summary(self):
        pass

    def test_get_github_stats(self):
        pass

    # test util functions
    def test_flatten_list(self):
        pass

    def test_count_items_in_list(self):
        pass

    def test_get_specific_count_to_sum(self):
        pass


if __name__ == '__main__':
    unittest.main()
