import json
import sys

from elasticsearch_dsl.connections import connections
from facepy import GraphAPI

from util.group import convert_data

if __name__ == "__main__":
  connections.create_connection()
  group_id = sys.argv[1]
  access_token = sys.argv[2]

  graph = GraphAPI(access_token)
  pages = graph.get("%s/feed" % group_id, page=True, retry=3, limit=10000)

  i = 1
  for page in pages:
    print "Page %d" % i
    for data in page["data"]:
      new_data = convert_data(data)
      new_data.save()
    i = i + 1
