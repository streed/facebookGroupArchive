import json
import sys

from dateutil import parser
from elasticsearch import Elasticsearch

from models.feed_item import FeedItem, FeedItemComment

def convert_data(raw_data):
  return dict(
      message=raw_data.get("message", ""),
      picture=raw_data.get("picture", ""),
      updated=parser.parse(raw_data["updated_time"]),
      create=parser.parse(raw_data["created_time"]),
      link=raw_data.get("link", ""),
      comments=convert_comments(raw_data.get("comments", {"data":[]})["data"]),
      upvote=0,
      downvote=0,
      approved=False,
      deleted=False,
      limbo=False
  )

def convert_comments(comments):
  return [dict(
    created_time=parser.parse(c["created_time"]), 
    message=c["message"],
    posted_by=c["from"]["name"]
  ) for c in comments]

