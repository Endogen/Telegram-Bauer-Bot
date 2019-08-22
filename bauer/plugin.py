import os
import sqlite3
import inspect
import logging
import threading
import bauer.constants as c

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
        self._db_path = os.path.join(c.PLG_DIR, cls_name, f"{cls_name}.db")
        directory = os.path.dirname(self._db_path)
        os.makedirs(directory, exist_ok=True)

    def add_plugin(self, module_name):
        self.tg_bot.add_plugin(module_name)

    def remove_plugin(self, module_name):
        self.tg_bot.remove_plugin(module_name)

    # TODO: Rename to 'get_file_content'?
    # TODO: 'from_plugin' is unused
    def get_res(self, filename, from_plugin=True):
        """ Return content from file """
        try:
            resource_file = os.path.join(c.RES_DIR, filename)
            with open(resource_file, "r", encoding="utf8") as f:
                content = f.readlines()
        except Exception as e:
            logging.error(e)
            return None

        return "".join(content)

    def get_sql(self, filename, from_plugin=True):
        """ Return SQL statement from file """
        filename = f"{filename}.sql"

        if from_plugin:
            path = os.path.join(self.resource_path(), filename)
        else:
            path = os.path.join(c.RES_DIR, filename)

        try:
            with open(path) as f:
                return f.read()
        except Exception as e:
            logging.error(e)
            raise e

    def execute_sql(self, sql, *args, plugin=None):
        """ Execute raw SQL statement on database for given plugin """
        res = {"success": None, "data": None}

        # Check if database usage is enabled
        if not Cfg.get("database", "use_db"):
            res["data"] = "Database disabled"
            res["success"] = False
            return res

        # Check if table already exists
        if sql.lower().startswith("create table"):
            if self._table_exists(sql.split()[2]):
                res["data"] = "Table already present"
                res["success"] = True
                return res

        if plugin:
            plugin = plugin.lower()
            db_name = f"{plugin}.db"
            db_path = os.path.join(self.data_path(plugin=plugin), db_name)
        else:
            db_path = self._db_path

        con = sqlite3.connect(db_path)
        cur = con.cursor()

        try:
            cur.execute(sql, args)
            con.commit()
            res["data"] = cur.fetchall()
            res["success"] = True
        except Exception as e:
            logging.error(e)
            res["data"] = str(e)
            res["success"] = False

        con.close()
        return res

    def _table_exists(self, table_name, plugin=None):
        """ Return TRUE if table exists, otherwise FALSE """
        if plugin:
            plugin = plugin.lower()
            db_name = f"{plugin}.db"
            db_path = os.path.join(self.data_path(plugin=plugin), db_name)
        else:
            db_path = self._db_path

        con = sqlite3.connect(db_path)
        cur = con.cursor()
        exists = False

        try:
            statement = self.get_sql("table_exists", from_plugin=False)
            if cur.execute(statement, [table_name]).fetchone():
                exists = True
        except Exception as e:
            logging.error(e)

        con.close()
        return exists

    # TODO: Make private?
    def plugin_name(self):
        return type(self).__name__.lower()

    # TODO: Make private?
    # TODO: Do i need it?
    def resource_path(self, plugin=plugin_name()):
        return os.path.join(c.PLG_DIR, plugin, c.PLG_RES_DIR)

    def config_path(self, plugin=plugin_name()):
        return os.path.join(c.PLG_DIR, plugin, c.PLG_CFG_DIR)

    def data_path(self, plugin=plugin_name()):
        return os.path.join(c.PLG_DIR, plugin, c.PLG_DAT_DIR)

    def plugin_available(self, plugin_name):
        # TODO: Implement search in self.tg_bot.plugins and return TRUE / FALSE
        pass

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
            if update.effective_user.id in Cfg.get("admin_id"):
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
