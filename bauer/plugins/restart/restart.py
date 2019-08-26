import os
import sys
import time
import logging
import bauer.emoji as emo

from bauer.plugin import BauerPlugin
from bauer.config import ConfigManager as Cfg


class Restart(BauerPlugin):

    def __enter__(self):
        # Read message and user_id from config file
        cfg_path = os.path.join(self.config_path(), f"{self.plugin_name()}.db")

        cfg = Cfg(cfg_path)
        message = cfg.get("message")
        user_id = cfg.get("user_id")

        # If no data saved, don't so anything
        if not message or not user_id:
            return self

        try:
            self.tg_bot.updater.bot.edit_message_text(
                chat_id=user_id,
                message_id=message,
                text=f"{emo.DONE} Restarting bot...")
        except Exception as e:
            logging.error(str(e))
        finally:
            cfg.remove("message")
            cfg.remove("user_id")

        return self

    def get_handle(self):
        return "restart"

    @BauerPlugin.threaded
    @BauerPlugin.only_owner
    @BauerPlugin.send_typing
    def get_action(self, bot, update, args):
        msg = f"{emo.WAIT} Restarting bot..."
        m = update.message.reply_text(msg)

        user_id = update.effective_user.id

        # TODO: How to have that as a class variable?
        cfg_path = os.path.join(self.config_path(), f"{self.plugin_name()}.db")

        # TODO: Folder will not be created automatically
        cfg = Cfg(cfg_path)
        cfg.set(user_id, "user_id")
        cfg.set(m.message_id, "message")

        m_name = __spec__.name
        m_name = m_name[:m_name.index(".")]

        time.sleep(1)
        os.execl(sys.executable, sys.executable, '-m', m_name, *sys.argv[1:])
