## Deploy own service in Heroku

- Deploy mongo instance
- [![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/aslepenkov/intube)
- config vars in heroku

```
MONGODB_URI=mongodb://<USER>:<PASS>@<ENDPOINT>:<PORT>
TELEGRAM_BOT_TOKEN = (provided by BotFather)
ADMIN_USER_ID = (your telegram id to get some debug messages)

STATS_COLLECTION = (name collection for vids stat)
USERS_COLLECTION = (name collection for users stat)
ERROR_COLLECTION = (name collection for errors logs)
MONGO_DB = (name of db)
```
