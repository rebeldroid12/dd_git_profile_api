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

## Considerations
- how to handle failed network call to github/bitbucket (what to return to client)
- which REST verbs and URI structure makes the most sense
- how efficient is your code?

## Rules of Engagement
- python 3.6 & Flask
- documentation
- readme
- unit tests