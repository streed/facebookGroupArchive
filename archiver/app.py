from flask import Flask, render_template
from flask.ext import restful
from flask.ext.restful import reqparse

from elasticsearch import Elasticsearch

app = Flask(__name__)
api = restful.Api(app)

parser = reqparse.RequestParser()
parser.add_argument('q', type=str, help='Query string is required!', location='args', required=True)

client = Elasticsearch()

class SearchArchive(restful.Resource):
  def get(self):
    args = parser.parse_args()
    response = client.search(
      index='facebookindex',
      body={
        "query": {
          "term": {
            "message": args["q"]
          }
        }
      }
    )

    return [ hit["_source"] for hit in response["hits"]["hits"]]

@app.route("/")
def index():
  return render_template("index.html")

api.add_resource(SearchArchive, '/search')

if __name__ == '__main__':
  app.run(debug=True)
