import json
import sys
import rethinkdb as r

from dateutil import parser
from elasticsearch import Elasticsearch

def convert_data(raw_data):
  return dict(
      id=raw_data["id"],
      message=raw_data.get("message", ""),
      picture=raw_data.get("picture", ""),
      updated=parser.parse(raw_data["updated_time"]),
      created=parser.parse(raw_data["created_time"]),
      link=raw_data.get("link", ""),
      comments=convert_comments(raw_data.get("comments", {"data":[]})["data"]),
      upvote=0,
      downvote=0,
      approved=True,
      deleted=False,
      limbo=False
  )

def convert_comments(comments):
  return [dict(
    created=parser.parse(c["created_time"]), 
    message=c["message"],
    by=c["from"]["name"]
  ) for c in comments]

def clean_feed_item(item):
  if not item:
    return {}

  item["created"] = item["created"].isoformat()
  item["updated"] = item["updated"].isoformat()
  comments = []
  for c in item["comments"]:
    c["created"] = c["created"].isoformat()
    comments.append(c)
  item["comments"] = comments

  return item

def unclean_feed_item(item):
  if not item:
    return {}

  item["created"] = parser.parse(item["created"])
  item["updated"] = parser.parse(item["updated"])
  comments = []
  for c in item["comments"]:
    c["created"] = parser.parse(c["created"])
    comments.append(c)
  item["comments"] = comments

  return item

def validate_new(new, original):

  if new["id"] != original["id"]:
    return False

  if new["created"] != original["created"]:
    return False

  if new["updated"] != original["updated"]:
    return False

  if not new["approved"] and not (new["limbo"] or new["deleted"]):
    return False

  if new["limbo"] and new["deleted"]:
    return False

  if abs(new["upvote"] - original["upvote"]) > 1:
    return False

  if abs(new["downvote"] - original["downvote"]) > 1:
    return False

  return True

