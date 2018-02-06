from flask import Flask
from flask_restful import Api, Resource

from bitbucket_api import BitbucketAPI, get_bitbucket_stats
from github_api import GithubAPI, get_github_stats
from util import merge_git_accounts

app = Flask(__name__)
api = Api(app)


class MergedAPI(Resource):
    def get(self, gh_user, bb_user):

        gh_data = get_github_stats(gh_user)
        bb_data = get_bitbucket_stats(bb_user)

        result = merge_git_accounts(gh_data, bb_data)

        return result

# route to get just github stats
api.add_resource(GithubAPI, '/stats/github/<gh_user>')

# route to get just bitbucket stats
api.add_resource(BitbucketAPI, '/stats/bitbucket/<bb_user>')

# route to get both stats
api.add_resource(MergedAPI, '/stats/github/<gh_user>/bitbucket/<bb_user>',
                 '/stats/github/<string:gh_user>/bitbucket/<string:bb_user>')


# run it
if __name__ == "__main__":
    app.run(port=5002)
