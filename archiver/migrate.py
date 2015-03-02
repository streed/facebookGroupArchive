import json
import sys

from facepy import GraphAPI
import rethinkdb as r

from util.group import convert_data

if __name__ == "__main__":
  r.connect("localhost", 28015).repl()
  try:
    r.db_create("facebookindex").run()
  except Exception as e:
    print e
    print "Database `facebookindex` already exists"

  try:
    r.db('facebookindex').table_create("feed").run()
  except Exception as e:
    print e
    print "Table `feed` already exists"

  group_id = sys.argv[1]
  access_token = sys.argv[2]

  graph = GraphAPI(access_token)
  pages = graph.get("%s/feed" % group_id, page=True, retry=3, limit=10000)

  i = 1
  bulk = []
  for page in pages:
    print "Page %d" % i
    for data in page["data"]:
      new_data = convert_data(data)
      bulk.append(new_data)

      if len(bulk) > 100:
        r.db("facebookindex").table("feed").insert(bulk).run()
        bulk = []
    i = i + 1
  r.db("facebookindex").table("feed").insert(bulk).run()
