from telegram import ParseMode
from bauer.plugin import BauerPlugin


class Start(BauerPlugin):

    INFO_FILE = "info.md"

    @BauerPlugin.threaded
    def execute(self, bot, update, args):
        update.message.reply_text(
            text=self.get_resource(self.INFO_FILE),
            parse_mode=ParseMode.MARKDOWN)
