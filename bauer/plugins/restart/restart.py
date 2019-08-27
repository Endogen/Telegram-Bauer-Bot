import os
import sys
import time
import logging
import bauer.emoji as emo

from bauer.plugin import BauerPlugin


class Restart(BauerPlugin):

    def __enter__(self):
        message = self.cfg_get("message")
        user_id = self.cfg_get("user_id")

        # If no data saved, don't do anything
        if not message or not user_id:
            return self

        try:
            self._tgb.updater.bot.edit_message_text(
                chat_id=user_id,
                message_id=message,
                text=f"{emo.DONE} Restarting bot...")
        except Exception as e:
            logging.error(str(e))
        finally:
            self.cfg_del("message")
            self.cfg_del("user_id")

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

        self.cfg_set(user_id, "user_id")
        self.cfg_set(m.message_id, "message")

        m_name = __spec__.name
        m_name = m_name[:m_name.index(".")]

        time.sleep(1)
        os.execl(sys.executable, sys.executable, '-m', m_name, *sys.argv[1:])
