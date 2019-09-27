import os
import sqlite3
import logging
import inspect
import threading
import bauer.constants as c

from pathlib import Path
from telegram import ChatAction
from bauer.config import ConfigManager


class BauerPlugin:

    def __init__(self, tg_bot):
        self._tgb = tg_bot
        self._job = None

        # Create access to global config
        self.global_config = self._tgb.config

        # Create access to plugin config
        cfg_path = os.path.join(self.get_cfg_path(), f"{self.get_name()}.json")
        self.config = ConfigManager(cfg_path)

    def __enter__(self):
        """ This method gets executed before the plugin gets loaded.
        Make sure to return 'self' if you override it """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """ This method gets executed after the plugin gets loaded """
        pass

    def execute(self, bot, update, args):
        """ Override this to be executed after command gets triggered """
        method = inspect.currentframe().f_code.co_name
        msg = f"Method '{method}' not implemented for plugin '{self.get_name()}'"
        logging.info(msg)

    def repeat(self, callback, interval, first=None):
        """ Logic that gets executed periodically """
        self._tgb.job_queue.run_repeating(callback, interval, first=first)

    def get_usage(self):
        """ Return how to use the command """
        usage = self.get_resource(f"{self.get_name()}.md")

        if usage:
            usage = usage.replace("{{handle}}", self.get_handle())
            return usage

        return None

    def get_handle(self):
        """ Return the command string that triggers the plugin """
        return self.config.get(self.get_name(), "handle")

    def get_category(self):
        """ Return the category of the plugin for the 'help' command """
        return self.config.get(self.get_name(), "category")

    def get_description(self):
        """ Return the description of the plugin """
        return self.config.get(self.get_name(), "description")

    def get_plugins(self):
        """ Return a list of all active plugins """
        return self._tgb.plugins

    def get_job(self):
        """ Return the periodic job or None if
        'interval' is not set in plugin config """
        return self._job

    def add_plugin(self, module_name):
        """ Enable a plugin """
        return self._tgb.add_plugin(module_name)

    def remove_plugin(self, module_name):
        """ Disable a plugin """
        return self._tgb.remove_plugin(module_name)

    def get_resource(self, filename, plugin=True):
        """ Return the content of the given file from
        the 'resource' directory of the plugin """

        if plugin:
            path = os.path.join(self.get_res_path(), filename)
        else:
            path = os.path.join(c.DIR_RES, filename)

        try:
            with open(path, "r", encoding="utf8") as f:
                return f.read()
        except Exception as e:
            logging.error(e)
            self.notify(e)
            return None

    def execute_sql(self, sql, *args, plugin="", db_name=""):
        """ Execute raw SQL statement on database for given
        plugin and return the result if there is one """

        res = {"success": None, "data": None}

        # Check if database usage is enabled
        if not self.global_config.get("database", "use_db"):
            res["data"] = "Database disabled"
            res["success"] = False
            return res

        if db_name:
            if not db_name.lower().endswith(".db"):
                db_name += ".db"
        else:
            if plugin:
                db_name = plugin + ".db"
            else:
                db_name = self.get_name() + ".db"

        if plugin:
            plugin = plugin.lower()
            data_path = self.get_dat_path(plugin=plugin)
            db_path = os.path.join(data_path, db_name)
        else:
            db_path = os.path.join(self.get_dat_path(), db_name)

        # Create directory if it doesn't exist
        directory = os.path.dirname(db_path)
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

    def table_exists(self, table_name, plugin="", db_name=""):
        """ Return TRUE if given table exists, otherwise FALSE """
        if db_name:
            if not db_name.lower().endswith(".db"):
                db_name += ".db"
        else:
            if plugin:
                db_name = plugin + ".db"
            else:
                db_name = self.get_name() + ".db"

        if plugin:
            db_path = os.path.join(self.get_dat_path(plugin=plugin), db_name)
        else:
            db_path = os.path.join(self.get_dat_path(), db_name)

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

    def get_name(self):
        """ Return the name of the current plugin """
        return type(self).__name__.lower()

    def get_res_path(self, plugin=""):
        """ Return path of resource directory for this plugin """
        if not plugin:
            plugin = self.get_name()
        return os.path.join(c.DIR_SRC, c.DIR_PLG, plugin, c.DIR_RES)

    def get_cfg_path(self, plugin=""):
        """ Return path of configuration directory for this plugin """
        if not plugin:
            plugin = self.get_name()
        return os.path.join(c.DIR_SRC, c.DIR_PLG, plugin, c.DIR_CFG)

    def get_dat_path(self, plugin=""):
        """ Return path of data directory for this plugin """
        if not plugin:
            plugin = self.get_name()
        return os.path.join(c.DIR_SRC, c.DIR_PLG, plugin, c.DIR_DAT)

    def get_plg_path(self, plugin=""):
        """ Return path of current plugin directory """
        if not plugin:
            plugin = self.get_name()
        return os.path.join(c.DIR_SRC, c.DIR_PLG, plugin)

    def plugin_available(self, plugin_name):
        """ Return TRUE if the given plugin is enabled or FALSE otherwise """
        for plugin in self.get_plugins():
            if plugin.get_name() == plugin_name.lower():
                return True
        return False

    def notify(self, some_input):
        """ All admins in global config will get a message with the given text.
         Primarily used for exceptions but can be used with other inputs too. """

        if self.global_config.get("admin", "notify_on_error"):
            for admin in self.global_config.get("admin", "ids"):
                self._tgb.updater.bot.send_message(
                    text=f"Notification:\n{some_input}",
                    chat_id=admin)
        return some_input

    @staticmethod
    def threaded(fn):
        """ Decorator for methods that have to run in their own thread """
        def wrapper(*args, **kwargs):
            thread = threading.Thread(target=fn, args=args, kwargs=kwargs)
            thread.start()
            return thread
        return wrapper

    @classmethod
    def send_typing(cls, func):
        """ Decorator for sending typing notification in the Telegram chat """
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
        """ Decorator that executes the method only of the user is an admin """
        def _only_owner(self, bot, update, **kwargs):
            user_id = update.effective_user.id

            admins_global = self.global_config.get("admin", "ids")
            if not admins_global or not isinstance(admins_global, list):
                return
            admins_local = self.global_config.get("admin", "ids")
            if not admins_local or not isinstance(admins_local, list):
                return

            if user_id in admins_global or user_id in admins_local:
                return func(self, bot, update, **kwargs)

        return _only_owner

    @classmethod
    def dependencies(cls, func):
        """ Decorator that executes a method only if the mentioned
        plugins in the config file of the current plugin are enabled """

        def _dependencies(self, bot, update, **kwargs):
            dependencies = self.plugin_config.get("dependency")
            if dependencies and isinstance(dependencies, list):
                plugins = [p.get_name() for p in self.get_plugins()]
                for dependency in dependencies:
                    if dependency.lower() not in plugins:
                        return
            return func(self, bot, update, **kwargs)
        return _dependencies
