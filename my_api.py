from flask import Flask
from flask_restful import Api

from bitbucket_api import  BitbucketAPI
from github_api import GithubAPI

app = Flask(__name__)
api = Api(app)

# route to get just github stats
api.add_resource(GithubAPI, '/github_stats/<user>')   # route1

# route to get just bitbucket stats
api.add_resource(BitbucketAPI, '/bitbucket_stats/<user>')   # route1


# run it
if __name__ == "__main__":
    app.run(port=5002)