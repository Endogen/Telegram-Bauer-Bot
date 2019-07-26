import os
import logging
import bauer.emoji as emo
import bauer.constants as con

from bauer.plugin import BauerPlugin


class Logfile(BauerPlugin):

    def get_handle(self):
        return "logfile"

    @BauerPlugin.only_owner
    @BauerPlugin.send_typing
    def get_action(self, bot, update, args):
        base_dir = os.path.abspath('./')
        log_file = os.path.join(base_dir, con.LOG_DIR, con.LOG_FILE)

        if os.path.isfile(log_file):
            try:
                file = open(log_file, 'rb')
            except Exception as e:
                logging.error(e)
                file = None
        else:
            file = None

        if file:
            update.message.reply_document(
                caption=f"{emo.DONE} Current Logfile",
                document=file)
        else:
            update.message.reply_text(
                text=f"{emo.ERROR} Not possible to download logfile")
