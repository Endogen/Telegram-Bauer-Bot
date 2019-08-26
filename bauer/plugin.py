import os
import sqlite3
import inspect
import logging
import threading
import bauer.constants as c

from pathlib import Path
from telegram import ChatAction
from bauer.config import ConfigManager as Cfg


class BauerPluginInterface:

    def __enter__(self):
        """ This method gets executed before the plugin gets loaded """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """ This method gets executed after the plugin gets loaded """
        pass

    def get_handle(self):
        """ Command string that triggers the plugin """
        method = inspect.currentframe().f_code.co_name
        raise NotImplementedError(f"Interface method '{method}' not implemented")

    def get_action(self, bot, update, args):
        """ Logic that gets executed if command gets triggered """
        method = inspect.currentframe().f_code.co_name
        raise NotImplementedError(f"Interface method '{method}' not implemented")

    # TODO: Read .md file from plugins dir and show content
    def get_usage(self):
        """ Show how to use the command """
        return None

    def get_description(self):
        """ Short description what the command does """
        return None

    def get_category(self):
        """ Category for command """
        return None


class BauerPlugin(BauerPluginInterface):

    def __init__(self, tg_bot):
        super().__init__()
        self.tg_bot = tg_bot

        # Preparation for database creation
        cls_name = type(self).__name__.lower()
        self._db_path = os.path.join(self.data_path(), f"{cls_name}.db")

    def add_plugin(self, module_name):
        self.tg_bot.add_plugin(module_name)

    def remove_plugin(self, module_name):
        self.tg_bot.remove_plugin(module_name)

    def get_resource(self, filename, from_plugin=True):
        """ Return content of file """
        if from_plugin:
            path = os.path.join(self.resource_path(), filename)
        else:
            path = os.path.join(c.DIR_RES, filename)

        try:
            with open(path, "r", encoding="utf8") as f:
                return f.read()
        except Exception as e:
            logging.error(e)
            return None

    def execute_sql(self, sql, *args, plugin=None):
        """ Execute raw SQL statement on database for given plugin """
        res = {"success": None, "data": None}

        # Check if database usage is enabled
        if not Cfg.get("database", "use_db"):
            res["data"] = "Database disabled"
            res["success"] = False
            return res

        if plugin:
            plugin = plugin.lower()
            data_path = self.data_path(plugin=plugin)
            db_path = os.path.join(data_path, f"{plugin}.db")
        else:
            db_path = self._db_path

        # Create directory if it doesn't exist
        directory = os.path.dirname(self._db_path)
        os.makedirs(directory, exist_ok=True)

        con = None

        try:
            con = sqlite3.connect(db_path)
            cur = con.cursor()
            cur.execute(sql, args)
            con.commit()

            res["data"] = cur.fetchall()
            res["success"] = True
        except Exception as e:
            logging.error(e)
            res["data"] = str(e)
            res["success"] = False

        if con:
            con.close()

        return res

    def table_exists(self, table_name, plugin=None):
        """ Return TRUE if table exists, otherwise FALSE """
        if plugin:
            plugin = plugin.lower()
            db_name = f"{plugin}.db"
            db_path = os.path.join(self.data_path(plugin=plugin), db_name)
        else:
            db_path = self._db_path

        if not Path(db_path).is_file():
            return False

        con = sqlite3.connect(db_path)
        cur = con.cursor()
        exists = False

        statement = self.get_resource("table_exists.sql", from_plugin=False)

        try:
            if cur.execute(statement, [table_name]).fetchone():
                exists = True
        except Exception as e:
            logging.error(e)

        con.close()
        return exists

    def plugin_name(self):
        return type(self).__name__.lower()

    def resource_path(self, plugin=None):
        if not plugin:
            plugin = self.plugin_name()
        return os.path.join(c.DIR_SRC, c.DIR_PLG, plugin, c.DIR_RES)

    def config_path(self, plugin=None):
        if not plugin:
            plugin = self.plugin_name()
        return os.path.join(c.DIR_SRC, c.DIR_PLG, plugin, c.DIR_CFG)

    def data_path(self, plugin=None):
        if not plugin:
            plugin = self.plugin_name()
        return os.path.join(c.DIR_SRC, c.DIR_PLG, plugin, c.DIR_DAT)

    def plugin_path(self, plugin=None):
        if not plugin:
            plugin = self.plugin_name()
        return os.path.join(c.DIR_SRC, c.DIR_PLG, plugin)

    def plugin_available(self, plugin_name):
        plugin_found = False

        for plugin in self.tg_bot.plugins:
            plg_name = type(self).__name__.lower()
            if plg_name == plugin_name.lower():
                plugin_found = True

        return plugin_found

    @staticmethod
    def threaded(fn):
        def wrapper(*args, **kwargs):
            thread = threading.Thread(target=fn, args=args, kwargs=kwargs)
            thread.start()
            return thread
        return wrapper

    @classmethod
    def send_typing(cls, func):
        def _send_typing_action(self, bot, update, **kwargs):
            if update.message:
                user_id = update.message.chat_id
            elif update.callback_query:
                user_id = update.callback_query.message.chat_id
            else:
                return func(self, bot, update, **kwargs)

            try:
                bot.send_chat_action(
                    chat_id=user_id,
                    action=ChatAction.TYPING)
            except Exception as e:
                logging.error(f"{e} - {update}")

            return func(self, bot, update, **kwargs)
        return _send_typing_action

    @classmethod
    def only_owner(cls, func):
        def _only_owner(self, bot, update, **kwargs):
            if update.effective_user.id in Cfg.get("admin", "ids"):
                return func(self, bot, update, **kwargs)
        return _only_owner


# Categories for commands
class Category:
    # TODO: Don't hardcode categories
    AUTOGAME = "Autogame"
    BISMUTH = "Bismuth"
    DRAGGINATOR = "Dragginator"
    HYPERNODES = "Hypernodes"
    BOT = "Bot"

    @classmethod
    def get_categories(cls):
        categories = list()

        for k, v in vars(cls).items():
            if k.isupper() and isinstance(v, str):
                categories.append({k: v})

        return categories
