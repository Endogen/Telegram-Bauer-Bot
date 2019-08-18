from telegram import ParseMode
from bauer.plugin import BauerPlugin


class Start(BauerPlugin):

    START_FILE = "start.md"

    def get_handle(self):
        return "start"

    @BauerPlugin.threaded
    def get_action(self, bot, update, args):
        update.message.reply_text(
            text=self.get_res(self.START_FILE),
            parse_mode=ParseMode.MARKDOWN)
