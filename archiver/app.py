from flask import Flask, render_template
from flask.ext import restful
from flask.ext.restful import reqparse

from elasticsearch import Elasticsearch
import rethinkdb as r

app = Flask(__name__)
api = restful.Api(app)

parser = reqparse.RequestParser()
parser.add_argument('q', type=str, help='Query string is required!', location='args', required=True)

client = Elasticsearch()
conn = r.connect(host='localhost', port=28015)
conn.use('facebookindex')

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

class FeedEndpoint(restful.Resource):
  def get(self, post_id):
    print r.table("feed").get(post_id).run(conn)

@app.route("/")
def index():
  return render_template("index.html")

@app.route("/post/<post_id>")
def post(post_id):
  return render_template("post.html", post_id=post_id)

api.add_resource(SearchArchive, '/search')
api.add_resource(FeedEndpoint, '/feed/<string:post_id>')

if __name__ == '__main__':
  app.run(debug=True)
