from elasticsearch_dsl import DocType, String, Date, Integer, Boolean

class FeedItemComment(DocType):
  created_time = Date()
  message = String(analyzer='snowball', fields={'raw': String(index='not_analyzed')})

class FeedItem(DocType):
  created_time = Date()
  message = String(analyzer='snowball', fields={'raw': String(index='not_analyzed')})
  caption = String(analyzer='snowball', fields={'raw': String(index='not_analyzed')})
  comments = FeedItemComment()
  upvote = Integer()
  downvote = Integer()
  approved = Boolean()
  deleted = Boolean()
  limbo = Boolean()

  class Meta:
    index = "feed-item-archive"

