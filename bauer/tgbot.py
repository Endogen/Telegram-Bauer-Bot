import os
import logging
import importlib
import bauer.emoji as emo
import bauer.constants as con

from importlib import reload
from bauer.config import ConfigManager
from telegram import ParseMode
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
from telegram.error import InvalidToken


class TelegramBot:

    plugins = list()

    def __init__(self, config: ConfigManager, token):
        self.config = config

        read_timeout = self.config.get("telegram", "read_timeout")
        connect_timeout = self.config.get("telegram", "connect_timeout")

        kwargs = dict()
        if read_timeout:
            kwargs["read_timeout"] = read_timeout
        if connect_timeout:
            kwargs["connect_timeout"] = connect_timeout

        try:
            self.updater = Updater(token, request_kwargs=kwargs)
        except InvalidToken as e:
            logging.error(e)
            exit("ERROR: Bot token not valid")

        self.job_queue = self.updater.job_queue
        self.dispatcher = self.updater.dispatcher

        # Load classes in folder 'plugins'
        self._load_plugins()

        # Handler for file downloads (plugin updates)
        mh = MessageHandler(Filters.document, self._download)
        self.dispatcher.add_handler(mh)

        # Handle all Telegram related errors
        self.dispatcher.add_error_handler(self._handle_tg_errors)

    def bot_start_polling(self):
        """ Start the bot in polling mode """
        self.updater.start_polling(clean=True)

    def bot_start_webhook(self):
        """ Start the bot in webhook mode """
        self.updater.start_webhook(
            listen=self.config.get("webhook", "listen"),
            port=self.config.get("webhook", "port"),
            url_path=self.updater.bot.token,
            key=self.config.get("webhook", "privkey_path"),
            cert=self.config.get("webhook", "cert_path"),
            webhook_url=f"{self.config.get('webhook', 'url')}:"
                        f"{self.config.get('webhook', 'port')}/"
                        f"{self.updater.bot.token}")

    # Go in idle mode
    def bot_idle(self):
        self.updater.idle()

    def add_plugin(self, module_name):
        """ Load a plugin so that it can be used """
        for plugin in self.plugins:
            if type(plugin).__name__.lower() == module_name.lower():
                return {"success": False, "msg": "Plugin already active"}

        try:
            module_path = f"{con.DIR_SRC}.{con.DIR_PLG}.{module_name}"
            module = importlib.import_module(module_path)

            reload(module)

            with getattr(module, module_name.capitalize())(self) as plugin:
                self._add_handler(plugin)
                self.plugins.append(plugin)
                logging.info(f"Plugin '{type(plugin).__name__}' added")
                return {"success": True, "msg": "Plugin added"}
        except Exception as ex:
            msg = f"Plugin '{module_name.capitalize()}' can't be added: {ex}"
            logging.warning(msg)
            raise ex

    def remove_plugin(self, module_name):
        """ Unload a plugin so that it can't be used """
        for plugin in self.plugins:
            if type(plugin).__name__.lower() == module_name.lower():
                try:
                    for handler in self.dispatcher.handlers[0]:
                        if isinstance(handler, CommandHandler):
                            if handler.command[0] == plugin.get_handle():
                                self.dispatcher.handlers[0].remove(handler)
                                break

                    self.plugins.remove(plugin)
                    logging.info(f"Plugin '{type(plugin).__name__}' removed")
                    break
                except Exception as ex:
                    msg = f"Plugin '{module_name.capitalize()}' can't be removed: {ex}"
                    logging.warning(msg)
                    raise ex
        return {"success": True, "msg": "Plugin removed"}

    def _load_plugins(self):
        """ Load all plugins from the 'plugins' folder """
        for _, folders, _ in os.walk(os.path.join(con.DIR_SRC, con.DIR_PLG)):
            for folder in folders:
                if folder.startswith("_"):
                    continue
                self._load_plugin(f"{folder}.py")
            break

    def _load_plugin(self, file):
        """ Load a single plugin """
        try:
            module_name, extension = os.path.splitext(file)
            module_path = f"{con.DIR_SRC}.{con.DIR_PLG}.{module_name}.{module_name}"
            module = importlib.import_module(module_path)

            with getattr(module, module_name.capitalize())(self) as plugin:
                self._add_handler(plugin)
                self.plugins.append(plugin)

                logging.info(f"Plugin '{type(plugin).__name__}' added")
        except Exception as e:
            logging.warning(f"File '{file}': {e}")

    def _add_handler(self, plugin):
        """ Add CommandHandler for given plugin """
        self.dispatcher.add_handler(
            CommandHandler(
                plugin.get_handle(),
                plugin.get_action,
                pass_args=True))

    def _download(self, bot, update):
        if update.effective_user.id not in self.config.get("admin", "ids"):
            return

        try:
            name = update.message.effective_attachment.file_name
            file = bot.getFile(update.message.document.file_id)
            file.download(os.path.join(con.DIR_SRC, con.DIR_PLG, name))

            class_name = name.replace(".py", "")

            self.remove_plugin(class_name)
            self.add_plugin(class_name)
            update.message.reply_text(f"{emo.DONE} Plugin loaded successfully")
        except Exception as e:
            logging.error(e)
            msg = f"{emo.ERROR} {e}"
            update.message.reply_text(msg)

    def _handle_tg_errors(self, bot, update, error):
        """ Handle errors for module 'telegram' and 'telegram.ext' """
        cls_name = f"Class: {type(self).__name__}"
        logging.error(f"{error} - {cls_name} - {update}")

        if not update:
            return

        error_msg = f"{emo.ERROR} *Telegram ERROR*: {error}"

        if update.message:
            update.message.reply_text(
                text=error_msg,
                parse_mode=ParseMode.MARKDOWN)
        elif update.callback_query:
            update.callback_query.message.reply_text(
                text=error_msg,
                parse_mode=ParseMode.MARKDOWN)
