import inspect
import logging
import bauer.emoji as emo

from telegram import ChatAction
from bauer.config import ConfigManager as Cfg


class BauerPluginInterface:

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    # command string that triggers the plugin
    def get_handle(self):
        method = inspect.currentframe().f_code.co_name
        raise NotImplementedError(f"Interface method '{method}' not implemented")

    # Logic that gets executed if command is triggered
    def get_action(self, bot, update, args):
        method = inspect.currentframe().f_code.co_name
        raise NotImplementedError(f"Interface method '{method}' not implemented")

    # How to use the command
    def get_usage(self):
        return None

    # Short description what the command does
    def get_description(self):
        return None

    # Category for command
    def get_category(self):
        return None

    # Execute logic after all plugins are loaded
    def after_plugins_loaded(self):
        return None


# TODO: Make plugin run in its own thread?
class BauerPlugin(BauerPluginInterface):

    def __init__(self, telegram_bot):
        super().__init__()
        self.tgb = telegram_bot

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

    @classmethod
    def save_user(cls, func):
        def _save_user(self, bot, update, **kwargs):
            if Cfg.get("database", "use_db"):
                self.tgb.db.save_user(update.effective_user)
            return func(self, bot, update, **kwargs)
        return _save_user

    # Handle exceptions (write to log, reply to Telegram message)
    def handle_error(self, error, update, send_error=True):
        cls_name = f"Class: {type(self).__name__}"
        logging.error(f"{repr(error)} - {error} - {cls_name} - {update}")

        if send_error and update and update.message:
            msg = f"{emo.ERROR} {error}"
            update.message.reply_text(msg)

    # Bridge to database method
    # TODO: Do we really need this?
    def get_sql(self, filename):
        return self.tgb.db.get_sql(filename)

    # Build button-menu for Telegram
    def build_menu(cls, buttons, n_cols=1, header_buttons=None, footer_buttons=None):
        menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]

        if header_buttons:
            menu.insert(0, header_buttons)
        if footer_buttons:
            menu.append(footer_buttons)

        return menu


# Categories for commands
class Category:

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
