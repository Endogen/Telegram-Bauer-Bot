import os
import logging
import importlib
import threading
import bauer.emoji as emo
import bauer.constants as con

from importlib import reload
from bauer.config import ConfigManager as Cfg
from telegram import ParseMode
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
from telegram.error import InvalidToken


def threaded(fn):
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=fn, args=args, kwargs=kwargs)
        thread.start()
        return thread

    return wrapper


class TelegramBot:

    plugins = list()
    bismuth = None

    def __init__(self, bot_token, bot_db):
        self.token = bot_token
        self.db = bot_db

        read_timeout = Cfg.get("telegram", "read_timeout")
        connect_timeout = Cfg.get("telegram", "connect_timeout")

        kwargs = dict()
        if read_timeout:
            kwargs["read_timeout"] = read_timeout
        if connect_timeout:
            kwargs["connect_timeout"] = connect_timeout

        try:
            self.updater = Updater(bot_token, request_kwargs=kwargs)
        except InvalidToken as e:
            cls_name = f"Class: {type(self).__name__}"
            logging.error(f"{repr(e)} - {cls_name}")
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

    # Start the bot --> polling
    def bot_start_polling(self):
        self.updater.start_polling(clean=True)

    # Start the bot --> webhook
    def bot_start_webhook(self):
        self.updater.start_webhook(
            listen=Cfg.get("webhook", "listen"),
            port=Cfg.get("webhook", "port"),
            url_path=self.token,
            key=Cfg.get("webhook", "privkey_path"),
            cert=Cfg.get("webhook", "cert_path"),
            webhook_url=f"{Cfg.get('webhook', 'url')}:"
                        f"{Cfg.get('webhook', 'port')}/"
                        f"{self.token}")

    # Go in idle mode
    def bot_idle(self):
        self.updater.idle()

    def _load_plugins(self):
        """ Load all plugins in the 'plugins' folder """
        threads = list()

        for _, _, files in os.walk(os.path.join(con.SRC_DIR, con.PLG_DIR)):
            for file in files:
                if not file.lower().endswith(".py"):
                    continue
                if file.startswith("_"):
                    continue

                threads.append(self._load_plugin(file))

        # Make sure that all plugins are loaded
        for thread in threads:
            thread.join()

        for plugin in self.plugins:
            plugin.after_plugins_loaded()

    @threaded
    def _load_plugin(self, file):
        """ Load a single plugin """
        try:
            module_name = file[:-3]
            module_path = f"{con.SRC_DIR}.{con.PLG_DIR}.{module_name}"
            module = importlib.import_module(module_path)

            with getattr(module, module_name.capitalize())(self) as plugin:
                self._add_handler(plugin)
                self.plugins.append(plugin)
                logging.info(f"Plugin '{type(plugin).__name__}' added")
        except Exception as ex:
            msg = f"File '{file}' can't be loaded as a plugin: {ex}"
            logging.warning(msg)

    def _add_handler(self, plugin):
        """ Add CommandHandler for given plugin """
        self.dispatcher.add_handler(
            CommandHandler(
                plugin.get_handle(),
                plugin.get_action,
                pass_args=True))

    def add_plugin(self, module_name):
        for plugin in self.plugins:
            if type(plugin).__name__.lower() == module_name.lower():
                return {"success": False, "msg": "Plugin already active"}

        try:
            module_path = f"{con.SRC_DIR}.{con.PLG_DIR}.{module_name}"
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

    def _download(self, bot, update):
        if update.effective_user.id not in Cfg.get("admin_id"):
            return

        name = update.message.effective_attachment.file_name
        file = bot.getFile(update.message.document.file_id)
        file.download(os.path.join(con.SRC_DIR, con.PLG_DIR, name))

        class_name = name.replace(".py", "")

        try:
            self.remove_plugin(class_name)
            self.add_plugin(class_name)
            update.message.reply_text(f"{emo.CHECK} Plugin loaded successfully")
        except Exception as ex:
            update.message.reply_text(f"{emo.ERROR} {ex}")

    # Handle all telegram and telegram.ext related errors
    def _handle_tg_errors(self, bot, update, error):
        cls_name = f"Class: {type(self).__name__}"
        logging.error(f"{error} - {cls_name} - {update}")

        if not update:
            return

        error_msg = f"{emo.ERROR} Telegram ERROR: {error}"

        if update.message:
            update.message.reply_text(
                text=error_msg,
                parse_mode=ParseMode.MARKDOWN)
        elif update.callback_query:
            update.callback_query.message.reply_text(
                text=error_msg,
                parse_mode=ParseMode.MARKDOWN)