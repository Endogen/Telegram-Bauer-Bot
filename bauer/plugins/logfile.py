import os
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

        # TODO: try & except and create variable
        update.message.reply_document(
            caption=f"{emo.CHECK} Current Logfile",
            document=open(os.path.join(base_dir, con.LOG_DIR, con.LOG_FILE), 'rb'))

    def get_usage(self):
        return f"`/{self.get_handle()}`"
