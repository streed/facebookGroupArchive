facebookGroupArchive
====================

The following tool is a simple Flask application that displays a single page react app that will allow someone to list and display feed items from one or more facebook groups. These feed items are updated each day at midnight. 

The following is how the system works:

* The migration script is run at midnight with the FaceBook group id and the associated api key.
 * As the migration script is running it will index new feed items into a RethinkDB database.
 * At the same time running an Elasticsearch node as well the `river` plugin for RethinkDB will auto sync both databases.
  * [river](https://github.com/rethinkdb/elasticsearch-river-rethinkdb). In their QuickStart change the `blog` database to `facebookindex`

Once the feed items are in both databases they are searchable from the page and displayable. There is a simple voting system in place to allow for better sorting of posts in the search results. Higher upvoted items will be given more precedence over items with less votes or downvotes.

If a feed item reaches a certain threshold in terms of downvotes then the item will go into limbo. At this point it can be deleted, which effectively hides it from search results.
