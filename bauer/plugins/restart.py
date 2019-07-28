import os
import sys
import time
import logging
import bauer.emoji as emo

from bauer.plugin import BauerPlugin
from bauer.config import ConfigManager as Cfg


class Restart(BauerPlugin):

    def __enter__(self):
        self._restart_notification()
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
        cls_name = type(self).__name__.lower()

        Cfg.set(user_id, "plugins", cls_name, "user_id")
        Cfg.set(m.message_id, "plugins", cls_name, "message")

        m_name = __spec__.name
        m_name = m_name[:m_name.index(".")]

        time.sleep(0.2)
        os.execl(sys.executable, sys.executable, '-m', m_name, *sys.argv[1:])

    # Inform about successful restart
    def _restart_notification(self):
        cls_name = type(self).__name__.lower()
        message = Cfg.get("plugins", cls_name, "message")
        user_id = Cfg.get("plugins", cls_name, "user_id")

        if not message or not user_id:
            return

        try:
            self.tgb.updater.bot.edit_message_text(
                chat_id=user_id,
                message_id=message,
                text=f"{emo.DONE} Restarting bot...")
        except Exception as e:
            msg = "Not possible to update restart message"
            logging.error(f"{msg}: {e}")

        Cfg.remove("plugins", cls_name)
