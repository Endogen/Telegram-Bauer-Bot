import os
import sys
import time
import logging
import bauer.emoji as emo

from bauer.plugin import BauerPlugin
from bauer.config import ConfigManager as Cfg


# TODO: Save data in plugin json file
class Restart(BauerPlugin):

    def __enter__(self):
        self._restart_check()
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

        # TODO: Save in 'state' file in plugin dir?
        Cfg.set(user_id, "plugins", cls_name, "user_id")
        Cfg.set(m.message_id, "plugins", cls_name, "message")

        m_name = __spec__.name
        m_name = m_name[:m_name.index(".")]

        time.sleep(1)
        os.execl(sys.executable, sys.executable, '-m', m_name, *sys.argv[1:])

    def _restart_check(self):
        """ Inform about successful restart """
        cls_name = type(self).__name__.lower()
        message = Cfg.get("plugins", cls_name, "message")
        user_id = Cfg.get("plugins", cls_name, "user_id")

        if not message or not user_id:
            return

        try:
            self.tg_bot.updater.bot.edit_message_text(
                chat_id=user_id,
                message_id=message,
                text=f"{emo.DONE} Restarting bot...")
        except Exception as e:
            logging.error(str(e))
        finally:
            Cfg.remove("plugins", cls_name)
