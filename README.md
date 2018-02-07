# Git Profile API

## Challenge

Develop API that aggregates data from both Github and BitBucket API to present information in a unified response

## Display

- total number of public repos (orig vs forked repos)
- total watcher count
- total follower count
- total number of stars received
- total number of stars given
- total number of open issues
- total number of commits to their repos
- total size of their accounts
- list/count of languages used
- list/count of repo topics

## How to run
1. *OPTIONAL* Add GITHUB_USER and GITHUB_PASSWORD to your environment variables with your github credentials (works if not OAuth2) this is only for rate limiting
2. Clone repo: https://github.com/rebeldroid12/dd_git_profile_api/
3. Create a virtualenv and run `pip install -r requirements.txt`
4. Run `python app.py`
5. You'll be running on ['http://127.0.0.1:5002']('http://127.0.0.1:5002')


### To get summary stats on a specific Github & Bitbucket user:
`GET /stats/github/<github_user>/bitbucket/<bitbucket_user>`

ex: [http://127.0.0.1:5002/stats/github/rebeldroid12/bitbucket/rebeldroid12](http://127.0.0.1:5002/stats/github/rebeldroid12/bitbucket/rebeldroid12)
![Aggregated stats](https://github.com/rebeldroid12/dd_git_profile_api/blob/master/misc/merged.png)


### To get summary stats on a specific Github user:
`GET /stats/github/<github_user>`

ex: [http://127.0.0.1:5002/stats/github/rebeldroid12](http://127.0.0.1:5002/stats/github/rebeldroid12)
![Github stats only](https://github.com/rebeldroid12/dd_git_profile_api/blob/master/misc/github.png)


### To get summary stats on a specific Bitbucket user:
`GET /stats/bitbucket/<bitbucket_user>`

ex: [http://127.0.0.1:5002/stats/bitbucket/rebeldroid12](http://127.0.0.1:5002/stats/bitbucket/rebeldroid12)
![Bitbucket stats only](https://github.com/rebeldroid12/dd_git_profile_api/blob/master/misc/bitbucket.png)

### Error messages
If user cannot be found on Github but can be found on Bitbucket:
![No merge due to Github user](https://github.com/rebeldroid12/dd_git_profile_api/blob/master/misc/no_merge_on_github.png)

If user cannot be found on Bitbucket but can be found on Github:
![No merge due to Bitbucket user](https://github.com/rebeldroid12/dd_git_profile_api/blob/master/misc/no_merge_on_bitbucket.png)

If user cannot be found on either Github or Bitbucket:
![No merge due to both](https://github.com/rebeldroid12/dd_git_profile_api/blob/master/misc/no_merge_both.png)

If user cannot be found on Github:
![Bad github](https://github.com/rebeldroid12/dd_git_profile_api/blob/master/misc/bad_github.png)

If user cannot be found on Bitbucket:
![Bad bitbucket](https://github.com/rebeldroid12/dd_git_profile_api/blob/master/misc/bad_bitbucket.png)
