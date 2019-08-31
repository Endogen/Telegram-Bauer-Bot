from telegram import ParseMode
from bauer.plugin import BauerPlugin


class About(BauerPlugin):

    INFO_FILE = "info.md"

    @BauerPlugin.threaded
    @BauerPlugin.send_typing
    def execute(self, bot, update, args):
        update.message.reply_text(
            text=self.get_resource(self.INFO_FILE),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True)
