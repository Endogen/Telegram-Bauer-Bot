import os
import sqlite3
import inspect
import logging
import threading
import bauer.constants as c

from pathlib import Path
from telegram import ChatAction
from bauer.config import ConfigManager


# TODO: Add option for command to only ...
# TODO: Merge with BauerPlugin?
# TODO: Remove 'Bauer' / 'bauer' everywhere and generalize things
class BauerPluginInterface:

    def __enter__(self):
        """ This method gets executed before the plugin gets loaded """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """ This method gets executed after the plugin gets loaded """
        pass

    # TODO: Rename this
    def get_action(self, bot, update, args):
        """ Logic that gets executed if command gets triggered """
        method = inspect.currentframe().f_code.co_name
        raise NotImplementedError(f"Interface method '{method}' not implemented")


class BauerPlugin(BauerPluginInterface):

    def __init__(self, tg_bot):
        super().__init__()
        self._tgb = tg_bot

        # Create access to plugin config file
        cfg_path = os.path.join(self.config_path(), f"{self.plugin_name()}.json")
        self._config = ConfigManager(cfg_path)

        # Save path to database file
        self._db_path = os.path.join(self.data_path(), f"{self.plugin_name()}.db")

    def usage(self):
        """ Show how to use the command """
        usage = self.get_resource("usage.md")
        return usage.replace("{plugin_name}", self.plugin_name())

    def handle(self):
        """ Command string that triggers the plugin """
        return self.cfg_get("handle")

    def plugins(self):
        return self._tgb.plugins

    def cfg_get(self, *keys, plugin=True):
        if plugin:
            keys = (self.plugin_name(),) + keys
            return self._config.get(*keys)
        return self._tgb.config.get(*keys)

    def cfg_set(self, value, *keys, plugin=True):
        if plugin:
            keys = (self.plugin_name(),) + keys
            self._config.set(value, *keys)
        else:
            self._tgb.config.set(value, *keys)

    def cfg_del(self, key):
        keys = [self.plugin_name(), key]
        self._config.remove(keys)

    def add_plugin(self, module_name):
        self._tgb.add_plugin(module_name)

    def remove_plugin(self, module_name):
        self._tgb.remove_plugin(module_name)

    def get_resource(self, filename, plugin=True):
        """ Return content of file """
        if plugin:
            path = os.path.join(self.resource_path(), filename)
        else:
            path = os.path.join(c.DIR_RES, filename)

        try:
            with open(path, "r", encoding="utf8") as f:
                return f.read()
        except Exception as e:
            logging.error(e)
            self.notify(e)
            return None

    def execute_sql(self, sql, *args, plugin=None):
        """ Execute raw SQL statement on database for given plugin """
        res = {"success": None, "data": None}

        # Check if database usage is enabled
        if not self.cfg_get("database", "use_db", plugin=False):
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
            self.notify(e)

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

        statement = self.get_resource("table_exists.sql", plugin=False)

        try:
            if cur.execute(statement, [table_name]).fetchone():
                exists = True
        except Exception as e:
            logging.error(e)
            self.notify(e)

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
        for plugin in self.plugins():
            if plugin.plugin_name() == plugin_name.lower():
                return True
        return False

    def notify(self, exception):
        if self.cfg_get("admin", "notify_on_error"):
            for admin in self.cfg_get("admin", "ids", plugin=False):
                self._tgb.updater.bot.send_message(
                    text=f"ERROR: {repr(exception)}",
                    chat_id=admin)
        return exception

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
            if update.effective_user.id in self.cfg_get("admin", "ids", plugin=False):
                return func(self, bot, update, **kwargs)
        return _only_owner
