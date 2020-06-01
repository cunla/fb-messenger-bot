Messenger bot
=============
This messenger bot aims to store quotes in DB and send a new quote daily to
users who asked for it. A user can then like or dislike the quote he got.

# Technologies used
This software is created using:
* [fbmessenger](https://github.com/rehabstudio/fbmessenger)
for using facebook API.
* [flask](https://github.com/pallets/flask) for creating endpoints.
* [sqlalchemy](https://github.com/sqlalchemy/sqlalchemy) as ORM.

# Running instructions
You need to setup a facebook page and facebook app and get a token for it.
There are many guides how to setup a facebook page, [this](https://blog.hartleybrody.com/fb-messenger-bot/) is one good example.
After setting up a facebook page and getting the token, you can run this app.

In order to run the app, you need to set 3 environment variables:
* `FB_PAGE_TOKEN` - Your facebook page token
* `FB_VERIFY_TOKEN` - Your facebook verification
* `DATABASE_URL` - Your database where you store quotes, etc. defaults to sqlite.

Then run `python app.py` and you will get a live server.

## Endpoints in app
* `/webhook` - for facebook usage, using `FB_VERIFY_TOKEN` environment variable.
* `/get-users` - Get list of registered users in the bot database.
* `//send-quote/<user_id>` - If registered, the user will get a quote never seen before
  with quick-replies to like/dislike.

## Loading quotes to database
You can use the `load_quotes.py` program to load quotes from quotes.csv to your DB.
