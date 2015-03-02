import os
import rethinkdb as r

from flask import Flask, render_template
from flask.ext import restful
from flask.ext.restful import reqparse
from flask.json import JSONEncoder
from flask_rethinkdb import RethinkDB

from elasticsearch import Elasticsearch

app = Flask(__name__)
app.json_encoder = JSONEncoder()

app.config["RETHINKDB_DB"] = "facebookindex"

api = restful.Api(app)
db = RethinkDB()
db.init_app(app)

parser = reqparse.RequestParser()
parser.add_argument('q', type=str, help='Query string is required!', location='args', required=True)
parser.add_argument('offset', type=int, help='Offset into the collection.', location='args', required=False)
parser.add_argument('limit', type=int, help='Limit into the collection.', location='args', required=False)

client = Elasticsearch()

BOOSTING_FACTOR = 1.35

class SearchArchive(restful.Resource):
  def get(self):
    args = parser.parse_args()
    offset = args["offset"] or 0
    limit = args["limit"] or 10
    
    response = client.search(
      index='facebookindex',
      body={
        "from": offset,
        "size": limit,
        "query": {
          "function_score": {
            "query": {
              "filtered": {
                "query": {
                  "term": {
                    "message": args["q"]
                    }
                },
                "filter": {
                  "bool": {
                    "must": [
                      {"term": {"approved": True}},
                      {"term": {"limbo": False}},
                      {"term": {"deleted": False}}
                    ]
                  }
                }
              }
            },
            "script_score": {
              "params": {
                "boosting_factor": BOOSTING_FACTOR
              },
              "script": """
                upvotes = doc['upvote'].value * boosting_factor;
                downvotes = doc['downvote'].value;

                if (upvotes == 0 && downvotes == 0) {
                  return 1;
                } 

                if (downvotes == 0) {
                  return upvotes;
                }

                if (upvotes == 0) {
                  return downvotes;
                }
                
                return upvotes / downvotes;
              """
            }
          }
        }
      }
    )

    return [hit["_source"] for hit in response["hits"]["hits"]]

def clean_feed_item(item):
  item["create"] = item["create"].isoformat()
  item["updated"] = item["updated"].isoformat()
  comments = []
  for c in item["comments"]:
    c["created_time"] = c["created_time"].isoformat()
    comments.append(c)
  item["comments"] = comments

  return item

class FeedEndpoint(restful.Resource):
  def get(self, post_id):
    return clean_feed_item(r.table("feed").get(post_id).run(db.conn))

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
