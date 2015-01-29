from flask import Flask
from flask.ext import restful
from flask.ext.restful import reqparse

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
from elasticsearch_dsl.connections import connections

connections.create_connection()


app = Flask(__name__)
api = restful.Api(app)

parser = reqparse.RequestParser()
parser.add_argument('q', type=str, help='Query string is required!', location='args', required=True)

class SearchArchive(restful.Resource):
  def get(self):
    args = parser.parse_args()

    q = args["q"]

    s = Search(index="feed-item-archive") \
        .query("match", message=q)
    response = s.execute()

    hits = []

    for hit in response:
      hits.append(hit.to_dict())

    return hits

api.add_resource(SearchArchive, '/search')

if __name__ == '__main__':
  app.run(debug=True)
