import json
import os
import sys

from facepy import GraphAPI


def convert_data(raw_data):
  data = {}
  data["created"] = raw_data["created_time"]
  if "caption" in data:
    data["caption"] = raw_data["caption"]
  if "message" in raw_data:
    data["message"] = raw_data["message"]
  if "comments" in raw_data:
    data["comments"] = convert_comments(raw_data["comments"]["data"])
  
  return data

def convert_comments(comments):
  return [{"created": c["created_time"], "message": c["message"]} for c in comments]

if __name__ == "__main__":
  group_id = sys.argv[1]
  access_token = sys.argv[2]

  graph = GraphAPI(access_token)
  pages = graph.get("%s/feed" % group_id, page=True, retry=3, limit=1000)

  for page in pages:
    for data in page["data"]:
      new_data = convert_data(data)
      print json.dumps(new_data, indent=4, sort_keys=True)
