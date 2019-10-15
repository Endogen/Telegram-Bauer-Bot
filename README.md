# Bauer Bot
Bauer is a Telegram bot for [Bismuth](https://bismuth.cz) (BIS) cryptocurrency.

## Overview
The bot is build around the [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) module and is polling based. [Webhook mode](https://github.com/python-telegram-bot/python-telegram-bot/wiki/Webhooks) is implemented but untested.

### General bot features
* Every command is a plugin
* Every plugin can be enabled / disabled without restarting the bot
* Every plugin can be updated by drag & dropping the implementation into the bot chat
* Restart or shutdown the bot via command
* Bot can be used with or without SQLite database
* Bot can be administered by more then one user

## Configuration
This part is only relevant if you want to host this bot yourself. If you just want to use the bot, [add the bot](https://t.me/bis_bauer_bot) *@bis_bauer_bot* to your Telegram contacts.

Before starting up the bot you have to take care of some settings and add a Telegram API token. The configuration file and toke file are located in the `config` folder.

### config.json
This file holds the configuration for the bot. You have to at least edit the value for __admin_id__. Everything else is optional.

- __admin - ids__: This is a list of Telegram user IDs that will be able to control the bot. You can add your own user or multiple users if you want. If you don't know your Telegram user ID, get in a conversation with Telegram bot [@userinfobot](https://t.me/userinfobot) and if you write him (anything) he will return you your user ID.
- __admin - notify_on_error__: If set to `true` then all user IDs in the "admin - ids" list will be notified if some error comes up.
- __telegram - read_timeout__: Read timeout in seconds as integer. Usually this value doesn't have to be changed.
- __telegram - connect_timeout__: Connect timeout in seconds as integer. Usually this value doesn't have to be changed.
- __webhook - listen__: Required only for webhook mode. IP to listen to.
- __webhook - port__: Required only for webhook mode. Port to listen on.
- __webhook - privkey_path__: Required only for webhook mode. Path to private key  (.pem file).
- __webhook - cert_path__: Required only for webhook mode. Path to certificate (.pem file).
- __webhook - url__: Required only for webhook mode. URL under which the bot is hosted.
- __database__ - __use_db__: If `true` then new database files (SQLite) will be created if a plugin tries to execute some SQL statements. If `false`, no databases will be used.

### token.json
This file holds the Telegram bot token. You have to provide one and you will get it in a conversation with Telegram bot [@BotFather](https://t.me/BotFather) while registering your bot.

If you don't want to provide the token in a file then you have two other options:
- Provide it as a command line argument: `-tkn <your token>`
- Provide it as an input on the command line (**MOST SECURE**): `--input-tkn`

## Starting
In order to run the bot you need to execute it with the Python interpreter. If you don't have any idea where to host the bot, take a look at [Where to host Telegram Bots](https://github.com/python-telegram-bot/python-telegram-bot/wiki/Where-to-host-Telegram-Bots). Services like [Heroku](https://www.heroku.com) (free) will work fine. You can also run the script locally on your own computer for testing purposes.

### Prerequisites
##### Python version
You have to use at least __Python 3.7__ to execute the scripts. Everything else is not supported.

##### Installing needed modules from `Pipfile`
Install all needed Python modules automatically with [Pipenv](https://pipenv.readthedocs.io). You have to be in the root folder of the bot - in the same directory as the `Pipfile`:

```shell
pipenv install
```

##### Installing needed modules from `requirements.txt`
This is an alternative way to install all needed Python modules. If you installed them already from the Pipfile then you can skip this section. If done this way, every installed module will be globally available to every other Python script you run.

1. Generate `requirements.txt` from `Pipfile`

```shell
pipenv lock -r
```

2. Install all needed Python modules

```shell
pip3 install -r requirements.txt
```

### Starting
1. First you have to make the script `run.sh` executable with

```shell
chmod +x run.sh
```

2. If you installed the needed Python modules via `Pipfile` you have to execute the following in the root folder of the bot:

```shell
pipenv run ./run.sh &
```

If you installed the modules globally:

```shell
./run.sh &
```

### Stopping
The recommended way to stop the bot is by using the bot command `/shutdown`. If you don't want or can't use this, you can shut the bot down with:

```shell
pkill python3.7
```

which will kill __every__ Python 3.7 process that is currently running.

## Usage

### Available commands
##### Bismuth
```
/accept - Accept terms and create BIS wallet
/address - Show your BIS wallet address
/balance - Show balance of your BIS wallet
/board - Show toplist for /rain and /tip
/deposit - Show qr-code for your BIS wallet
/giveaway - Give away BIS to random user
/rain - Randomly distribute BIS coins
/tip - Tip BIS coins to users
/withdraw - Withdraw BIS coins to a wallet
```

##### Bot
```
/about - Info about bot and creator
/admin - Control and maintain the bot
/backup - Backup whole bot folder
/feedback - Send us your feedback
/help - Show all available commands
/log - Download current logfile
/restart - Restart the bot
/shutdown - Shutdown the bot
```

If you want to show a list of available commands as you type, open a chat with Telegram bot [@BotFather](https://t.me/BotFather) and execute the command `/setcommands`. Then choose the bot you want to activate the list for and after that send the list of commands with description. Something like this:

```
about - Info about bot and its creator
address - Shows your wallet address
admin - Manage and controle the bot
backup - Backup whole bot or a plugin
balance - Shows your wallet balance
deposit - Shows qr-code for your address
feedback - <your feedback>
help - Show overview of available commands
logfile - Download current logfile
price - Show price on exchanges in BTC
rain - <total amount> <number of users>
restart - Restart the bot
shutdown - Shutdown the bot
tip - @<username> <amount>
board - tip | rain
accept - Accept terms and create wallet
withdraw - <address> <amount>
```

## Development
I am actively developing this bot and will do so also in the near future. If you would like to help out with development, send a message via Telegram to [@endogen](https://t.me/endogen). If you experience any issues open an issue here at GitHub.

### Plugins
If you decide to write your own plugin, check out the [Plugin Page](https://github.com/Endogen/Telegram-Bauer-Bot/tree/master/bauer/plugins) to read up on how to create a plugin and know about available plugins.

## Disclaimer
I use this bot personally and it should work fine but if not, I will NOT take any responsibility! Do NOT deposit huge amounts of coins into your bot wallet and be aware that the administrators that host the bot have access to the private key of any wallet that has been created with the bot.