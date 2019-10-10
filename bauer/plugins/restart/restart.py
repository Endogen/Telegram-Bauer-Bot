import os
import sys
import time
import logging
import bauer.emoji as emo

from bauer.plugin import BauerPlugin


# TODO: Remove access to protected variable
class Restart(BauerPlugin):

    def __enter__(self):
        chat_id = self.config.get("chat_id")
        mess_id = self.config.get("message_id")

        # If no data saved, don't do anything
        if not mess_id or not chat_id:
            return self

        try:
            self._tgb.updater.bot.edit_message_text(
                chat_id=chat_id,
                message_id=mess_id,
                text=f"{emo.DONE} Restarting bot...")
        except Exception as e:
            logging.error(str(e))
        finally:
            self.config.remove("chat_id")
            self.config.remove("message_id")

        return self

    @BauerPlugin.owner
    @BauerPlugin.threaded
    @BauerPlugin.send_typing
    def execute(self, bot, update, args):
        msg = f"{emo.WAIT} Restarting bot..."
        message = update.message.reply_text(msg)

        chat_id = message.chat_id
        mess_id = message.message_id

        self.config.set(chat_id, "chat_id")
        self.config.set(mess_id, "message_id")

        m_name = __spec__.name
        m_name = m_name[:m_name.index(".")]

        time.sleep(1)
        os.execl(sys.executable, sys.executable, '-m', m_name, *sys.argv[1:])
