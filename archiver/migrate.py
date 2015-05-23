import datetime
import json
import os
import sys
import time

from facepy import GraphAPI
from facepy.utils import get_application_access_token
import rethinkdb as r

from util.group import convert_data

if __name__ == "__main__":
  APPLICATION_ID = os.environ["FACEBOOK_APPLICATION_ID"]
  APPLICATION_SECRET = os.environ["FACEBOOK_APPLICATION_SECRET"]

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
  
  backfill = False
  if len(sys.argv) > 1:
    backfill = sys.argv[2] == "backfill"

  access_token = get_application_access_token(APPLICATION_ID, APPLICATION_SECRET)
  graph = GraphAPI(access_token)
  if backfill:
    print "BACKFILLING"
    pages = graph.get("%s/feed" % group_id, page=True, retry=3, limit=1)
  else:
    print "DOING ONLY PAST DAY"
    yesterday = datetime.datetime.now() - datetime.timedelta(days = 1)
    yesterday_beginning = datetime.datetime(yesterday.year, yesterday.month, yesterday.day,0,0,0,0)
    yesterday_beginning_time = int(time.mktime(yesterday_beginning.timetuple()))
    yesterday_end = datetime.datetime(yesterday.year, yesterday.month, yesterday.day,23,59,59,999)
    yesterday_end_time = int(time.mktime(yesterday_end.timetuple()))
    pages = graph.get("{}/feed?since={}&until={}".format(group_id, yesterday_beginning_time, yesterday_end_time), page=True, retry=3, limit=500, since=yesterday_beginning_time, until=yesterday_end_time)

  i = 1
  bulk = []
  for page in pages:
    print "Page %d" % i
    for data in page["data"]:
      new_data = convert_data(data)
      bulk.append(new_data)

      if len(bulk) > 500:
        r.db("facebookindex").table("feed").insert(bulk, conflict="update").run()
        bulk = []
    i = i + 1
  r.db("facebookindex").table("feed").insert(bulk, conflict="update").run()

