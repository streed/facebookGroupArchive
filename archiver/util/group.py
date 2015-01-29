import json
import sys

from dateutil import parser
from elasticsearch import Elasticsearch

from models.feed_item import FeedItem, FeedItemComment

def convert_data(raw_data):
  return FeedItem(created_time=parser.parse(raw_data["created_time"]),
      caption=raw_data.get("caption", ""),
      message=raw_data.get("message", ""),
      comments=convert_comments(raw_data.get("comments", {"data":[]})["data"]),
      upvote=0,
      downvote=0,
      approved=False,
      deleted=False,
      limbo=False)

def convert_comments(comments):
  return [FeedItemComment(created_time=parser.parse(c["created_time"]), message=c["message"]) for c in comments]

