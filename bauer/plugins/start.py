import os
import logging
import bauer.constants as con
import bauer.emoji as emo

from telegram import ParseMode
from bauer.plugin import BauerPlugin


class Start(BauerPlugin):

    START_FILENAME = "start.md"

    def get_handle(self):
        return "start"

    @BauerPlugin.threaded
    def get_action(self, bot, update, args):
        about_file = os.path.join(con.RES_DIR, self.START_FILENAME)

        try:
            with open(about_file, "r", encoding="utf8") as file:
                content = file.readlines()
        except Exception as e:
            logging.error(e)
            content = f"{emo.ERROR} Can't display `{self.START_FILENAME}`"

        update.message.reply_text(
            text="".join(content),
            parse_mode=ParseMode.MARKDOWN)
